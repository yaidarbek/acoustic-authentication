import Foundation
import AVFoundation
import Combine

/// Authentication state machine
enum AuthState {
    case idle
    case listeningReady      // Listening for READY tone from laptop
    case sendingAck          // Sending ACK tone to laptop
    case listening           // Listening for challenge
    case decoding
    case computing
    case transmitting
    case listeningConfirmation  // Listening for ACK/NACK from laptop
    case authenticated
    case failed(String)
}

/// Orchestrates the full challenge-response protocol on the iPhone (prover) side
/// Mirrors: acoustic_auth.py AcousticAuthenticator (prover role only)
///
/// Flow:
///   1. Listen for FSK-encoded challenge from laptop
///   2. Decode challenge using Goertzel algorithm
///   3. Compute HMAC-SHA256 response using shared secret
///   4. Transmit response back to laptop via FSK audio
class AcousticAuthenticator: ObservableObject {

    // MARK: - Published State (drives SwiftUI)
    @Published var state: AuthState = .idle
    @Published var logMessages: [String] = []

    // MARK: - Components
    private let fskDecoder: FSKDecoder
    private let cryptoEngine: CryptoEngine
    private let recordingEngine = AVAudioEngine()
    private let playbackEngine = AVAudioEngine()
    private var recordedSamples: [Float] = []

    // MARK: - Config
    private let challengeSizeBytes = 16   // 128-bit challenge
    private let responseSizeBytes  = 32   // 256-bit HMAC-SHA256 response
    
    // Handshaking tones
    private let readyToneFreq: Double = 12000.0   // 12 kHz - READY from laptop
    private let ackToneFreq: Double = 14000.0     // 14 kHz - ACK to laptop
    private let nackToneFreq: Double = 6000.0     // 6 kHz - NACK from laptop
    private let toneDuration: Double = 0.5        // 0.5 seconds
    private let successToneDuration: Double = 1.0 // 1 second for final ACK/NACK

    // MARK: - Init

    /// Initialise with shared secret key
    /// In production: load from iOS Keychain using SecItemCopyMatching
    init(sharedKeyHex: String) {
        self.fskDecoder  = FSKDecoder()
        self.cryptoEngine = CryptoEngine(hexKey: sharedKeyHex)
    }

    // MARK: - Public API

    /// Start the full authentication cycle
    /// Called when user taps "Authenticate" in ContentView
    func startAuthentication() {
        logMessages.removeAll()
        log("🚀 Button tapped - starting...")
        Task {
            await runAuthenticationCycle()
        }
    }

    func reset() {
        state = .idle
        logMessages.removeAll()
        recordedSamples.removeAll()
        stopAudioEngine()
    }

    // MARK: - Authentication Cycle

    @MainActor
    private func runAuthenticationCycle() async {
        do {
            // Step 1: Listen for READY tone from laptop
            updateState(.listeningReady)
            log("🚀 Starting authentication cycle...")
            log("👂 Listening for READY tone from laptop...")
            try await listenForReadyTone()
            log("✅ READY tone detected")
            
            // Step 2: Send ACK tone to laptop
            updateState(.sendingAck)
            log("📡 Sending ACK tone to laptop...")
            try await sendAckTone()
            log("✅ ACK sent, connection established")
            
            // Step 3: Listen for challenge
            updateState(.listening)
            log("🎧 Listening for acoustic challenge...")
            let audioData = try await recordAudio()
            log("✅ Recorded \(audioData.count) audio samples")

            // Step 4: Decode FSK signal
            updateState(.decoding)
            log("🔍 Decoding FSK signal...")
            let expectedBits = challengeSizeBytes * 8
            let bits = fskDecoder.decodeSignal(signal: audioData, expectedBits: expectedBits)
            log("📊 Decoded \(bits.count) bits")
            let challenge = fskDecoder.bitsToData(bits)

            guard challenge.count == challengeSizeBytes else {
                throw AuthError.decodingFailed("Expected \(challengeSizeBytes) bytes, got \(challenge.count)")
            }
            log("✅ Challenge decoded: \(challenge.hex.prefix(16))...")

            // Step 5: Compute HMAC response
            updateState(.computing)
            log("🔐 Computing HMAC-SHA256 response...")
            let response = cryptoEngine.computeResponse(challenge: challenge)
            log("✅ Response computed: \(response.hex.prefix(16))...")

            // Step 6: Transmit response
            updateState(.transmitting)
            log("📡 Transmitting response acoustically...")
            try await transmitResponse(response)
            log("✅ Transmission complete")
            
            // Step 7: Listen for ACK/NACK confirmation
            updateState(.listeningConfirmation)
            log("👂 Waiting for laptop confirmation...")
            let success = try await listenForConfirmation()
            
            if success {
                updateState(.authenticated)
                log("🎉 Authentication successful - laptop accepted response")
            } else {
                updateState(.failed("Authentication rejected by laptop"))
                log("❌ Authentication failed - laptop rejected response")
            }

        } catch {
            updateState(.failed(error.localizedDescription))
            log("❌ ERROR: \(error.localizedDescription)")
        }
    }

    // MARK: - Handshaking Functions
    
    /// Listen for READY tone from laptop (12 kHz)
    private func listenForReadyTone() async throws {
        let duration = 10.0
        let samples = try await recordTone(duration: duration)
        let actualRate = recordingEngine.inputNode.outputFormat(forBus: 0).sampleRate
        let detected = fskDecoder.detectTone(frequency: readyToneFreq, in: samples, threshold: 3.0, actualSampleRate: actualRate)
        if !detected {
            throw AuthError.decodingFailed("READY tone not detected - ensure laptop is transmitting")
        }
    }
    
    /// Send ACK tone to laptop (14 kHz)
    private func sendAckTone() async throws {
        let tone = fskDecoder.generateTone(frequency: ackToneFreq, duration: toneDuration)
        try await playSignal(tone)
    }
    
    /// Listen for ACK (12 kHz) or NACK (6 kHz) from laptop
    /// Returns true if ACK, false if NACK
    private func listenForConfirmation() async throws -> Bool {
        let duration = 10.0  // Listen for up to 10 seconds
        let samples = try await recordTone(duration: duration)
        
        let ackDetected = fskDecoder.detectTone(frequency: readyToneFreq, in: samples, threshold: 50.0)
        let nackDetected = fskDecoder.detectTone(frequency: nackToneFreq, in: samples, threshold: 50.0)
        
        if ackDetected {
            return true
        } else if nackDetected {
            return false
        } else {
            throw AuthError.decodingFailed("No confirmation tone received from laptop")
        }
    }
    
    /// Record audio for tone detection (shorter duration than full FSK recording)
    private func recordTone(duration: Double) async throws -> [Float] {
        return try await withCheckedThrowingContinuation { continuation in
            Task { @MainActor in
                do {
                    let session = AVAudioSession.sharedInstance()
                    try session.setCategory(.record, mode: .default, options: [])
                    try session.setActive(true)
                    
                    let inputNode = self.recordingEngine.inputNode
                    let inputFormat = inputNode.outputFormat(forBus: 0)
                    print("[AcousticAuth] recordTone input format: \(inputFormat.sampleRate) Hz")
                    let totalSamples = Int(inputFormat.sampleRate * duration)
                    
                    var samples: [Float] = []
                    var resumed = false
                    
                    inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { buffer, _ in
                        guard !resumed else { return }
                        
                        guard let channelData = buffer.floatChannelData?[0] else { return }
                        let frameCount = Int(buffer.frameLength)
                        samples.append(contentsOf: UnsafeBufferPointer(start: channelData, count: frameCount))
                        
                        if samples.count >= totalSamples && !resumed {
                            resumed = true
                            self.recordingEngine.inputNode.removeTap(onBus: 0)
                            self.recordingEngine.stop()
                            try? session.setActive(false)
                            continuation.resume(returning: Array(samples.prefix(totalSamples)))
                        }
                    }
                    
                    try self.recordingEngine.start()
                    
                    // Timeout
                    DispatchQueue.main.asyncAfter(deadline: .now() + duration + 1.0) {
                        if !resumed {
                            resumed = true
                            if self.recordingEngine.isRunning {
                                self.recordingEngine.inputNode.removeTap(onBus: 0)
                                self.recordingEngine.stop()
                                try? session.setActive(false)
                            }
                            continuation.resume(returning: samples)
                        }
                    }
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - Audio Recording

    private func recordAudio() async throws -> [Float] {
        return try await withCheckedThrowingContinuation { continuation in
            Task { @MainActor in
                do {
                    // Request microphone permission first
                    let session = AVAudioSession.sharedInstance()
                    
                    // Check if we have permission
                    switch session.recordPermission {
                    case .denied:
                        self.log("❌ Microphone permission denied")
                        continuation.resume(throwing: AuthError.decodingFailed("Microphone permission denied. Enable in Settings."))
                        return
                    case .undetermined:
                        self.log("❓ Requesting microphone permission...")
                        // Request permission
                        let granted = await withCheckedContinuation { permContinuation in
                            session.requestRecordPermission { granted in
                                permContinuation.resume(returning: granted)
                            }
                        }
                        if !granted {
                            self.log("❌ Permission denied by user")
                            continuation.resume(throwing: AuthError.decodingFailed("Microphone permission denied"))
                            return
                        }
                        self.log("✅ Permission granted")
                    case .granted:
                        self.log("✅ Microphone permission already granted")
                        break
                    @unknown default:
                        break
                    }
                    
                    self.log("🎵 Setting up audio session...")
                    try session.setCategory(.record, mode: .measurement, options: [])
                    try session.setActive(true, options: [])

                    let inputNode = self.recordingEngine.inputNode
                    // Use the microphone's native format
                    let inputFormat = inputNode.outputFormat(forBus: 0)
                    self.log("🎶 Input format: \(inputFormat.sampleRate) Hz, \(inputFormat.channelCount) ch")

                    // Calculate recording duration using the ACTUAL sample rate
                    // Protocol frame structure: preamble(1) + type(1) + seq(1) + length(1) + payload(16) + CRC(2) = 21 bytes
                    let protocolOverhead = 5  // preamble + type + seq + length + CRC bytes
                    let totalBytes = self.challengeSizeBytes + protocolOverhead
                    let totalSymbols = totalBytes * 8 + 7  // data bits + Barker-7 preamble
                    let dataDuration = Double(totalSymbols) * self.fskDecoder.symbolDuration
                    let duration = dataDuration + 3.0  // Add 3s buffer for finding sync
                    let totalSamples = Int(inputFormat.sampleRate * duration)  // Use ACTUAL sample rate
                    
                    self.log("⏱️ Recording duration: \(String(format: "%.1f", duration))s (\(totalSamples) samples at \(inputFormat.sampleRate)Hz)")
                    self.log("📊 Expecting \(totalSymbols) symbols (\(totalBytes) bytes with protocol overhead)")

                    var samples: [Float] = []
                    var resumed = false
                    
                    self.log("🎤 Installing audio tap...")
                    self.log("📊 Need to record \(totalSamples) samples (\(String(format: "%.1f", duration))s)")

                    inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { buffer, _ in
                        guard !resumed else { return }
                        
                        // Convert to Float32 samples
                        guard let channelData = buffer.floatChannelData?[0] else { return }
                        let frameCount = Int(buffer.frameLength)
                        
                        // Resample if needed
                        let sampleRateRatio = self.fskDecoder.sampleRate / inputFormat.sampleRate
                        if abs(sampleRateRatio - 1.0) < 0.01 {
                            // Sample rates are close enough, use directly
                            samples.append(contentsOf: UnsafeBufferPointer(start: channelData, count: frameCount))
                        } else {
                            // Simple resampling
                            for i in 0..<frameCount {
                                samples.append(channelData[i])
                            }
                        }
                        
                        // Log progress every 20000 samples
                        if samples.count % 20000 < frameCount {
                            DispatchQueue.main.async {
                                self.log("📊 Recording: \(samples.count)/\(totalSamples) samples")
                            }
                        }

                        if samples.count >= totalSamples && !resumed {
                            resumed = true
                            DispatchQueue.main.async {
                                self.log("✅ Recording complete: \(samples.count) samples")
                                self.log("🛑 Stopping audio engine...")
                            }
                            self.recordingEngine.inputNode.removeTap(onBus: 0)
                            self.recordingEngine.stop()
                            try? session.setActive(false, options: [])
                            continuation.resume(returning: Array(samples.prefix(totalSamples)))
                        }
                    }
                    
                    self.log("▶️ Starting audio engine...")
                    try self.recordingEngine.start()
                    self.log("✅ Audio engine started, recording for \(String(format: "%.1f", duration))s...")

                    // Timeout safety
                    DispatchQueue.main.asyncAfter(deadline: .now() + duration + 2.0) {
                        if !resumed {
                            resumed = true
                            self.log("⏰ Timeout reached, stopping...")
                            if self.recordingEngine.isRunning {
                                self.recordingEngine.inputNode.removeTap(onBus: 0)
                                self.recordingEngine.stop()
                                try? session.setActive(false, options: [])
                            }
                            self.log("✅ Collected \(samples.count) samples before timeout")
                            continuation.resume(returning: samples)
                        }
                    }

                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - Audio Transmission

    private func transmitResponse(_ response: Data) async throws {
        let bits = fskDecoder.dataToBits(response)
        
        log("🔊 Preparing \(bits.count) bits for transmission...")

        // Build Barker-7 preamble + data signal
        let barker: [Double] = [1, 1, 1, -1, -1, 1, -1]
        var signal: [Float] = []

        // Preamble
        for chip in barker {
            let freq = chip > 0 ? fskDecoder.f1 : fskDecoder.f0
            signal.append(contentsOf: generateTone(frequency: freq, duration: fskDecoder.symbolDuration))
        }

        // Data bits
        for bit in bits {
            let freq = bit == "1" ? fskDecoder.f1 : fskDecoder.f0
            signal.append(contentsOf: generateTone(frequency: freq, duration: fskDecoder.symbolDuration))
        }
        
        log("🎵 Generated \(signal.count) audio samples for playback")

        try await playSignal(signal)
    }

    private func generateTone(frequency: Double, duration: Double) -> [Float] {
        let samples = Int(fskDecoder.sampleRate * duration)
        let fadeLen = max(1, Int(Double(samples) * 0.05))

        var tone = (0..<samples).map { i in
            Float(0.3 * sin(2.0 * Double.pi * frequency * Double(i) / fskDecoder.sampleRate))
        }

        // Fade in/out to reduce clicks
        for i in 0..<fadeLen {
            let factor = Float(i) / Float(fadeLen)
            tone[i] *= factor
            tone[samples - 1 - i] *= factor
        }

        return tone
    }

    private func playSignal(_ samples: [Float]) async throws {
        return try await withCheckedThrowingContinuation { continuation in
            do {
                log("🎶 Configuring playback audio session...")
                let session = AVAudioSession.sharedInstance()
                try session.setActive(false)
                try session.setCategory(.playback, mode: .default, options: [])
                try session.setActive(true)

                let format = AVAudioFormat(
                    standardFormatWithSampleRate: fskDecoder.sampleRate,
                    channels: 1
                )!

                guard let buffer = AVAudioPCMBuffer(pcmFormat: format,
                                                    frameCapacity: AVAudioFrameCount(samples.count)) else {
                    throw AuthError.transmissionFailed("Could not create audio buffer")
                }

                buffer.frameLength = AVAudioFrameCount(samples.count)
                let channelData = buffer.floatChannelData![0]
                for (i, sample) in samples.enumerated() {
                    channelData[i] = sample
                }
                
                log("🔊 Setting up player node...")
                let playerNode = AVAudioPlayerNode()
                playbackEngine.attach(playerNode)
                playbackEngine.connect(playerNode, to: playbackEngine.mainMixerNode, format: format)

                log("▶️ Starting playback...")
                try playbackEngine.start()

                playerNode.scheduleBuffer(buffer) {
                    self.log("✅ Playback complete")
                    self.playbackEngine.stop()
                    try? session.setActive(false)
                    continuation.resume()
                }
                
                playerNode.play()

            } catch {
                log("❌ Playback error: \(error.localizedDescription)")
                continuation.resume(throwing: error)
            }
        }
    }

    // MARK: - Helpers

    @MainActor
    private func updateState(_ newState: AuthState) {
        state = newState
        // Log state changes to Xcode console
        switch newState {
        case .idle:
            print("[AcousticAuth] STATE: Idle")
        case .listeningReady:
            print("[AcousticAuth] STATE: Listening for READY")
        case .sendingAck:
            print("[AcousticAuth] STATE: Sending ACK")
        case .listening:
            print("[AcousticAuth] STATE: Listening for Challenge")
        case .decoding:
            print("[AcousticAuth] STATE: Decoding")
        case .computing:
            print("[AcousticAuth] STATE: Computing")
        case .transmitting:
            print("[AcousticAuth] STATE: Transmitting")
        case .listeningConfirmation:
            print("[AcousticAuth] STATE: Listening for Confirmation")
        case .authenticated:
            print("[AcousticAuth] STATE: Authenticated ✅")
        case .failed(let msg):
            print("[AcousticAuth] STATE: Failed - \(msg) ❌")
        }
    }

    private func log(_ message: String) {
        print("[AcousticAuth] \(message)")  // Print to Xcode console
        DispatchQueue.main.async {
            self.logMessages.append(message)  // Show in iPhone UI
        }
    }

    private func stopAudioEngine() {
        if recordingEngine.isRunning {
            recordingEngine.inputNode.removeTap(onBus: 0)
            recordingEngine.stop()
        }
        if playbackEngine.isRunning {
            playbackEngine.stop()
        }
        try? AVAudioSession.sharedInstance().setActive(false, options: [])
    }
}

// MARK: - Errors

enum AuthError: LocalizedError {
    case decodingFailed(String)
    case transmissionFailed(String)

    var errorDescription: String? {
        switch self {
        case .decodingFailed(let msg):    return "Decoding failed: \(msg)"
        case .transmissionFailed(let msg): return "Transmission failed: \(msg)"
        }
    }
}

// MARK: - Data Extension

extension Data {
    var hex: String {
        return map { String(format: "%02x", $0) }.joined()
    }
}
