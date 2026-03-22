#!/usr/bin/env python

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

DEFAULT_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Import the real WIF pipeline
from wif_recover_pipeline import run_wif_recovery_pipeline


class BTCRecoverUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BTCRecover-Level-Up")
        self.geometry("900x650")

        self.search_paths = []

        self._build_widgets()
        self._populate_defaults()

    def _build_widgets(self):
        # Search paths + options
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Search paths (for wallet/key files):").pack(anchor=tk.W)

        self.paths_box = scrolledtext.ScrolledText(
            top, height=5, width=100, state="disabled"
        )
        self.paths_box.pack(fill=tk.X, pady=5)

        btn_row = tk.Frame(top)
        btn_row.pack(fill=tk.X)

        tk.Button(btn_row, text="Add Folder…", command=self.add_folder).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_row, text="Clear", command=self.clear_paths).pack(
            side=tk.LEFT, padx=5
        )

        opt_row = tk.Frame(self)
        opt_row.pack(fill=tk.X, padx=10, pady=5)

        self.var_scan_windows = tk.BooleanVar(value=True)
        self.var_scan_linux = tk.BooleanVar(value=True)

        tk.Checkbutton(
            opt_row,
            text="Scan Windows drives",
            variable=self.var_scan_windows,
        ).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(
            opt_row,
            text="Scan Linux/WSL roots",
            variable=self.var_scan_linux,
        ).pack(side=tk.LEFT, padx=5)

        # Direct WIF input
        wif_row = tk.Frame(self)
        wif_row.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(wif_row, text="Direct BTC WIF (optional):").pack(side=tk.LEFT)
        self.entry_wif = tk.Entry(wif_row, width=60)
        self.entry_wif.pack(side=tk.LEFT, padx=5)

        # Action button
        action_row = tk.Frame(self)
        action_row.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            action_row, text="Start Scan & Recover", command=self.start_recover
        ).pack(side=tk.LEFT, padx=5)

        # Output window
        self.output = scrolledtext.ScrolledText(
            self, height=20, width=100, state="disabled"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _append_output(self, text: str):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")
        self.update_idletasks()

    def _populate_defaults(self):
        home = os.path.expanduser("~")
        self._add_path(home)
        self._add_path(DEFAULT_REPO_ROOT)

        # Windows drives
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\"
            if os.path.isdir(path):
                self._add_path(path)

        # WSL/Linux mounts
        for letter in "abcdefghijklmnopqrstuvwxyz":
            path = f"/mnt/{letter}"
            if os.path.isdir(path):
                self._add_path(path)

        # Common Linux roots
        for p in ["/", "/home", "/media", "/mnt"]:
            if os.path.isdir(p):
                self._add_path(p)

    def _add_path(self, path: str):
        path = os.path.abspath(path)
        if path in self.search_paths:
            return
        self.search_paths.append(path)
        self.paths_box.configure(state="normal")
        self.paths_box.insert(tk.END, path + "\n")
        self.paths_box.configure(state="disabled")

    def add_folder(self):
        d = filedialog.askdirectory()
        if d:
            self._add_path(d)

    def clear_paths(self):
        self.search_paths = []
        self.paths_box.configure(state="normal")
        self.paths_box.delete("1.0", tk.END)
        self.paths_box.configure(state="disabled")

    def start_recover(self):
        # Capture WIF from the UI
        wif = self.entry_wif.get().strip()

        if not wif:
            messagebox.showerror("Error", "Enter a BTC WIF in the WIF field.")
            return

        self._append_output("[*] Starting BTCRecover-Level-Up for provided WIF...")
        t = threading.Thread(target=self._run_wif_pipeline, args=(wif,), daemon=True)
        t.start()

    def _run_wif_pipeline(self, wif: str):
        # Redirect stdout/stderr for the duration into the UI
        old_stdout, old_stderr = sys.stdout, sys.stderr

        class _UIWriter:
            def __init__(self, append_func):
                self._append = append_func

            def write(self, s):
                s = s.rstrip("\n")
                if s:
                    self._append(s)

            def flush(self):
                pass

        ui_writer = _UIWriter(self._append_output)
        sys.stdout = ui_writer
        sys.stderr = ui_writer

        try:
            run_wif_recovery_pipeline(wif, password_label="WIF")
        except Exception as e:
            self._append_output(f"[!] Error in WIF recovery pipeline: {e}")
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr


def main():
    app = BTCRecoverUI()
    app.mainloop()


if __name__ == "__main__":
    main()
