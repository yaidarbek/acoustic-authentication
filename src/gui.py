import tkinter as tk
from tkinter import ttk, font
import threading
import sys
import os

# Add src/ to path when running from anywhere
sys.path.insert(0, os.path.dirname(__file__))
from acoustic_auth import AcousticAuthenticator

# --- Colours ---
BG          = "#1e1e2e"
PANEL       = "#2a2a3e"
TEXT        = "#cdd6f4"
SUBTLE      = "#6c7086"
GREEN       = "#a6e3a1"
RED         = "#f38ba8"
YELLOW      = "#f9e2af"
BLUE        = "#89b4fa"
BORDER      = "#45475a"


class AuthGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Acoustic Authentication System")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.authenticator = None
        self._build_ui()
        self._set_status("idle")

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 20, "pady": 10}

        # Title
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        tk.Label(
            self.root, text="Acoustic Authentication",
            font=title_font, bg=BG, fg=TEXT
        ).pack(pady=(24, 4))

        tk.Label(
            self.root, text="Secure offline proximity authentication via FSK audio",
            font=("Helvetica", 10), bg=BG, fg=SUBTLE
        ).pack(pady=(0, 16))

        # Status panel
        status_frame = tk.Frame(self.root, bg=PANEL, bd=0, highlightthickness=1,
                                highlightbackground=BORDER)
        status_frame.pack(fill="x", **pad)

        tk.Label(status_frame, text="STATUS", font=("Helvetica", 8, "bold"),
                 bg=PANEL, fg=SUBTLE).pack(anchor="w", padx=12, pady=(10, 2))

        self.status_dot = tk.Label(status_frame, text="●", font=("Helvetica", 14),
                                   bg=PANEL, fg=SUBTLE)
        self.status_dot.pack(side="left", padx=(12, 6), pady=(0, 10))

        self.status_label = tk.Label(status_frame, text="Idle",
                                     font=("Helvetica", 13, "bold"),
                                     bg=PANEL, fg=TEXT)
        self.status_label.pack(side="left", pady=(0, 10))

        # Progress bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Auth.Horizontal.TProgressbar",
                        troughcolor=PANEL, background=BLUE,
                        bordercolor=BORDER, lightcolor=BLUE, darkcolor=BLUE)

        self.progress = ttk.Progressbar(
            self.root, style="Auth.Horizontal.TProgressbar",
            mode="indeterminate", length=360
        )
        self.progress.pack(**pad)

        # Log box
        log_frame = tk.Frame(self.root, bg=PANEL, highlightthickness=1,
                             highlightbackground=BORDER)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        tk.Label(log_frame, text="LOG", font=("Helvetica", 8, "bold"),
                 bg=PANEL, fg=SUBTLE).pack(anchor="w", padx=12, pady=(8, 2))

        self.log_text = tk.Text(
            log_frame, height=10, width=50,
            bg=PANEL, fg=TEXT, insertbackground=TEXT,
            font=("Courier", 10), relief="flat",
            state="disabled", wrap="word"
        )
        self.log_text.pack(padx=12, pady=(0, 12), fill="both", expand=True)

        # Result banner (hidden until auth completes)
        self.result_frame = tk.Frame(self.root, bg=BG)
        self.result_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.result_label = tk.Label(
            self.result_frame, text="", font=("Helvetica", 14, "bold"),
            bg=BG, fg=TEXT
        )
        self.result_label.pack()

        # Buttons
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=(0, 24))

        self.start_btn = tk.Button(
            btn_frame, text="Start Authentication",
            font=("Helvetica", 12, "bold"),
            bg=BLUE, fg=BG, activebackground=TEXT, activeforeground=BG,
            relief="flat", padx=20, pady=10, cursor="hand2",
            command=self._on_start
        )
        self.start_btn.pack(side="left", padx=8)

        self.reset_btn = tk.Button(
            btn_frame, text="Reset",
            font=("Helvetica", 12),
            bg=PANEL, fg=TEXT, activebackground=BORDER, activeforeground=TEXT,
            relief="flat", padx=20, pady=10, cursor="hand2",
            command=self._on_reset
        )
        self.reset_btn.pack(side="left", padx=8)

    # ------------------------------------------------------------------
    # Status Management
    # ------------------------------------------------------------------

    def _set_status(self, state: str, message: str = None):
        states = {
            "idle":          (SUBTLE, "Idle"),
            "transmitting":  (YELLOW, "Transmitting Challenge..."),
            "waiting":       (YELLOW, "Waiting for Response..."),
            "verifying":     (BLUE,   "Verifying Response..."),
            "success":       (GREEN,  "Authentication Successful"),
            "failed":        (RED,    "Authentication Failed"),
            "error":         (RED,    "Error"),
        }
        colour, label = states.get(state, (SUBTLE, "Idle"))
        if message:
            label = message

        self.status_dot.config(fg=colour)
        self.status_label.config(text=label, fg=colour)

    def _log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _show_result(self, success: bool):
        if success:
            self.result_label.config(
                text="ACCESS GRANTED", fg=GREEN,
                bg="#1a2e1a"
            )
            self.result_frame.config(bg="#1a2e1a")
        else:
            self.result_label.config(
                text="ACCESS DENIED", fg=RED,
                bg="#2e1a1a"
            )
            self.result_frame.config(bg="#2e1a1a")

    # ------------------------------------------------------------------
    # Button Handlers
    # ------------------------------------------------------------------

    def _on_start(self):
        self.start_btn.config(state="disabled")
        self.result_label.config(text="")
        self.result_frame.config(bg=BG)
        self._clear_log()
        self.progress.start(12)
        threading.Thread(target=self._run_authentication, daemon=True).start()

    def _on_reset(self):
        self.progress.stop()
        self._set_status("idle")
        self._clear_log()
        self.result_label.config(text="")
        self.result_frame.config(bg=BG)
        self.start_btn.config(state="normal")
        if self.authenticator:
            try:
                self.authenticator.cleanup()
            except Exception:
                pass
            self.authenticator = None

    # ------------------------------------------------------------------
    # Authentication Flow (runs in background thread)
    # ------------------------------------------------------------------

    def _run_authentication(self):
        try:
            self.authenticator = AcousticAuthenticator()

            # Step 1 — Generate and transmit challenge
            self.root.after(0, self._set_status, "transmitting")
            self.root.after(0, self._log, "[1/3] Generating cryptographic challenge...")
            challenge = self.authenticator.auth_protocol.initiate_authentication()
            self.root.after(0, self._log, f"      Challenge: {challenge.hex()[:16]}...")

            self.root.after(0, self._log, "[1/3] Transmitting challenge via FSK audio...")
            self.authenticator.fsk.transmit_data_with_protocol(challenge)
            self.root.after(0, self._log, "      Transmission complete.")

            # Step 2 — Receive response
            self.root.after(0, self._set_status, "waiting")
            self.root.after(0, self._log, "[2/3] Listening for response...")

            frame_bits = (32 + 5) * 8
            duration = frame_bits * self.authenticator.fsk.symbol_duration + 1.0
            rx_stats = self.authenticator.fsk.receive_data_with_protocol(
                expected_frames=1, timeout_per_frame=duration
            )

            if not rx_stats['successful_frames']:
                raise RuntimeError("No response received — check device proximity")

            received_response = rx_stats['recovered_data']
            self.root.after(0, self._log, f"      Response: {received_response.hex()[:16]}...")

            # Step 3 — Verify
            self.root.after(0, self._set_status, "verifying")
            self.root.after(0, self._log, "[3/3] Verifying HMAC-SHA256 response...")

            success = self.authenticator.auth_protocol.verify_authentication(received_response)

            # Show result
            self.root.after(0, self.progress.stop)
            if success:
                self.root.after(0, self._set_status, "success")
                self.root.after(0, self._log, "      Verification PASSED.")
                self.root.after(0, self._log, "\nACCESS GRANTED")
            else:
                self.root.after(0, self._set_status, "failed")
                self.root.after(0, self._log, "      Verification FAILED — response mismatch.")
                self.root.after(0, self._log, "\nACCESS DENIED")

            self.root.after(0, self._show_result, success)

        except Exception as e:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self._set_status, "error", f"Error: {str(e)}")
            self.root.after(0, self._log, f"\nERROR: {e}")
            self.root.after(0, self._show_result, False)

        finally:
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            if self.authenticator:
                try:
                    self.authenticator.cleanup()
                except Exception:
                    pass


# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("420x620")
    app = AuthGUI(root)
    root.mainloop()
