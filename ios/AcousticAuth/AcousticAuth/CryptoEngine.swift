import Foundation
import CryptoKit

/// Implements HMAC-SHA256 challenge-response authentication
/// Mirrors crypto_core.py CryptographicCore on the prover (iPhone) side
class CryptoEngine {

    private let sharedKey: SymmetricKey

    /// Initialise with a 256-bit shared secret
    /// In production this would be loaded from the iOS Keychain / Secure Enclave
    init(sharedKeyData: Data) {
        self.sharedKey = SymmetricKey(data: sharedKeyData)
    }

    /// Convenience initialiser using a hex string key (for testing)
    convenience init(hexKey: String) {
        var data = Data()
        var hex = hexKey
        while hex.count >= 2 {
            let byte = hex.prefix(2)
            hex = String(hex.dropFirst(2))
            if let value = UInt8(byte, radix: 16) {
                data.append(value)
            }
        }
        self.init(sharedKeyData: data)
    }

    // MARK: - Core Operations

    /// Compute HMAC-SHA256 response to a challenge
    /// R = HMAC(K, C) using SHA-256
    /// Mirrors: crypto_core.py CryptographicCore.compute_response()
    func computeResponse(challenge: Data) -> Data {
        let mac = HMAC<SHA256>.authenticationCode(
            for: challenge,
            using: sharedKey
        )
        return Data(mac)
    }

    /// Verify a received response against expected value
    /// Uses constant-time comparison to prevent timing attacks
    /// Mirrors: crypto_core.py CryptographicCore.verify_response()
    func verifyResponse(challenge: Data, response: Data) -> Bool {
        let expected = computeResponse(challenge: challenge)
        // HMAC.isValidAuthenticationCode provides constant-time comparison
        return HMAC<SHA256>.isValidAuthenticationCode(
            response,
            authenticating: challenge,
            using: sharedKey
        )
    }

    // MARK: - Key Info

    var keyLengthBytes: Int {
        return sharedKey.bitCount / 8
    }
}
