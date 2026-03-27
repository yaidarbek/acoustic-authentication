import Foundation
import AVFoundation
import Accelerate

/// FSK demodulator for the iPhone (prover) side
/// Mirrors working_fsk.py WorkingFSK on iOS
/// Receives FSK-encoded challenges from the laptop and decodes them
class FSKDecoder {

    // MARK: - Configuration (must match laptop Python config)
    let sampleRate: Double = 44100.0
    let f0: Double = 8000.0    // Binary '0' — 8 kHz
    let f1: Double = 10000.0   // Binary '1' — 10 kHz
    let symbolDuration: Double = 0.1  // 100 ms per symbol
    let bandpassLow: Double  = 7000.0
    let bandpassHigh: Double = 11000.0

    // Barker-7 sequence for synchronization
    private let barker: [Double] = [1, 1, 1, -1, -1, 1, -1]

    var samplesPerSymbol: Int {
        return Int(sampleRate * symbolDuration)
    }

    // MARK: - Goertzel Algorithm

    /// Compute signal power at a specific frequency using Goertzel algorithm
    /// More efficient than FFT for detecting two specific frequencies
    /// Mirrors: working_fsk.py WorkingFSK.goertzel_detect()
    func goertzelDetect(samples: [Float], frequency: Double) -> Double {
        let N = samples.count
        let k = Int(0.5 + (Double(N) * frequency / sampleRate))
        let w = (2.0 * Double.pi / Double(N)) * Double(k)
        let cosine = cos(w)
        let coeff = 2.0 * cosine

        var q0: Double = 0
        var q1: Double = 0
        var q2: Double = 0

        for sample in samples {
            q0 = coeff * q1 - q2 + Double(sample)
            q2 = q1
            q1 = q0
        }

        let real = q1 - q2 * cosine
        let imag = q2 * sin(w)
        return sqrt(real * real + imag * imag)
    }

    // MARK: - Automatic Gain Control

    /// Normalize signal amplitude to [-1, 1] range
    /// Compensates for distance-dependent attenuation
    /// Mirrors: working_fsk.py WorkingFSK.apply_agc()
    func applyAGC(samples: [Float]) -> [Float] {
        let maxAmp = samples.map { abs($0) }.max() ?? 0
        guard maxAmp > 0 else { return samples }
        return samples.map { $0 / maxAmp }
    }

    // MARK: - Barker Synchronization

    /// Find frame start using Barker-7 cross-correlation
    /// Mirrors: working_fsk.py WorkingFSK.barker_sync()
    func barkerSync(signal: [Float]) -> Int {
        // Build reference signal: each Barker chip is one symbol duration
        var reference: [Float] = []
        for chip in barker {
            let freq = chip > 0 ? f1 : f0
            let tone = generateToneBuffer(frequency: freq, duration: symbolDuration)
            reference.append(contentsOf: tone)
        }

        guard signal.count >= reference.count else { return 0 }

        // Cross-correlate signal with reference
        let corrLength = signal.count - reference.count + 1
        var correlation = [Float](repeating: 0, count: corrLength)

        for i in 0..<corrLength {
            var sum: Float = 0
            for j in 0..<reference.count {
                sum += signal[i + j] * reference[j]
            }
            correlation[i] = abs(sum)
        }

        // Return index of peak correlation
        let maxIndex = correlation.enumerated().max(by: { $0.element < $1.element })?.offset ?? 0
        return maxIndex
    }

    // MARK: - FSK Decoding

    /// Decode FSK signal into binary string
    /// Pipeline: AGC -> Barker sync -> Goertzel demodulation
    /// Mirrors: working_fsk.py WorkingFSK.decode_signal()
    func decodeSignal(signal: [Float], expectedBits: Int) -> String {
        // Step 1: AGC
        let normalized = applyAGC(samples: signal)

        // Step 2: Barker sync — find frame start
        let barkerLen = barker.count * samplesPerSymbol
        let frameStart = barkerSync(signal: normalized)
        let dataStart = frameStart + barkerLen

        // Step 3: Goertzel demodulation
        var decodedBits = ""

        for i in 0..<expectedBits {
            let symbolStart = dataStart + i * samplesPerSymbol
            let symbolEnd = symbolStart + samplesPerSymbol

            guard symbolEnd <= normalized.count else { break }

            let symbolData = Array(normalized[symbolStart..<symbolEnd])
            let powerF0 = goertzelDetect(samples: symbolData, frequency: f0)
            let powerF1 = goertzelDetect(samples: symbolData, frequency: f1)

            decodedBits += powerF1 > powerF0 ? "1" : "0"
        }

        return decodedBits
    }

    // MARK: - Bit/Byte Conversion

    /// Convert binary string to Data
    /// Mirrors: acoustic_auth.py AcousticAuthenticator.bits_to_bytes()
    func bitsToData(_ bits: String) -> Data {
        var paddedBits = bits
        while paddedBits.count % 8 != 0 {
            paddedBits += "0"
        }

        var data = Data()
        var index = paddedBits.startIndex
        while index < paddedBits.endIndex {
            let byteEnd = paddedBits.index(index, offsetBy: 8)
            let byteStr = String(paddedBits[index..<byteEnd])
            if let byte = UInt8(byteStr, radix: 2) {
                data.append(byte)
            }
            index = byteEnd
        }
        return data
    }

    /// Convert Data to binary string
    func dataToBits(_ data: Data) -> String {
        return data.map { String($0, radix: 2).leftPadded(toLength: 8, with: "0") }.joined()
    }

    // MARK: - Tone Generation (for Barker reference signal)

    private func generateToneBuffer(frequency: Double, duration: Double) -> [Float] {
        let samples = Int(sampleRate * duration)
        return (0..<samples).map { i in
            Float(sin(2.0 * Double.pi * frequency * Double(i) / sampleRate))
        }
    }
}

// MARK: - String Helper

private extension String {
    func leftPadded(toLength length: Int, with character: Character) -> String {
        let padding = length - self.count
        guard padding > 0 else { return self }
        return String(repeating: character, count: padding) + self
    }
}
