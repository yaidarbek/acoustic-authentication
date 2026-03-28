import Foundation
import AVFoundation

/// Authentication state machine
enum AuthState {
    case idle
    case listening
    case decoding
    case computing
    case transmitting
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
    private let audioEngine = AVAudioEngine()
    private var recordedSamples: [Float] = []

    // MARK: - Config
    private let challengeSizeBytes = 16   // 128-bit challenge
    private let responseSizeBytes  = 32   // 256-bit HMAC-SHA256 response

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
            // Step 1: Listen for challenge
            updateState(.listening)
            log("Listening for acoustic challenge...")
            let audioData = try await recordAudio()

            // Step 2: Decode FSK signal
            updateState(.decoding)
            log("Decoding FSK signal...")
            let expectedBits = challengeSizeBytes * 8
            let bits = fskDecoder.decodeSignal(signal: audioData, expectedBits: expectedBits)
            let challenge = fskDecoder.bitsToData(bits)

            guard challenge.count == challengeSizeBytes else {
                throw AuthError.decodingFailed("Expected \(challengeSizeBytes) bytes, got \(challenge.count)")
            }
            log("Challenge decoded: \(challenge.hex.prefix(16))...")

            // Step 3: Compute HMAC response
            updateState(.computing)
            log("Computing HMAC-SHA256 response...")
            let response = cryptoEngine.computeResponse(challenge: challenge)
            log("Response computed: \(response.hex.prefix(16))...")

            // Step 4: Transmit response
            updateState(.transmitting)
            log("Transmitting response acoustically...")
            try await transmitResponse(response)
            log("Transmission complete.")

            updateState(.authenticated)
            log("Authentication complete — response sent successfully.")

        } catch {
            updateState(.failed(error.localizedDescription))
            log("ERROR: \(error.localizedDescription)")
        }
    }

    // MARK: - Audio Recording

    private func recordAudio() async throws -> [Float] {
        return try await withCheckedThrowingContinuation { continuation in
            do {
                let session = AVAudioSession.sharedInstance()
                try session.setCategory(.record, mode: .measurement)
                try session.setActive(true)

                let inputNode = audioEngine.inputNode
                let format = AVAudioFormat(
                    standardFormatWithSampleRate: fskDecoder.sampleRate,
                    channels: 1
                )!

                // Calculate recording duration:
                // challenge bits + Barker-7 preamble (7 symbols) + 1s buffer
                let totalSymbols = challengeSizeBytes * 8 + 7
                let duration = Double(totalSymbols) * fskDecoder.symbolDuration + 1.0
                let totalSamples = Int(fskDecoder.sampleRate * duration)

                var samples: [Float] = []

                inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
                    let channelData = buffer.floatChannelData![0]
                    let frameCount = Int(buffer.frameLength)
                    samples.append(contentsOf: UnsafeBufferPointer(start: channelData, count: frameCount))

                    if samples.count >= totalSamples {
                        self.audioEngine.inputNode.removeTap(onBus: 0)
                        self.audioEngine.stop()
                        continuation.resume(returning: Array(samples.prefix(totalSamples)))
                    }
                }

                try audioEngine.start()

                // Timeout safety
                DispatchQueue.main.asyncAfter(deadline: .now() + duration + 2.0) {
                    if self.audioEngine.isRunning {
                        self.audioEngine.inputNode.removeTap(onBus: 0)
                        self.audioEngine.stop()
                        continuation.resume(returning: samples)
                    }
                }

            } catch {
                continuation.resume(throwing: error)
            }
        }
    }

    // MARK: - Audio Transmission

    private func transmitResponse(_ response: Data) async throws {
        let bits = fskDecoder.dataToBits(response)

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
                let session = AVAudioSession.sharedInstance()
                try session.setCategory(.playback, mode: .default)
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

                let playerNode = AVAudioPlayerNode()
                audioEngine.attach(playerNode)
                audioEngine.connect(playerNode, to: audioEngine.mainMixerNode, format: format)

                try audioEngine.start()

                playerNode.scheduleBuffer(buffer) {
                    self.audioEngine.stop()
                    continuation.resume()
                }
                playerNode.play()

            } catch {
                continuation.resume(throwing: error)
            }
        }
    }

    // MARK: - Helpers

    @MainActor
    private func updateState(_ newState: AuthState) {
        state = newState
    }

    private func log(_ message: String) {
        DispatchQueue.main.async {
            self.logMessages.append(message)
        }
    }

    private func stopAudioEngine() {
        if audioEngine.isRunning {
            audioEngine.stop()
        }
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
