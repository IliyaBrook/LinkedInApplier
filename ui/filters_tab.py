import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class FiltersTab:
    def __init__(self, parent, filters_file):
        self.frame = ttk.Frame(parent)
        self.filters_file = filters_file
        self.badWords_var = tk.StringVar()
        self.titleFilterWords_var = tk.StringVar()
        self.titleSkipWords_var = tk.StringVar()
        self.create_widgets()
        self.load_filters()

    def create_widgets(self):
        ttk.Label(self.frame, text="Bad Words (comma separated)").pack(anchor="w")
        self.badWords_entry = ttk.Entry(self.frame, textvariable=self.badWords_var, width=60)
        self.badWords_entry.pack(fill="x")

        ttk.Label(self.frame, text="Title Filter Words (comma separated)").pack(anchor="w")
        self.titleFilterWords_entry = ttk.Entry(self.frame, textvariable=self.titleFilterWords_var, width=60)
        self.titleFilterWords_entry.pack(fill="x")

        ttk.Label(self.frame, text="Title Skip Words (comma separated)").pack(anchor="w")
        self.titleSkipWords_entry = ttk.Entry(self.frame, textvariable=self.titleSkipWords_var, width=60)
        self.titleSkipWords_entry.pack(fill="x")

        ttk.Button(self.frame, text="Save Filters", command=self.save_filters).pack(pady=5)

    def load_filters(self):
        try:
            with open(self.filters_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.badWords_var.set(", ".join(data.get("badWords", [])))
            self.titleFilterWords_var.set(", ".join(data.get("titleFilterWords", [])))
            self.titleSkipWords_var.set(", ".join(data.get("titleSkipWords", [])))
        except Exception:
            pass

    def save_filters(self):
        data = {
            "badWords": [w.strip() for w in self.badWords_var.get().split(",") if w.strip()],
            "titleFilterWords": [w.strip() for w in self.titleFilterWords_var.get().split(",") if w.strip()],
            "titleSkipWords": [w.strip() for w in self.titleSkipWords_var.get().split(",") if w.strip()]
        }
        try:
            with open(self.filters_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Filters saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e)) 