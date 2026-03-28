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
    func goertzelDetect(samples: [Float], frequency: Double, actualSampleRate: Double? = nil) -> Double {
        let N = samples.count
        let rate = actualSampleRate ?? sampleRate
        let k = Int(0.5 + (Double(N) * frequency / rate))
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
        print("[FSKDecoder] Building Barker reference signal...")
        // Build reference signal: each Barker chip is one symbol duration
        var reference: [Float] = []
        for chip in barker {
            let freq = chip > 0 ? f1 : f0
            let tone = generateToneBuffer(frequency: freq, duration: symbolDuration)
            reference.append(contentsOf: tone)
        }

        guard signal.count >= reference.count else { 
            print("[FSKDecoder] Signal too short for Barker sync")
            return 0 
        }

        // Optimized cross-correlation: downsample for speed
        let step = 100  // Check every 100 samples instead of every sample
        let corrLength = (signal.count - reference.count) / step
        var maxCorr: Float = 0
        var maxIndex = 0
        
        print("[FSKDecoder] Cross-correlating (checking \(corrLength) positions)...")

        for i in stride(from: 0, to: signal.count - reference.count, by: step) {
            var sum: Float = 0
            // Sample every 10th point in reference for speed
            for j in stride(from: 0, to: reference.count, by: 10) {
                sum += signal[i + j] * reference[j]
            }
            let corr = abs(sum)
            if corr > maxCorr {
                maxCorr = corr
                maxIndex = i
            }
        }
        
        print("[FSKDecoder] Peak correlation at index \(maxIndex) (value: \(maxCorr))")
        return maxIndex
    }

    // MARK: - FSK Decoding

    /// Decode FSK signal into binary string
    /// Pipeline: AGC -> Barker sync -> Goertzel demodulation
    /// Mirrors: working_fsk.py WorkingFSK.decode_signal()
    func decodeSignal(signal: [Float], expectedBits: Int) -> String {
        let startTime = Date()
        print("[FSKDecoder] Starting decode: \(signal.count) samples, expecting \(expectedBits) bits")
        
        // Step 1: AGC
        let agcStart = Date()
        print("[FSKDecoder] Applying AGC normalization...")
        let normalized = applyAGC(samples: signal)
        let agcTime = Date().timeIntervalSince(agcStart)
        print("[FSKDecoder] AGC complete in \(String(format: "%.3f", agcTime))s")

        // Step 2: Barker sync — find frame start
        let syncStart = Date()
        print("[FSKDecoder] Searching for Barker-7 sync pattern...")
        let barkerLen = barker.count * samplesPerSymbol
        let frameStart = barkerSync(signal: normalized)
        let dataStart = frameStart + barkerLen
        let syncTime = Date().timeIntervalSince(syncStart)
        print("[FSKDecoder] Frame start found at sample \(frameStart), data starts at \(dataStart) (\(String(format: "%.3f", syncTime))s)")

        // Step 3: Goertzel demodulation
        let demodStart = Date()
        print("[FSKDecoder] Demodulating \(expectedBits) bits using Goertzel algorithm...")
        var decodedBits = ""

        for i in 0..<expectedBits {
            let symbolStart = dataStart + i * samplesPerSymbol
            let symbolEnd = symbolStart + samplesPerSymbol

            guard symbolEnd <= normalized.count else { 
                print("[FSKDecoder] Ran out of samples at bit \(i)")
                break 
            }

            let symbolData = Array(normalized[symbolStart..<symbolEnd])
            let powerF0 = goertzelDetect(samples: symbolData, frequency: f0)
            let powerF1 = goertzelDetect(samples: symbolData, frequency: f1)
            
            let bit = powerF1 > powerF0 ? "1" : "0"
            decodedBits += bit
            
            // Log every 32 bits
            if (i + 1) % 32 == 0 {
                print("[FSKDecoder] Decoded \(i + 1)/\(expectedBits) bits: ...\(decodedBits.suffix(16))")
            }
        }
        
        let demodTime = Date().timeIntervalSince(demodStart)
        let totalTime = Date().timeIntervalSince(startTime)
        print("[FSKDecoder] Demodulation complete in \(String(format: "%.3f", demodTime))s")
        print("[FSKDecoder] Total decoding time: \(String(format: "%.3f", totalTime))s")
        print("[FSKDecoder] Decoded \(decodedBits.count) bits")
        print("[FSKDecoder] First 32 bits: \(decodedBits.prefix(32))")
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
    
    // MARK: - Single Tone Detection (for handshaking)
    
    /// Detect presence of a specific frequency tone in signal
    /// Used for READY/ACK/NACK detection
    /// Returns true if tone power exceeds threshold
    func detectTone(frequency: Double, in signal: [Float], threshold: Double = 100.0, actualSampleRate: Double? = nil) -> Bool {
        let power = goertzelDetect(samples: signal, frequency: frequency, actualSampleRate: actualSampleRate ?? sampleRate)
        print("[FSKDecoder] Tone detection at \(Int(frequency))Hz: power=\(String(format: "%.2f", power)), threshold=\(threshold)")
        return power > threshold
    }
    
    /// Generate a pure tone at specified frequency
    /// Used for ACK tone transmission
    func generateTone(frequency: Double, duration: Double, amplitude: Float = 0.3) -> [Float] {
        let samples = Int(sampleRate * duration)
        let fadeLen = max(1, Int(Double(samples) * 0.05))
        
        // Generate base tone
        var tone: [Float] = []
        for i in 0..<samples {
            let phase = 2.0 * Double.pi * frequency * Double(i) / sampleRate
            let sinValue = sin(phase)
            let sample = Float(amplitude) * Float(sinValue)
            tone.append(sample)
        }
        
        // Fade in/out to reduce clicks
        for i in 0..<fadeLen {
            let factor = Float(i) / Float(fadeLen)
            tone[i] *= factor
            tone[samples - 1 - i] *= factor
        }
        
        return tone
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
