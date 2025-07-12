import tkinter as tk
from tkinter import ttk, messagebox
import json

class AutofillTab:
    def __init__(self, parent, autofill_file):
        self.frame = ttk.Frame(parent)
        self.autofill_file = autofill_file
        self.input_fields = {}
        self.radio_fields = {}
        self.dropdown_fields = {}
        self.autofill_sections = {}
        self.autofill_section_frames = {}
        self.autofill_section_states = {}
        self.create_widgets()
        self.load_autofill()

    def create_widgets(self):
        for section in ["inputFieldConfigs", "radioButtons", "dropdowns"]:
            frame = ttk.Frame(self.frame)
            frame.pack(fill="x", padx=5, pady=2)
            btn = ttk.Button(frame, text=section, width=25, command=lambda s=section: self.toggle_section(s))
            btn.pack(anchor="w", pady=(2,0))
            content = ttk.Frame(frame)
            self.autofill_sections[section] = content
            self.autofill_section_frames[section] = frame
            self.autofill_section_states[section] = False
        ttk.Button(self.frame, text="Save Autofill", command=self.save_autofill).pack(pady=5)

    def toggle_section(self, section):
        state = self.autofill_section_states[section]
        if state:
            self.autofill_sections[section].pack_forget()
        else:
            self.autofill_sections[section].pack(fill="x", padx=10, pady=(0,2))
        self.autofill_section_states[section] = not state

    def load_autofill(self):
        for section in ["inputFieldConfigs", "radioButtons", "dropdowns"]:
            for widget in self.autofill_sections[section].winfo_children():
                widget.destroy()
        try:
            with open(self.autofill_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for section, fields in data.items():
                for key, value in fields.items():
                    var = tk.StringVar(value=value)
                    label = ttk.Label(self.autofill_sections[section], text=key)
                    label.pack(anchor="w", padx=5, pady=(4,0))
                    entry = ttk.Entry(self.autofill_sections[section], textvariable=var, width=40)
                    entry.pack(anchor="w", padx=5, pady=(0,2))
                    if section == "inputFieldConfigs":
                        self.input_fields[key] = var
                    elif section == "radioButtons":
                        self.radio_fields[key] = var
                    elif section == "dropdowns":
                        self.dropdown_fields[key] = var
        except Exception:
            pass

    def save_autofill(self):
        data = {
            "inputFieldConfigs": {k: v.get() for k, v in self.input_fields.items()},
            "radioButtons": {k: v.get() for k, v in self.radio_fields.items()},
            "dropdowns": {k: v.get() for k, v in self.dropdown_fields.items()}
        }
        try:
            with open(self.autofill_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Autofill data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e)) 