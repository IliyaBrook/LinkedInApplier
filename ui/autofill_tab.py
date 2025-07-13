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
            for key, value in data.get("inputFieldConfigs", {}).items():
                var = tk.StringVar(value=value)
                label = ttk.Label(self.autofill_sections["inputFieldConfigs"], text=key)
                label.pack(anchor="w", padx=5, pady=(4,0))
                entry = ttk.Entry(self.autofill_sections["inputFieldConfigs"], textvariable=var, width=40)
                entry.pack(anchor="w", padx=5, pady=(0,2))
                self.input_fields[key] = var
            for rb in data.get("radioButtons", []):
                label_text = rb.get("placeholderIncludes", "")
                count = rb.get("count", None)
                if count is not None:
                    label_text = f"{label_text} (count: {count})"
                label = ttk.Label(self.autofill_sections["radioButtons"], text=label_text)
                label.pack(anchor="w", padx=5, pady=(8,0))
                var = tk.StringVar(value=rb.get("defaultValue", ""))
                self.radio_fields[rb.get("placeholderIncludes", "")] = var
                for opt in rb.get("options", []):
                    ttk.Radiobutton(self.autofill_sections["radioButtons"], text=opt["text"], value=opt["value"], variable=var).pack(anchor="w", padx=20)
                del_btn = ttk.Button(self.autofill_sections["radioButtons"], text="Delete", command=lambda l=rb.get("placeholderIncludes", ""): self.delete_radio(l))
                del_btn.pack(anchor="w", padx=20, pady=(0,4))
            for dd in data.get("dropdowns", []):
                label_text = dd.get("placeholderIncludes", "")
                count = dd.get("count", None)
                if count is not None:
                    label_text = f"{label_text} (count: {count})"
                label = ttk.Label(self.autofill_sections["dropdowns"], text=label_text)
                label.pack(anchor="w", padx=5, pady=(8,0))
                var = tk.StringVar(value=dd.get("defaultValue", ""))
                self.dropdown_fields[dd.get("placeholderIncludes", "")] = var
                values = [opt["text"] for opt in dd.get("options", [])]
                value_map = {opt["text"]: opt["value"] for opt in dd.get("options", [])}
                combo = ttk.Combobox(self.autofill_sections["dropdowns"], textvariable=var, values=values, state="readonly")
                combo.pack(anchor="w", padx=20)
                combo.value_map = value_map
                del_btn = ttk.Button(self.autofill_sections["dropdowns"], text="Delete", command=lambda l=dd.get("placeholderIncludes", ""): self.delete_dropdown(l))
                del_btn.pack(anchor="w", padx=20, pady=(0,4))
        except Exception:
            pass

    def save_autofill(self):
        data = {
            "inputFieldConfigs": {k: v.get() for k, v in self.input_fields.items()},
            "radioButtons": [],
            "dropdowns": []
        }
        # radioButtons
        for label, var in self.radio_fields.items():
            rb = None
            try:
                with open(self.autofill_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                for item in file_data.get("radioButtons", []):
                    if item.get("placeholderIncludes", "") == label:
                        rb = item
                        break
            except Exception:
                pass
            if rb:
                rb["defaultValue"] = var.get()
                data["radioButtons"].append(rb)
        # dropdowns
        for label, var in self.dropdown_fields.items():
            dd = None
            try:
                with open(self.autofill_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                for item in file_data.get("dropdowns", []):
                    if item.get("placeholderIncludes", "") == label:
                        dd = item
                        break
            except Exception:
                pass
            if dd:
                dd["defaultValue"] = dd["options"][[opt["text"] for opt in dd["options"]].index(var.get())]["value"] if dd["options"] else var.get()
                data["dropdowns"].append(dd)
        try:
            with open(self.autofill_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Autofill data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_radio(self, label):
        if label in self.radio_fields:
            del self.radio_fields[label]
        try:
            with open(self.autofill_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["radioButtons"] = [rb for rb in data.get("radioButtons", []) if rb.get("placeholderIncludes", "") != label]
            with open(self.autofill_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.load_autofill()
        except Exception:
            pass

    def delete_dropdown(self, label):
        if label in self.dropdown_fields:
            del self.dropdown_fields[label]
        try:
            with open(self.autofill_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["dropdowns"] = [dd for dd in data.get("dropdowns", []) if dd.get("placeholderIncludes", "") != label]
            with open(self.autofill_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.load_autofill()
        except Exception:
            pass 