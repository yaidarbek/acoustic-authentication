import Foundation
import AVFoundation
import Combine

enum AuthState {
    case idle
    case listeningBeacon     // Listening for READY beacon in real-time chunks
    case sendingAck          // Sending ACK tone to laptop
    case listeningSync       // Listening for FSK sync packet
    case listening           // Listening for FSK challenge (slot 1)
    case decoding
    case computing
    case transmitting        // Sending FSK response (slot 2)
    case listeningResult     // Listening for result tone (slot 3)
    case authenticated
    case failed(String)
}

class AcousticAuthenticator: ObservableObject {

    @Published var state: AuthState = .idle
    @Published var logMessages: [String] = []

    private let fskDecoder   = FSKDecoder()
    private let cryptoEngine = CryptoEngine(hexKey: "0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0")
    private let recordingEngine = AVAudioEngine()
    private let playbackEngine  = AVAudioEngine()

    // Sizes
    private let challengeBits = 32
    private let syncBits      = 16
    private let syncPattern   = "1010101010101010"

    // Frequencies
    private let readyFreq: Double = 11000.0  // 11 kHz - READY beacon from laptop
    private let ackFreq:   Double = 13000.0  // 13 kHz - ACK to laptop

    // MARK: - Public API

    func startAuthentication() {
        logMessages.removeAll()
        log("🚀 Starting authentication...")
        Task { await runAuthenticationCycle() }
    }

    func reset() {
        state = .idle
        logMessages.removeAll()
        stopEngines()
    }

    // MARK: - Authentication Cycle

    @MainActor
    private func runAuthenticationCycle() async {
        do {
            // Phase 1: Listen for READY beacon in real-time chunks
            updateState(.listeningBeacon)
            log("👂 Listening for READY beacon (11kHz)...")
            try await listenForBeacon()
            log("✅ Beacon detected")

            // Send ACK
            updateState(.sendingAck)
            log("📡 Sending ACK (13kHz)...")
            try await playTone(frequency: ackFreq, duration: 1.0)
            log("✅ ACK sent")

            // Phase 2: Listen for sync packet
            updateState(.listeningSync)
            log("👂 Listening for sync packet...")
            try await listenForSync()
            log("✅ Sync received - challenge coming immediately")

            // Wait for laptop to finish sync transmission and start challenge
            let syncWait = Double(7 + syncBits) * fskDecoder.symbolDuration + 2.0
            try await Task.sleep(nanoseconds: UInt64(syncWait * 1_000_000_000))
            // Phase 3 Slot 1: Record challenge
            updateState(.listening)
            log("🎧 Recording FSK challenge (32 bits)...")
            let challengeAudio = try await recordSlot(bits: challengeBits)
            log("✅ Recorded \(challengeAudio.count) samples")

            // Decode challenge
            updateState(.decoding)
            log("🔍 Decoding challenge...")
            let challengeBitsStr = fskDecoder.decodeSignal(signal: challengeAudio, expectedBits: challengeBits)
            let challenge = fskDecoder.bitsToData(challengeBitsStr)
            guard challenge.count == challengeBits / 8 else {
                throw AuthError.decodingFailed("Expected \(challengeBits/8) bytes, got \(challenge.count)")
            }
            log("✅ Challenge: \(challenge.hex.prefix(8))...")

            // Compute response
            updateState(.computing)
            log("🔐 Computing truncated HMAC-SHA256...")
            let response = cryptoEngine.computeResponse(challenge: challenge)
            log("✅ Response: \(response.hex.prefix(8))...")

            // Phase 3 Slot 2: Transmit response
            updateState(.transmitting)
            log("📡 Transmitting FSK response (64 bits)...")
            try await transmitBits(data: response)
            log("✅ Response transmitted")

            // Wait for laptop to finish recording response, verify, and play result tone
            // Buffer = laptop's full response recording duration (response transmission + 2.0s buffer)
            let resultWait = Double(7 + 64) * fskDecoder.symbolDuration + 2.0 + 2.0
            try await Task.sleep(nanoseconds: UInt64(resultWait * 1_000_000_000))

            // Phase 3 Slot 3: Listen for result
            updateState(.listeningResult)
            log("👂 Listening for result tone...")
            let success = try await listenForResult()

            if success {
                updateState(.authenticated)
                log("🎉 ACCESS GRANTED")
            } else {
                updateState(.failed("Authentication rejected"))
                log("❌ ACCESS DENIED")
            }

        } catch {
            updateState(.failed(error.localizedDescription))
            log("❌ ERROR: \(error.localizedDescription)")
        }
    }

    // MARK: - Phase 1: Beacon detection (real-time chunks)

    private func listenForBeacon() async throws {
        let chunkDuration = 2.0   // check every 2s chunk
        let maxChunks     = 30    // up to 60 seconds total

        for _ in 0..<maxChunks {
            let samples    = try await recordRaw(duration: chunkDuration)
            let actualRate = recordingEngine.inputNode.outputFormat(forBus: 0).sampleRate
            if fskDecoder.detectTone(frequency: readyFreq, in: samples, threshold: 3.0, actualSampleRate: actualRate) {
                return
            }
        }
        throw AuthError.decodingFailed("READY beacon not detected")
    }

    // MARK: - Phase 2: Sync packet

    private func listenForSync() async throws {
        // Buffer = ackToneDuration (worst case laptop detects ACK at start of tone)
        let buffer = 1.0  // ackToneDuration
        let duration = Double(7 + syncBits) * fskDecoder.symbolDuration + buffer
        let samples  = try await recordResampled(duration: duration)
        let bits     = fskDecoder.decodeSignal(signal: samples, expectedBits: syncBits)

        guard String(bits.prefix(syncBits)) == String(syncPattern.prefix(syncBits)) else {
            throw AuthError.decodingFailed("Sync pattern mismatch: got \(bits.prefix(16))")
        }
    }

    // MARK: - Phase 3: Record a data slot

    private func recordSlot(bits: Int) async throws -> [Float] {
        // Buffer = sync transmission duration (worst case sync still transmitting when we start)
        let syncTransmitDuration = Double(7 + syncBits) * fskDecoder.symbolDuration
        let duration = Double(7 + bits) * fskDecoder.symbolDuration + syncTransmitDuration
        return try await recordResampled(duration: duration)
    }

    // MARK: - Phase 3: Transmit response bits

    private func transmitBits(data: Data) async throws {
        let bits   = fskDecoder.dataToBits(data)
        let barker: [Double] = [1, 1, 1, -1, -1, 1, -1]
        var signal: [Float]  = []

        for chip in barker {
            let freq = chip > 0 ? fskDecoder.f1 : fskDecoder.f0
            signal.append(contentsOf: generateTone(frequency: freq, duration: fskDecoder.symbolDuration))
        }
        for bit in bits {
            let freq = bit == "1" ? fskDecoder.f1 : fskDecoder.f0
            signal.append(contentsOf: generateTone(frequency: freq, duration: fskDecoder.symbolDuration))
        }

        try await playSignal(signal)
    }

    // MARK: - Phase 3: Result tone

    private func listenForResult() async throws -> Bool {
        let samples    = try await recordRaw(duration: 3.0)
        let actualRate = recordingEngine.inputNode.outputFormat(forBus: 0).sampleRate
        return fskDecoder.detectTone(frequency: readyFreq, in: samples, threshold: 3.0, actualSampleRate: actualRate)
    }

    // MARK: - Audio Helpers

    /// Record raw samples at hardware rate (no resampling) — for tone detection
    private func recordRaw(duration: Double) async throws -> [Float] {
        return try await withCheckedThrowingContinuation { continuation in
            Task { @MainActor in
                do {
                    let session = AVAudioSession.sharedInstance()
                    try session.setCategory(.record, mode: .default, options: [])
                    try session.setActive(true)

                    let inputNode   = self.recordingEngine.inputNode
                    let inputFormat = inputNode.outputFormat(forBus: 0)
                    let totalSamples = Int(inputFormat.sampleRate * duration)
                    var samples: [Float] = []
                    var resumed = false

                    inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { buffer, _ in
                        guard !resumed, let ch = buffer.floatChannelData?[0] else { return }
                        samples.append(contentsOf: UnsafeBufferPointer(start: ch, count: Int(buffer.frameLength)))
                        if samples.count >= totalSamples {
                            resumed = true
                            self.recordingEngine.inputNode.removeTap(onBus: 0)
                            self.recordingEngine.stop()
                            self.recordingEngine.reset()
                            try? session.setActive(false)
                            continuation.resume(returning: Array(samples.prefix(totalSamples)))
                        }
                    }

                    try self.recordingEngine.start()

                    DispatchQueue.main.asyncAfter(deadline: .now() + duration + 1.0) {
                        if !resumed {
                            resumed = true
                            if self.recordingEngine.isRunning {
                                self.recordingEngine.inputNode.removeTap(onBus: 0)
                                self.recordingEngine.stop()
                            }
                            self.recordingEngine.reset()
                            try? session.setActive(false)
                            continuation.resume(returning: samples)
                        }
                    }
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    /// Record and resample to FSKDecoder rate — for FSK decoding
    private func recordResampled(duration: Double) async throws -> [Float] {
        let raw        = try await recordRaw(duration: duration)
        let actualRate = recordingEngine.inputNode.outputFormat(forBus: 0).sampleRate
        return resample(raw, fromRate: actualRate, toRate: fskDecoder.sampleRate)
    }

    private func playTone(frequency: Double, duration: Double) async throws {
        let tone = fskDecoder.generateTone(frequency: frequency, duration: duration)
        try await playSignal(tone)
    }

    private func generateTone(frequency: Double, duration: Double) -> [Float] {
        let samples = Int(fskDecoder.sampleRate * duration)
        let fadeLen = max(1, Int(Double(samples) * 0.05))
        var tone = (0..<samples).map { i in
            Float(0.3 * sin(2.0 * Double.pi * frequency * Double(i) / fskDecoder.sampleRate))
        }
        for i in 0..<fadeLen {
            let f = Float(i) / Float(fadeLen)
            tone[i] *= f
            tone[samples - 1 - i] *= f
        }
        return tone
    }

    private func playSignal(_ samples: [Float]) async throws {
        return try await withCheckedThrowingContinuation { continuation in
            Task { @MainActor in
                do {
                    let session = AVAudioSession.sharedInstance()
                    try session.setActive(false)
                    try session.setCategory(.playback, mode: .default, options: [])
                    try session.setActive(true)

                    if self.playbackEngine.isRunning { self.playbackEngine.stop() }
                    self.playbackEngine.reset()

                    let format = AVAudioFormat(standardFormatWithSampleRate: self.fskDecoder.sampleRate, channels: 1)!
                    guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(samples.count)) else {
                        throw AuthError.transmissionFailed("Could not create audio buffer")
                    }
                    buffer.frameLength = AVAudioFrameCount(samples.count)
                    let ch = buffer.floatChannelData![0]
                    for (i, s) in samples.enumerated() { ch[i] = s }

                    let playerNode = AVAudioPlayerNode()
                    self.playbackEngine.attach(playerNode)
                    self.playbackEngine.connect(playerNode, to: self.playbackEngine.mainMixerNode, format: format)
                    try self.playbackEngine.start()

                    playerNode.scheduleBuffer(buffer) {
                        self.playbackEngine.stop()
                        self.playbackEngine.reset()
                        try? session.setActive(false)
                        continuation.resume()
                    }
                    playerNode.play()
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    private func resample(_ samples: [Float], fromRate: Double, toRate: Double) -> [Float] {
        guard abs(fromRate - toRate) > 1.0 else { return samples }
        let ratio       = toRate / fromRate
        let outputCount = Int(Double(samples.count) * ratio)
        var output      = [Float](repeating: 0, count: outputCount)
        for i in 0..<outputCount {
            let src  = Double(i) / ratio
            let lo   = Int(src)
            let hi   = min(lo + 1, samples.count - 1)
            let frac = Float(src - Double(lo))
            output[i] = samples[lo] * (1.0 - frac) + samples[hi] * frac
        }
        return output
    }

    // MARK: - Helpers

    @MainActor
    private func updateState(_ newState: AuthState) {
        state = newState
        switch newState {
        case .idle:              print("[AcousticAuth] STATE: Idle")
        case .listeningBeacon:   print("[AcousticAuth] STATE: Listening for Beacon")
        case .sendingAck:        print("[AcousticAuth] STATE: Sending ACK")
        case .listeningSync:     print("[AcousticAuth] STATE: Listening for Sync")
        case .listening:         print("[AcousticAuth] STATE: Listening for Challenge")
        case .decoding:          print("[AcousticAuth] STATE: Decoding")
        case .computing:         print("[AcousticAuth] STATE: Computing")
        case .transmitting:      print("[AcousticAuth] STATE: Transmitting")
        case .listeningResult:   print("[AcousticAuth] STATE: Listening for Result")
        case .authenticated:     print("[AcousticAuth] STATE: Authenticated ✅")
        case .failed(let msg):   print("[AcousticAuth] STATE: Failed - \(msg) ❌")
        }
    }

    private func log(_ message: String) {
        print("[AcousticAuth] \(message)")
        DispatchQueue.main.async { self.logMessages.append(message) }
    }

    private func stopEngines() {
        if recordingEngine.isRunning {
            recordingEngine.inputNode.removeTap(onBus: 0)
            recordingEngine.stop()
        }
        if playbackEngine.isRunning { playbackEngine.stop() }
        try? AVAudioSession.sharedInstance().setActive(false, options: [])
    }
}

// MARK: - Errors

enum AuthError: LocalizedError {
    case decodingFailed(String)
    case transmissionFailed(String)

    var errorDescription: String? {
        switch self {
        case .decodingFailed(let msg):     return "Decoding failed: \(msg)"
        case .transmissionFailed(let msg): return "Transmission failed: \(msg)"
        }
    }
}

extension Data {
    var hex: String { map { String(format: "%02x", $0) }.joined() }
}
