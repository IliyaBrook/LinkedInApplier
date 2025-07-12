import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

DB_DIR = "DB"
FILTERS_FILE = os.path.join(DB_DIR, "user_filters.json")
AUTOFILL_FILE = os.path.join(DB_DIR, "form_autofill.json")
BROWSER_FILE = os.path.join(DB_DIR, "browser_settings.json")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Easy Apply Bot")
        self.is_running = False
        self.create_widgets()
        self.load_all_data()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.filters_frame = ttk.Frame(self.notebook)
        self.autofill_frame = ttk.Frame(self.notebook)
        self.browser_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.filters_frame, text="Filters")
        self.notebook.add(self.autofill_frame, text="Autofill")
        self.notebook.add(self.browser_frame, text="Browser")

        self.create_filters_tab()
        self.create_autofill_tab()
        self.create_browser_tab()

        self.start_btn = ttk.Button(self.root, text="Start", command=self.toggle_bot)
        self.start_btn.pack(pady=10)

    def create_filters_tab(self):
        self.badWords_var = tk.StringVar()
        self.titleFilterWords_var = tk.StringVar()
        self.titleSkipWords_var = tk.StringVar()

        ttk.Label(self.filters_frame, text="Bad Words (comma separated)").pack(anchor="w")
        self.badWords_entry = ttk.Entry(self.filters_frame, textvariable=self.badWords_var, width=60)
        self.badWords_entry.pack(fill="x")

        ttk.Label(self.filters_frame, text="Title Filter Words (comma separated)").pack(anchor="w")
        self.titleFilterWords_entry = ttk.Entry(self.filters_frame, textvariable=self.titleFilterWords_var, width=60)
        self.titleFilterWords_entry.pack(fill="x")

        ttk.Label(self.filters_frame, text="Title Skip Words (comma separated)").pack(anchor="w")
        self.titleSkipWords_entry = ttk.Entry(self.filters_frame, textvariable=self.titleSkipWords_var, width=60)
        self.titleSkipWords_entry.pack(fill="x")

        ttk.Button(self.filters_frame, text="Save Filters", command=self.save_filters).pack(pady=5)

    def create_autofill_tab(self):
        self.input_fields = {}
        self.radio_fields = {}
        self.dropdown_fields = {}

        self.autofill_sections = {}
        for section in ["inputFieldConfigs", "radioButtons", "dropdowns"]:
            frame = ttk.LabelFrame(self.autofill_frame, text=section)
            frame.pack(fill="x", padx=5, pady=5)
            self.autofill_sections[section] = frame

        ttk.Button(self.autofill_frame, text="Save Autofill", command=self.save_autofill).pack(pady=5)

    def create_browser_tab(self):
        self.executable_path_var = tk.StringVar()
        self.profile_path_var = tk.StringVar()

        ttk.Label(self.browser_frame, text="Executable Path").pack(anchor="w")
        path_frame = ttk.Frame(self.browser_frame)
        path_frame.pack(fill="x")
        self.executable_entry = ttk.Entry(path_frame, textvariable=self.executable_path_var, width=60)
        self.executable_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_executable).pack(side="left")

        ttk.Label(self.browser_frame, text="Profile Path").pack(anchor="w")
        profile_frame = ttk.Frame(self.browser_frame)
        profile_frame.pack(fill="x")
        self.profile_entry = ttk.Entry(profile_frame, textvariable=self.profile_path_var, width=60)
        self.profile_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(profile_frame, text="Browse", command=self.browse_profile).pack(side="left")

        ttk.Button(self.browser_frame, text="Save Browser Settings", command=self.save_browser).pack(pady=5)

    def load_all_data(self):
        self.load_filters()
        self.load_autofill()
        self.load_browser()

    def load_filters(self):
        try:
            with open(FILTERS_FILE, "r", encoding="utf-8") as f:
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
            with open(FILTERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Filters saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_autofill(self):
        for section in ["inputFieldConfigs", "radioButtons", "dropdowns"]:
            for widget in self.autofill_sections[section].winfo_children():
                widget.destroy()
        try:
            with open(AUTOFILL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for section, fields in data.items():
                for key, value in fields.items():
                    var = tk.StringVar(value=value)
                    entry = ttk.Entry(self.autofill_sections[section], textvariable=var, width=40)
                    entry.pack(anchor="w", padx=5, pady=2)
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
            with open(AUTOFILL_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Autofill data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_browser(self):
        try:
            with open(BROWSER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.executable_path_var.set(data.get("executable_path", ""))
            self.profile_path_var.set(data.get("profile_path", ""))
        except Exception:
            pass

    def save_browser(self):
        data = {
            "executable_path": self.executable_path_var.get(),
            "profile_path": self.profile_path_var.get()
        }
        try:
            with open(BROWSER_FILE, "w", encoding="utf-8") as f:
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

    def toggle_bot(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.config(text="Stop")
            # Здесь будет запуск бота
        else:
            self.start_btn.config(text="Start")
            # Здесь будет остановка бота

def main():
    root = ThemedTk(theme="arc")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main() 