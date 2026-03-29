import SwiftUI

struct ContentView: View {

    // MARK: - Shared key (in production: load from Keychain)
    // Must match the key used on the laptop Python side
    @StateObject private var authenticator = AcousticAuthenticator()

    // MARK: - Body

    var body: some View {
        ZStack {
            Color(hex: "#1e1e2e").ignoresSafeArea()

            VStack(spacing: 0) {
                headerView
                statusView
                logView
                Spacer()
                buttonView
                    .padding(.bottom, 40)
            }
        }
        .preferredColorScheme(.dark)
    }

    // MARK: - Header

    private var headerView: some View {
        VStack(spacing: 6) {
            Image(systemName: "waveform.and.mic")
                .font(.system(size: 44))
                .foregroundColor(Color(hex: "#89b4fa"))
                .padding(.top, 48)

            Text("Acoustic Auth")
                .font(.system(size: 26, weight: .bold))
                .foregroundColor(Color(hex: "#cdd6f4"))

            Text("Secure offline proximity authentication")
                .font(.system(size: 13))
                .foregroundColor(Color(hex: "#6c7086"))
        }
        .padding(.bottom, 24)
    }

    // MARK: - Status

    private var statusView: some View {
        VStack(spacing: 12) {
            HStack(spacing: 10) {
                Circle()
                    .fill(statusColour)
                    .frame(width: 12, height: 12)
                    .shadow(color: statusColour.opacity(0.6), radius: 4)

                Text(statusText)
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(statusColour)
            }
            .padding(.vertical, 14)
            .padding(.horizontal, 24)
            .background(Color(hex: "#2a2a3e"))
            .cornerRadius(12)

            if isActive {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: Color(hex: "#89b4fa")))
                    .scaleEffect(1.2)
            }
        }
        .padding(.horizontal, 24)
        .animation(.easeInOut, value: statusText)
    }

    // MARK: - Log

    private var logView: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("LOG")
                .font(.system(size: 11, weight: .bold))
                .foregroundColor(Color(hex: "#6c7086"))
                .padding(.horizontal, 4)

            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 4) {
                        ForEach(Array(authenticator.logMessages.enumerated()), id: \.offset) { index, message in
                            Text(message)
                                .font(.system(size: 12, design: .monospaced))
                                .foregroundColor(Color(hex: "#cdd6f4"))
                                .id(index)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(12)
                }
                .onChange(of: authenticator.logMessages.count) { oldValue, newValue in
                    if let last = authenticator.logMessages.indices.last {
                        proxy.scrollTo(last, anchor: .bottom)
                    }
                }
            }
            .frame(height: 200)
            .background(Color(hex: "#2a2a3e"))
            .cornerRadius(12)
        }
        .padding(.horizontal, 24)
        .padding(.top, 20)
    }

    // MARK: - Buttons

    private var buttonView: some View {
        VStack(spacing: 12) {
            // Result banner
            if case .authenticated = authenticator.state {
                resultBanner(text: "ACCESS GRANTED", colour: Color(hex: "#a6e3a1"))
            } else if case .failed = authenticator.state {
                resultBanner(text: "ACCESS DENIED", colour: Color(hex: "#f38ba8"))
            }

            HStack(spacing: 12) {
                Button(action: { authenticator.startAuthentication() }) {
                    Label("Authenticate", systemImage: "ear")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(Color(hex: "#1e1e2e"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(Color(hex: "#89b4fa"))
                        .cornerRadius(12)
                }
                .disabled(isActive)
                .opacity(isActive ? 0.5 : 1.0)

                Button(action: { authenticator.reset() }) {
                    Text("Reset")
                        .font(.system(size: 16))
                        .foregroundColor(Color(hex: "#cdd6f4"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(Color(hex: "#2a2a3e"))
                        .cornerRadius(12)
                }
            }
            .padding(.horizontal, 24)
        }
    }

    private func resultBanner(text: String, colour: Color) -> some View {
        Text(text)
            .font(.system(size: 18, weight: .bold))
            .foregroundColor(colour)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(colour.opacity(0.15))
            .cornerRadius(12)
            .padding(.horizontal, 24)
            .transition(.scale.combined(with: .opacity))
    }

    // MARK: - Computed Helpers

    private var statusText: String {
        switch authenticator.state {
        case .idle:             return "Idle — ready to authenticate"
        case .listeningBeacon:  return "Listening for READY beacon..."
        case .sendingAck:       return "Sending ACK..."
        case .listeningSync:    return "Waiting for sync packet..."
        case .listening:        return "Recording challenge..."
        case .decoding:         return "Decoding FSK signal..."
        case .computing:        return "Computing HMAC response..."
        case .transmitting:     return "Transmitting response..."
        case .listeningResult:  return "Waiting for result..."
        case .authenticated:    return "Authenticated"
        case .failed(let msg):  return "Failed: \(msg)"
        }
    }

    private var statusColour: Color {
        switch authenticator.state {
        case .idle:            return Color(hex: "#6c7086")
        case .listeningBeacon,
             .sendingAck,
             .listeningSync,
             .listening,
             .decoding,
             .computing,
             .transmitting,
             .listeningResult:  return Color(hex: "#f9e2af")
        case .authenticated:   return Color(hex: "#a6e3a1")
        case .failed:          return Color(hex: "#f38ba8")
        }
    }

    private var isActive: Bool {
        switch authenticator.state {
        case .listeningBeacon, .sendingAck, .listeningSync,
             .listening, .decoding, .computing, .transmitting, .listeningResult:
            return true
        default:
            return false
        }
    }
}

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r = Double((int >> 16) & 0xFF) / 255.0
        let g = Double((int >> 8)  & 0xFF) / 255.0
        let b = Double(int         & 0xFF) / 255.0
        self.init(red: r, green: g, blue: b)
    }
}

// MARK: - Preview

#Preview {
    ContentView()
}
