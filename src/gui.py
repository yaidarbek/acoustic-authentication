import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
import threading
import sys
import os

# Add src/ to path when running from anywhere
sys.path.insert(0, os.path.dirname(__file__))
from acoustic_auth import AcousticAuthenticator
from secure_storage import SecureStorage

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
        self.root.resizable(True, True)

        self.authenticator = None
        self.storage = None
        self.authenticated = False
        self.auth_running = False
        self.stop_requested = False
        self._build_ui()
        self._set_status("idle")
        self._update_storage_state()

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
            log_frame, height=6, width=50,
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

        self.stop_btn = tk.Button(
            btn_frame, text="Stop",
            font=("Helvetica", 12),
            bg=RED, fg=BG, activebackground=TEXT, activeforeground=BG,
            relief="flat", padx=20, pady=10, cursor="hand2",
            command=self._on_stop, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=8)

        self.test_btn = tk.Button(
            btn_frame, text="Test Mode",
            font=("Helvetica", 12),
            bg=YELLOW, fg=BG, activebackground=TEXT, activeforeground=BG,
            relief="flat", padx=20, pady=10, cursor="hand2",
            command=self._on_test_mode
        )
        self.test_btn.pack(side="left", padx=8)

        # Secure Storage Section
        storage_frame = tk.Frame(self.root, bg=PANEL, highlightthickness=1,
                                highlightbackground=BORDER)
        storage_frame.pack(fill="both", expand=True, padx=20, pady=(10, 10))

        tk.Label(storage_frame, text="SECURE STORAGE", font=("Helvetica", 8, "bold"),
                 bg=PANEL, fg=SUBTLE).pack(anchor="w", padx=12, pady=(8, 2))

        self.storage_status = tk.Label(
            storage_frame, text="🔒 Locked - Authenticate to access",
            font=("Helvetica", 10), bg=PANEL, fg=RED
        )
        self.storage_status.pack(anchor="w", padx=12, pady=(4, 8))

        # File list
        list_frame = tk.Frame(storage_frame, bg=PANEL)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(
            list_frame, height=5, bg=PANEL, fg=TEXT,
            font=("Courier", 9), relief="flat",
            selectbackground=BLUE, selectforeground=BG,
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Storage buttons
        storage_btn_frame = tk.Frame(storage_frame, bg=PANEL)
        storage_btn_frame.pack(pady=(0, 12))

        self.add_btn = tk.Button(
            storage_btn_frame, text="Add File",
            font=("Helvetica", 9), bg=BLUE, fg=BG,
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._on_add_file, state="disabled"
        )
        self.add_btn.pack(side="left", padx=4)

        self.open_btn = tk.Button(
            storage_btn_frame, text="Open File",
            font=("Helvetica", 9), bg=GREEN, fg=BG,
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._on_open_file, state="disabled"
        )
        self.open_btn.pack(side="left", padx=4)

        self.delete_btn = tk.Button(
            storage_btn_frame, text="Delete",
            font=("Helvetica", 9), bg=RED, fg=BG,
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._on_delete_file, state="disabled"
        )
        self.delete_btn.pack(side="left", padx=4)

    # ------------------------------------------------------------------
    # Status Management
    # ------------------------------------------------------------------

    def _set_status(self, state: str, message: str = None):
        states = {
            "idle":          (SUBTLE, "Idle"),
            "ready":         (YELLOW, "Sending READY - Waiting for iPhone..."),
            "connected":     (BLUE,   "iPhone Connected"),
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
        self.stop_btn.config(state="normal")
        self.result_label.config(text="")
        self.result_frame.config(bg=BG)
        self._clear_log()
        self.progress.start(12)
        self.auth_running = True
        self.stop_requested = False
        threading.Thread(target=self._run_authentication, daemon=True).start()

    def _on_reset(self):
        self.progress.stop()
        self._set_status("idle")
        self._clear_log()
        self.result_label.config(text="")
        self.result_frame.config(bg=BG)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.authenticated = False
        self.auth_running = False
        self.stop_requested = False
        self._update_storage_state()
        if self.authenticator:
            try:
                self.authenticator.cleanup()
            except Exception:
                pass
            self.authenticator = None

    def _on_stop(self):
        """Stop the current authentication process"""
        self.stop_requested = True
        self.progress.stop()
        self._set_status("idle", "Stopped by user")
        self._log("\nAuthentication stopped by user")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.auth_running = False
        if self.authenticator:
            try:
                self.authenticator.cleanup()
            except Exception:
                pass

    def _on_test_mode(self):
        """Simulate successful authentication for testing storage"""
        self._clear_log()
        self._log("TEST MODE: Simulating successful authentication...")
        test_auth = AcousticAuthenticator()
        shared_key = test_auth.auth_protocol.get_shared_key()
        self.authenticated = True
        self.storage = SecureStorage(shared_key)
        self._update_storage_state()
        self._refresh_file_list()
        self._set_status("success", "Test Mode - Storage Unlocked")
        self._log("\n✓ Storage unlocked in test mode")
        self._show_result(True)
        self.result_label.config(text="TEST MODE - STORAGE UNLOCKED")

    # ------------------------------------------------------------------
    # Authentication Flow (runs in background thread)
    # ------------------------------------------------------------------

    def _run_authentication(self):
        try:
            self.authenticator = AcousticAuthenticator()

            self.root.after(0, self._log, "=== ACOUSTIC AUTHENTICATION ===")
            self.root.after(0, self._log, "Press 'Authenticate' on iPhone when ready\n")
            self.root.after(0, self._set_status, "ready")

            if self.stop_requested:
                return

            # Phase 1: Beacon
            self.root.after(0, self._log, "[1/3] Running beacon...")
            if not self.authenticator.run_beacon():
                raise RuntimeError("Connection failed - iPhone did not respond")

            if self.stop_requested:
                return

            self.root.after(0, self._set_status, "connected")
            self.root.after(0, self._log, "      ✓ iPhone connected\n")

            # Phase 2: Sync
            self.root.after(0, self._set_status, "transmitting")
            self.root.after(0, self._log, "[2/3] Sending sync + challenge...")
            self.authenticator.send_sync()
            # Wait for iPhone to finish processing sync before sending challenge
            time.sleep(self.authenticator.SYNC_DURATION + self.authenticator.TONE_DURATION)
            challenge = self.authenticator.send_challenge()
            self.root.after(0, self._log, f"      Challenge: {challenge.hex()}")

            if self.stop_requested:
                return

            # Phase 3: Receive and verify response
            self.root.after(0, self._set_status, "waiting")
            self.root.after(0, self._log, "[3/3] Waiting for response...")
            response = self.authenticator.receive_response()

            if self.stop_requested:
                return

            self.root.after(0, self._set_status, "verifying")
            success = self.authenticator.auth_protocol.verify_authentication(response)
            self.authenticator.send_result(success)

            self.root.after(0, self.progress.stop)
            if success:
                self.root.after(0, self._set_status, "success")
                self.root.after(0, self._log, "\n🔓 ACCESS GRANTED")
                self.authenticated = True
                shared_key = self.authenticator.auth_protocol.get_shared_key()
                self.storage = SecureStorage(shared_key)
                self.root.after(0, self._update_storage_state)
                self.root.after(0, self._refresh_file_list)
            else:
                self.root.after(0, self._set_status, "failed")
                self.root.after(0, self._log, "\n🔒 ACCESS DENIED")

            self.root.after(0, self._show_result, success)

        except Exception as e:
            if not self.stop_requested:
                self.root.after(0, self.progress.stop)
                self.root.after(0, self._set_status, "error", f"Error: {str(e)}")
                self.root.after(0, self._log, f"\n❌ ERROR: {e}")
                self.root.after(0, self._show_result, False)
                # Try to send NACK on error
                try:
                    if self.authenticator:
                        self.authenticator.send_result(False)
                except:
                    pass

        finally:
            self.auth_running = False
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            if self.authenticator:
                try:
                    self.authenticator.cleanup()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Secure Storage Handlers
    # ------------------------------------------------------------------

    def _update_storage_state(self):
        """Update storage UI based on authentication state"""
        if self.authenticated:
            self.storage_status.config(
                text="🔓 Unlocked - Storage accessible",
                fg=GREEN
            )
            self.add_btn.config(state="normal")
            self.open_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            self.storage_status.config(
                text="🔒 Locked - Authenticate to access",
                fg=RED
            )
            self.add_btn.config(state="disabled")
            self.open_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def _refresh_file_list(self):
        """Refresh the file list display"""
        self.file_listbox.delete(0, tk.END)
        if self.storage:
            files = self.storage.list_files()
            for f in files:
                size_kb = f['size'] / 1024
                self.file_listbox.insert(tk.END, f"{f['name']} ({size_kb:.1f} KB)")

    def _on_add_file(self):
        """Add a file to secure storage"""
        if not self.authenticated:
            messagebox.showerror("Error", "Please authenticate first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select file to encrypt and store",
            filetypes=[("All files", "*.*")]
        )
        
        if file_path:
            if self.storage.add_file(file_path):
                self._refresh_file_list()
                messagebox.showinfo("Success", "File encrypted and stored")
            else:
                messagebox.showerror("Error", "Failed to store file")

    def _on_open_file(self):
        """Open a file from secure storage"""
        if not self.authenticated:
            messagebox.showerror("Error", "Please authenticate first")
            return
        
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        files = self.storage.list_files()
        file_id = files[selection[0]]['id']
        file_name = files[selection[0]]['name']
        
        data = self.storage.get_file(file_id)
        if data:
            save_path = filedialog.asksaveasfilename(
                title="Save decrypted file as",
                initialfile=file_name,
                defaultextension=""
            )
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(data)
                messagebox.showinfo("Success", f"File decrypted and saved to:\n{save_path}")
        else:
            messagebox.showerror("Error", "Failed to decrypt file")

    def _on_delete_file(self):
        """Delete a file from secure storage"""
        if not self.authenticated:
            messagebox.showerror("Error", "Please authenticate first")
            return
        
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        files = self.storage.list_files()
        file_id = files[selection[0]]['id']
        file_name = files[selection[0]]['name']
        
        if messagebox.askyesno("Confirm", f"Delete {file_name}?"):
            if self.storage.delete_file(file_id):
                self._refresh_file_list()
                messagebox.showinfo("Success", "File deleted")
            else:
                messagebox.showerror("Error", "Failed to delete file")


# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x950")
    root.resizable(True, True)
    app = AuthGUI(root)
    root.mainloop()
