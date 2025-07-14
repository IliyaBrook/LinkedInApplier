import json
import tkinter as tk
from tkinter import ttk, messagebox


class FiltersTab:
    def __init__(self, parent, filters_file):
        self.timeFilter_combo = None
        self.easy_apply_checkbox = None
        self.easy_apply_var = None
        self.frame = ttk.Frame(parent)
        self.filters_file = filters_file
        self.timeFilter_var = tk.StringVar()
        self.badWords_entries = []
        self.titleFilterWords_entries = []
        self.titleSkipWords_entries = []
        self.job_apply_url = ""
        self.create_widgets()
        self.load_filters()
        self.update_job_apply_url()

    def create_widgets(self):

        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)

        scroll_container = ttk.Frame(main_container)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        main_canvas = tk.Canvas(scroll_container)
        scrollbar = ttk.Scrollbar(
            scroll_container, orient="vertical", command=main_canvas.yview
        )
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")),
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        filter_controls_container = ttk.Frame(scrollable_frame)
        filter_controls_container.pack(fill="x", padx=10, pady=10)

        filter_controls_frame = ttk.Frame(filter_controls_container)
        filter_controls_frame.pack(fill="x")

        easy_apply_frame = ttk.Frame(filter_controls_frame)
        easy_apply_frame.pack(side="left", padx=(0, 20))

        self.easy_apply_var = tk.BooleanVar(value=False)
        self.easy_apply_checkbox = ttk.Checkbutton(
            easy_apply_frame, text="Easy apply only", variable=self.easy_apply_var
        )
        self.easy_apply_checkbox.pack(anchor="w", pady=5)

        time_filter_frame = ttk.Frame(filter_controls_frame)
        time_filter_frame.pack(side="left")

        ttk.Label(time_filter_frame, text="Time Filter").pack(anchor="w")
        self.timeFilter_combo = ttk.Combobox(
            time_filter_frame,
            textvariable=self.timeFilter_var,
            state="readonly",
            width=20,
        )
        self.timeFilter_combo["values"] = (
            "Any Time",
            "Past 24 hours",
            "Past Week",
            "Past Month",
        )
        self.timeFilter_combo.pack(anchor="w")

        self.timeFilter_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.on_time_filter_change()
        )

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)

        filters_parent_container = ttk.Frame(scrollable_frame)
        filters_parent_container.pack(fill="both", expand=True, padx=10, pady=5)

        filters_container = ttk.Frame(filters_parent_container)
        filters_container.pack(fill="x", pady=5)

        self.create_word_list_section(filters_container, "Bad Words", "badWords")
        self.create_word_list_section(
            filters_container, "Title Filter Words", "titleFilterWords"
        )
        self.create_word_list_section(
            filters_container, "Title Skip Words", "titleSkipWords"
        )

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        button_container = ttk.Frame(main_container)
        button_container.pack(fill="x", padx=10, pady=10)

        ttk.Separator(button_container, orient="horizontal").pack(
            fill="x", pady=(0, 10)
        )

        ttk.Button(
            button_container, text="Save Filters", command=self.save_filters
        ).pack(pady=5)

        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        main_canvas.bind("<MouseWheel>", _on_mousewheel)

    def create_word_list_section(self, parent, title, field_type):
        section_frame = ttk.LabelFrame(parent, text=title, padding=10)
        section_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        list_frame = ttk.Frame(section_frame)
        list_frame.pack(fill="x")

        setattr(self, f"{field_type}_list_frame", list_frame)

        add_button = ttk.Button(
            section_frame, text="Add", command=lambda: self.add_word_entry(field_type)
        )
        add_button.pack(anchor="w", pady=(5, 0))

    def add_word_entry(self, field_type, initial_value=""):
        list_frame = getattr(self, f"{field_type}_list_frame")
        entries_list = getattr(self, f"{field_type}_entries")

        entry_frame = ttk.Frame(list_frame)
        entry_frame.pack(fill="x", pady=2)

        delete_btn = ttk.Button(
            entry_frame,
            text="Delete",
            width=8,
            command=lambda: self.remove_word_entry(field_type, entry_frame, entry_var),
        )
        delete_btn.pack(side="left", padx=(0, 5))

        entry_var = tk.StringVar(value=initial_value)
        entry = ttk.Entry(entry_frame, textvariable=entry_var)
        entry.pack(side="left", fill="x", expand=True)

        entries_list.append(entry_var)

        return entry_var

    def remove_word_entry(self, field_type, entry_frame, entry_var):
        entries_list = getattr(self, f"{field_type}_entries")
        if entry_var in entries_list:
            entries_list.remove(entry_var)
        entry_frame.destroy()

    def load_filters(self):
        try:
            with open(self.filters_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for word in data.get("badWords", []):
                if word.strip():
                    self.add_word_entry("badWords", word.strip())

            for word in data.get("titleFilterWords", []):
                if word.strip():
                    self.add_word_entry("titleFilterWords", word.strip())

            for word in data.get("titleSkipWords", []):
                if word.strip():
                    self.add_word_entry("titleSkipWords", word.strip())

            if not data.get("badWords"):
                self.add_word_entry("badWords")
            if not data.get("titleFilterWords"):
                self.add_word_entry("titleFilterWords")
            if not data.get("titleSkipWords"):
                self.add_word_entry("titleSkipWords")

            self.timeFilter_var.set(
                self.time_filter_label(data.get("timeFilter", "any"))
            )
            self.easy_apply_var.set(data.get("easyApplyOnly", False))

        except (FileNotFoundError, json.JSONDecodeError, OSError, PermissionError):
            self.add_word_entry("badWords")
            self.add_word_entry("titleFilterWords")
            self.add_word_entry("titleSkipWords")
            self.timeFilter_var.set("Any Time")
            self.easy_apply_var.set(False)

    def save_filters(self):
        data = {
            "badWords": [
                entry.get().strip()
                for entry in self.badWords_entries
                if entry.get().strip()
            ],
            "titleFilterWords": [
                entry.get().strip()
                for entry in self.titleFilterWords_entries
                if entry.get().strip()
            ],
            "titleSkipWords": [
                entry.get().strip()
                for entry in self.titleSkipWords_entries
                if entry.get().strip()
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

    @staticmethod
    def build_linkedin_job_url(job_title, time_code, easy_apply_only):
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
        if easy_apply_only:
            params.append("f_AL=true")
        return base_url + "&".join(params)

    def update_job_apply_url(self):
        try:
            with open("DB/form_autofill.json", "r", encoding="utf-8") as f:
                autofill = json.load(f)
            job_title = autofill.get("textInput", {}).get("jobTitle", "")
        except (FileNotFoundError, json.JSONDecodeError, OSError, PermissionError):
            job_title = ""
        time_code = self.time_filter_code(self.timeFilter_var.get())
        easy_apply_only = self.easy_apply_var.get()
        self.job_apply_url = self.build_linkedin_job_url(
            job_title, time_code, easy_apply_only
        )

    @staticmethod
    def time_filter_code(label):
        if label == "Past 24 hours":
            return "r86400"
        elif label == "Past Week":
            return "r604800"
        elif label == "Past Month":
            return "r2592000"
        return "any"

    @staticmethod
    def time_filter_label(code):
        if code == "r86400":
            return "Past 24 hours"
        elif code == "r604800":
            return "Past Week"
        elif code == "r2592000":
            return "Past Month"
        return "Any Time"
