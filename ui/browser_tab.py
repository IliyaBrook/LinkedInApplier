import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json


class BrowserTab:
    def __init__(self, parent, browser_file):
        self.executable_entry = None
        self.frame = ttk.Frame(parent)
        self.browser_file = browser_file
        self.executable_path_var = tk.StringVar()
        self.profile_path_var = tk.StringVar()
        self.create_widgets()
        self.load_browser()

    def create_widgets(self):
        ttk.Label(self.frame, text="Executable Path").pack(anchor="w")
        path_frame = ttk.Frame(self.frame)
        path_frame.pack(fill="x")
        self.executable_entry = ttk.Entry(
            path_frame, textvariable=self.executable_path_var, width=60
        )
        self.executable_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_executable).pack(
            side="left"
        )

        ttk.Button(
            self.frame, text="Save Browser Settings", command=self.save_browser
        ).pack(pady=5)

    def load_browser(self):
        try:
            with open(self.browser_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.executable_path_var.set(data.get("executable_path", ""))
            self.profile_path_var.set(data.get("profile_path", ""))
        except (FileNotFoundError, json.JSONDecodeError, OSError, PermissionError):
            self.executable_path_var.set("")
            self.profile_path_var.set("")


    def save_browser(self):
        data = {
            "executable_path": self.executable_path_var.get(),
            "profile_path": self.profile_path_var.get(),
        }
        try:
            with open(self.browser_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Browser settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def browse_executable(self):
        path = filedialog.askopenfilename(title="Select Browser Executable")
        if path:
            self.executable_path_var.set(path)

    def browse_profile(self):
        path = filedialog.askdirectory(title="Select Browser Profile Directory")
        if path:
            self.profile_path_var.set(path)
