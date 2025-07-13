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
        self.timeFilter_var = tk.StringVar()
        self.job_apply_url = ""
        self.create_widgets()
        self.load_filters()
        self.update_job_apply_url()

    def create_widgets(self):
        inputMinHeight = 5
        ttk.Label(self.frame, text="Bad Words (comma separated)").pack(anchor="w")
        self.badWords_entry = tk.Text(
            self.frame, height=inputMinHeight, width=60, wrap="word"
        )
        self.badWords_entry.pack(fill="x")
        self.badWords_entry.bind(
            "<KeyRelease>", lambda e: self._auto_resize(self.badWords_entry)
        )

        ttk.Label(self.frame, text="Title Filter Words (comma separated)").pack(
            anchor="w"
        )
        self.titleFilterWords_entry = tk.Text(
            self.frame, height=inputMinHeight, width=60, wrap="word"
        )
        self.titleFilterWords_entry.pack(fill="x")
        self.titleFilterWords_entry.bind(
            "<KeyRelease>", lambda e: self._auto_resize(self.titleFilterWords_entry)
        )

        ttk.Label(self.frame, text="Title Skip Words (comma separated)").pack(
            anchor="w"
        )
        self.titleSkipWords_entry = tk.Text(
            self.frame, height=inputMinHeight, width=60, wrap="word"
        )
        self.titleSkipWords_entry.pack(fill="x")
        self.titleSkipWords_entry.bind(
            "<KeyRelease>", lambda e: self._auto_resize(self.titleSkipWords_entry)
        )

        ttk.Label(self.frame, text="Time Filter").pack(anchor="w")
        self.timeFilter_combo = ttk.Combobox(
            self.frame, textvariable=self.timeFilter_var, state="readonly", width=30
        )
        self.timeFilter_combo["values"] = (
            "Any Time",
            "Past 24 hours",
            "Past Week",
            "Past Month",
        )
        self.timeFilter_combo.pack(fill="x")
        self.timeFilter_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.on_time_filter_change()
        )

        self.easy_apply_var = tk.BooleanVar(value=False)
        self.easy_apply_checkbox = ttk.Checkbutton(
            self.frame, text="Easy apply only", variable=self.easy_apply_var
        )
        self.easy_apply_checkbox.pack(anchor="w", pady=5)

        ttk.Button(self.frame, text="Save Filters", command=self.save_filters).pack(
            pady=5
        )

    def _auto_resize(self, text_widget):
        lines = int(text_widget.index("end-1c").split(".")[0])
        text_widget.config(height=max(4, min(lines, 10)))

    def load_filters(self):
        try:
            with open(self.filters_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.badWords_entry.delete("1.0", tk.END)
            self.badWords_entry.insert("1.0", ", ".join(data.get("badWords", [])))
            self.titleFilterWords_entry.delete("1.0", tk.END)
            self.titleFilterWords_entry.insert(
                "1.0", ", ".join(data.get("titleFilterWords", []))
            )
            self.titleSkipWords_entry.delete("1.0", tk.END)
            self.titleSkipWords_entry.insert(
                "1.0", ", ".join(data.get("titleSkipWords", []))
            )
            self.timeFilter_var.set(
                self.time_filter_label(data.get("timeFilter", "any"))
            )
            self.easy_apply_var.set(data.get("easyApplyOnly", False))
        except Exception:
            self.timeFilter_var.set("Any Time")
            self.easy_apply_var.set(False)

    def save_filters(self):
        data = {
            "badWords": [
                w.strip()
                for w in self.badWords_entry.get("1.0", tk.END).split(",")
                if w.strip()
            ],
            "titleFilterWords": [
                w.strip()
                for w in self.titleFilterWords_entry.get("1.0", tk.END).split(",")
                if w.strip()
            ],
            "titleSkipWords": [
                w.strip()
                for w in self.titleSkipWords_entry.get("1.0", tk.END).split(",")
                if w.strip()
            ],
            "timeFilter": self.time_filter_code(self.timeFilter_var.get()),
            "easyApplyOnly": self.easy_apply_var.get(),
        }
        try:
            with open(self.filters_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.update_job_apply_url()
            messagebox.showinfo("Success", "Filters saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_time_filter_change(self):
        self.save_filters()

    def update_job_apply_url(self):
        try:
            with open("DB/form_autofill.json", "r", encoding="utf-8") as f:
                autofill = json.load(f)
            job_title = autofill.get("textInput", {}).get("jobTitle", "")
        except Exception:
            job_title = ""
        time_code = self.time_filter_code(self.timeFilter_var.get())
        base_url = "https://www.linkedin.com/jobs/search/?"
        params = []
        if job_title:
            params.append(f"keywords={job_title.replace(' ', '%20')}")
        if time_code == "r86400":
            params.append("f_TPR=r86400")
        elif time_code == "r604800":
            params.append("f_TPR=r604800")
        elif time_code == "r2592000":
            params.append("f_TPR=r2592000")
        if self.easy_apply_var.get():
            params.append("f_AL=true")
        url = base_url + "&".join(params)
        self.job_apply_url = url

    def time_filter_code(self, label):
        if label == "Past 24 hours":
            return "r86400"
        elif label == "Past Week":
            return "r604800"
        elif label == "Past Month":
            return "r2592000"
        return "any"

    def time_filter_label(self, code):
        if code == "r86400":
            return "Past 24 hours"
        elif code == "r604800":
            return "Past Week"
        elif code == "r2592000":
            return "Past Month"
        return "Any Time"
