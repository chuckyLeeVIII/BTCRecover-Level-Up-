#!/usr/bin/env python

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


DEFAULT_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


class BTCRecoverUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BTCRecover-Level-Up")
        self.geometry("900x600")

        self.search_paths = []

        self._build_widgets()
        self._populate_defaults()

    def _build_widgets(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Search paths:").pack(anchor=tk.W)

        self.paths_box = scrolledtext.ScrolledText(
            top, height=6, width=100, state="disabled"
        )
        self.paths_box.pack(fill=tk.X, pady=5)

        btn_row = tk.Frame(top)
        btn_row.pack(fill=tk.X)

        tk.Button(btn_row, text="Add Folder…", command=self.add_folder).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            btn_row, text="Clear", command=self.clear_paths
        ).pack(side=tk.LEFT, padx=5)

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

        action_row = tk.Frame(self)
        action_row.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            action_row, text="Start Scan & Recover", command=self.start_recover
        ).pack(side=tk.LEFT, padx=5)

        self.output = scrolledtext.ScrolledText(
            self, height=18, width=100, state="disabled"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _append_output(self, text: str):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")
        self.update_idletasks()

    def _populate_defaults(self):
        # Home and repo root
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
        if not self.search_paths:
            messagebox.showerror("Error", "No search paths selected.")
            return

        self._append_output("[*] Starting BTCRecover-Level-Up...")
        t = threading.Thread(target=self._run_recover, daemon=True)
        t.start()

    def _run_recover(self):
        env = os.environ.copy()

        # Pass search paths and cross-OS toggles via env vars for orchestrator
        env["BTCR_LEVELUP_SEARCH_PATHS"] = os.pathsep.join(self.search_paths)
        env["BTCR_LEVELUP_SCAN_WINDOWS"] = "1" if self.var_scan_windows.get() else "0"
        env["BTCR_LEVELUP_SCAN_LINUX"] = "1" if self.var_scan_linux.get() else "0"

        cmd = [sys.executable, os.path.join(DEFAULT_REPO_ROOT, "btcrecover.py")]

        self._append_output(f"[*] Running: {' '.join(cmd)}")
        try:
            import subprocess

            proc = subprocess.Popen(
                cmd,
                cwd=DEFAULT_REPO_ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                self._append_output(line.rstrip("\n"))
            proc.wait()
            self._append_output(f"[+] btcrecover.py exited with code {proc.returncode}")
        except Exception as e:
            self._append_output(f"[!] Error running btcrecover.py: {e}")


def main():
    app = BTCRecoverUI()
    app.mainloop()


if __name__ == "__main__":
    main()
