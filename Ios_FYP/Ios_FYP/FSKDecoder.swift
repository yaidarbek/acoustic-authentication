import Foundation
import AVFoundation
import Accelerate

/// FSK demodulator for the iPhone (prover) side
/// Mirrors working_fsk.py WorkingFSK on iOS
/// Receives FSK-encoded challenges from the laptop and decodes them
class FSKDecoder {

    // MARK: - Configuration (must match laptop Python config)
    let sampleRate: Double = 44100.0
    let f0: Double = 7000.0    // Binary '0' — 7 kHz
    let f1: Double = 9000.0    // Binary '1' — 9 kHz
    let symbolDuration: Double = 0.15  // 150ms — matches Python working_fsk.py
    let bandpassLow: Double  = 6000.0
    let bandpassHigh: Double = 10000.0
    let amplitude: Float = 0.3  // Single amplitude used everywhere

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
        // Build reference using same tone generation as encoder (with fade)
        var reference: [Float] = []
        for chip in barker {
            let freq = chip > 0 ? f1 : f0
            reference.append(contentsOf: generateTone(frequency: freq, duration: symbolDuration))
        }
        guard signal.count >= reference.count else { return 0 }

        // Limit search to first 3s
        let searchEnd   = min(signal.count - reference.count, Int(sampleRate * 3.0))
        let searchSlice = Array(signal[0..<(searchEnd + reference.count)])

        // Step 1: Coarse search on consistently downsampled signal
        let ds    = 10
        let sigDs = stride(from: 0, to: searchSlice.count, by: ds).map { searchSlice[$0] }
        let refDs = stride(from: 0, to: reference.count,   by: ds).map { reference[$0] }
        let corrLen = sigDs.count - refDs.count
        guard corrLen > 0 else { return 0 }
        var maxCorr: Float = 0
        var coarsePeak = 0
        for i in 0..<corrLen {
            var sum: Float = 0
            sigDs.withUnsafeBufferPointer { sigPtr in
                refDs.withUnsafeBufferPointer { refPtr in
                    vDSP_dotpr(sigPtr.baseAddress! + i, 1, refPtr.baseAddress!, 1, &sum, vDSP_Length(refDs.count))
                }
            }
            let c = abs(sum)
            if c > maxCorr { maxCorr = c; coarsePeak = i }
        }
        coarsePeak *= ds

        // Step 2: Fine search every 10 samples within +-100 samples of coarse peak
        let fineStart = max(0, coarsePeak - 100)
        let fineEnd   = min(signal.count - reference.count, coarsePeak + 100)
        maxCorr = 0
        var finePeak = coarsePeak
        for i in stride(from: fineStart, to: fineEnd, by: 10) {
            var sum: Float = 0
            signal.withUnsafeBufferPointer { sigPtr in
                reference.withUnsafeBufferPointer { refPtr in
                    vDSP_dotpr(sigPtr.baseAddress! + i, 1, refPtr.baseAddress!, 1, &sum, vDSP_Length(reference.count))
                }
            }
            let c = abs(sum)
            if c > maxCorr { maxCorr = c; finePeak = i }
        }

        // Step 3: Ultra-fine search every 1 sample within +-10 samples of fine peak
        let ultraStart = max(0, finePeak - 10)
        let ultraEnd   = min(signal.count - reference.count, finePeak + 10)
        for i in ultraStart..<ultraEnd {
            var sum: Float = 0
            signal.withUnsafeBufferPointer { sigPtr in
                reference.withUnsafeBufferPointer { refPtr in
                    vDSP_dotpr(sigPtr.baseAddress! + i, 1, refPtr.baseAddress!, 1, &sum, vDSP_Length(reference.count))
                }
            }
            let c = abs(sum)
            if c > maxCorr { maxCorr = c; finePeak = i }
        }

        print("[FSKDecoder] Barker sync: coarse=\(coarsePeak) fine=\(finePeak) peak=\(maxCorr)")
        return finePeak
    }

    // MARK: - FSK Decoding

    /// Decode FSK signal into binary string
    /// Pipeline: AGC -> Barker sync -> Goertzel demodulation
    /// Mirrors: working_fsk.py WorkingFSK.decode_signal()
    func decodeSignal(signal: [Float], expectedBits: Int) -> String {
        let startTime = Date()
        print("[FSKDecoder] Starting decode: \(signal.count) samples, expecting \(expectedBits) bits")

        // Step 1: Signal quality check
        let maxAmp = signal.map { abs($0) }.max() ?? 0
        let maxAmpStr = String(format: "%.4f", maxAmp)
        print("[FSKDecoder] Signal max amplitude: \(maxAmpStr)")
        guard maxAmp > 0.01 else {
            print("[FSKDecoder] Signal too weak, skipping decode")
            return ""
        }

        // Step 2: Barker sync on raw signal — find frame start first
        let syncStart = Date()
        print("[FSKDecoder] Searching for Barker-7 sync pattern...")
        let barkerLen = barker.count * samplesPerSymbol
        let frameStart = barkerSync(signal: signal)
        let dataStart  = frameStart + barkerLen
        let syncTime   = Date().timeIntervalSince(syncStart)
        let syncTimeStr = String(format: "%.3f", syncTime)
        print("[FSKDecoder] Frame start found at sample \(frameStart) (\(String(format: "%.3f", Double(frameStart)/sampleRate))s), data starts at \(dataStart) (\(String(format: "%.3f", Double(dataStart)/sampleRate))s) took \(syncTimeStr)s")

        // Step 3: Windowed AGC — normalize only the detected signal window
        let windowStart = max(0, frameStart)
        let windowEnd   = min(signal.count, dataStart + expectedBits * samplesPerSymbol)
        let window      = Array(signal[windowStart..<windowEnd])
        let normalized  = applyAGC(samples: window)
        let windowedDataStart = dataStart - windowStart

        // Step 4: Goertzel demodulation on normalized window
        let demodStart = Date()
        print("[FSKDecoder] Demodulating \(expectedBits) bits using Goertzel algorithm...")
        var decodedBits = ""

        for i in 0..<expectedBits {
            let symbolStart = windowedDataStart + i * samplesPerSymbol
            let symbolEnd   = symbolStart + samplesPerSymbol

            guard symbolEnd <= normalized.count else {
                print("[FSKDecoder] Ran out of samples at bit \(i)")
                break
            }

            let symbolData = Array(normalized[symbolStart..<symbolEnd])
            let powerF0 = goertzelDetect(samples: symbolData, frequency: f0)
            let powerF1 = goertzelDetect(samples: symbolData, frequency: f1)

            let bit = powerF1 > powerF0 ? "1" : "0"
            decodedBits += bit

            if (i + 1) % 32 == 0 {
                print("[FSKDecoder] Decoded \(i + 1)/\(expectedBits) bits: ...\(decodedBits.suffix(16))")
            }
        }

        let demodTime  = Date().timeIntervalSince(demodStart)
        let totalTime  = Date().timeIntervalSince(startTime)
        let demodTimeStr = String(format: "%.3f", demodTime)
        let totalTimeStr = String(format: "%.3f", totalTime)
        print("[FSKDecoder] Demodulation complete in \(demodTimeStr)s")
        print("[FSKDecoder] Total decoding time: \(totalTimeStr)s")
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
        guard !signal.isEmpty else { return false }
        let power = goertzelDetect(samples: signal, frequency: frequency, actualSampleRate: actualSampleRate ?? sampleRate)
        guard power.isFinite else { return false }
        print("[FSKDecoder] Tone detection at \(Int(frequency))Hz: power=\(String(format: "%.2f", power)), threshold=\(threshold)")
        return power > threshold
    }
    
    /// Generate a pure tone at specified frequency
    /// Used for ACK tone transmission
    func generateTone(frequency: Double, duration: Double, amplitude: Float? = nil) -> [Float] {
        let amp = amplitude ?? self.amplitude
        let samples = Int(sampleRate * duration)
        let fadeLen = max(1, Int(Double(samples) * 0.05))
        var tone: [Float] = []
        for i in 0..<samples {
            let phase = 2.0 * Double.pi * frequency * Double(i) / sampleRate
            tone.append(amp * Float(sin(phase)))
        }
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
