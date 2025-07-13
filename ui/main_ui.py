import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from ui.filters_tab import FiltersTab
from ui.autofill_tab import AutofillTab
from ui.browser_tab import BrowserTab
from browser_control.browser_manager import BrowserManager
import json

DB_DIR = "DB"
FILTERS_FILE = os.path.join(DB_DIR, "user_filters.json")
AUTOFILL_FILE = os.path.join(DB_DIR, "form_autofill.json")
BROWSER_FILE = os.path.join(DB_DIR, "browser_settings.json")

class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Easy Apply Bot")
        self.is_running = False
        self.bot_should_run = False
        self.browser_open = False
        self.browser = BrowserManager(BROWSER_FILE)
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.filters_tab = FiltersTab(self.notebook, FILTERS_FILE)
        self.autofill_tab = AutofillTab(self.notebook, AUTOFILL_FILE)
        self.browser_tab = BrowserTab(self.notebook, BROWSER_FILE)

        self.notebook.add(self.filters_tab.frame, text="Filters")
        self.notebook.add(self.autofill_tab.frame, text="Autofill")
        self.notebook.add(self.browser_tab.frame, text="Browser")

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.open_browser_btn = ttk.Button(btn_frame, text="Open Browser", command=self.toggle_browser)
        self.open_browser_btn.pack(side="left", padx=5)

        self.start_btn = ttk.Button(
            btn_frame, 
            text="Start", 
            command=self.toggle_bot, 
            # disable for now
            # state="disabled"
            )
        self.start_btn.pack(side="left", padx=5)

    def start_browser_on_launch(self):
        thread = threading.Thread(target=self._start_browser_on_launch)
        thread.daemon = True
        thread.start()

    def _start_browser_on_launch(self):
        try:
            self.browser.start_browser()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start browser: {e}"))

    def toggle_browser(self):
        if not self.browser_open:
            self.open_browser_thread()
        else:
            self.close_browser_thread()

    def open_browser_thread(self):
        thread = threading.Thread(target=self._open_browser)
        thread.daemon = True
        thread.start()

    def _open_browser(self):
        try:
            self.browser.start_browser()
            self.root.after(0, self.on_browser_opened)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to open browser: {e}"))

    def on_browser_opened(self):
        self.browser_open = True
        self.open_browser_btn.config(text="Close Browser")
        self.start_btn.config(state="normal")

    def close_browser_thread(self):
        thread = threading.Thread(target=self._close_browser)
        thread.daemon = True
        thread.start()

    def _close_browser(self):
        try:
            self.browser.stop()
            self.root.after(0, self.on_browser_closed)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to close browser: {e}"))

    def on_browser_closed(self):
        self.browser_open = False
        self.open_browser_btn.config(text="Open Browser")
        self.start_btn.config(
            # disable for now
            # state="disabled"
            state="normal"
            )
        self.is_running = False
        self.start_btn.config(text="Start")

    def toggle_bot(self):
        if not self.is_running:
            self.is_running = True
            self.bot_should_run = True
            self.start_btn.config(text="Stop")
            self.start_bot_thread()
        else:
            self.bot_should_run = False
            self.is_running = False
            self.start_btn.config(text="Start")

    def start_bot_thread(self):
        thread = threading.Thread(target=self._run_bot)
        thread.daemon = True
        thread.start()

    def _run_bot(self):
        try:
            if not self.browser.driver:
                self.root.after(0, lambda: messagebox.showerror("Error", "Browser is not open."))
                self.is_running = False
                self.bot_should_run = False
                self.root.after(0, lambda: self.start_btn.config(text="Start"))
                return
            current_url = self.browser.driver.current_url
            if "linkedin.com/jobs" in current_url:
                self.browser.process_job_listings(AUTOFILL_FILE, FILTERS_FILE, lambda: self.bot_should_run)
            else:
                with open(FILTERS_FILE, "r", encoding="utf-8") as f:
                    filters = json.load(f)
                with open(AUTOFILL_FILE, "r", encoding="utf-8") as f:
                    autofill = json.load(f)
                job_title = autofill.get("inputFieldConfigs", {}).get("jobTitle", "")
                time_code = filters.get("timeFilter", "any")
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
                job_apply_url = base_url + "&".join(params)
                self.browser.go_to_url(job_apply_url)
                self.browser.process_job_listings(AUTOFILL_FILE, FILTERS_FILE, lambda: self.bot_should_run)
            self.root.after(0, self.on_bot_stopped)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to run bot: {e}"))
            self.root.after(0, self.on_bot_stopped)

    def on_bot_stopped(self):
        self.is_running = False
        self.bot_should_run = False
        self.start_btn.config(text="Start")

def run():
    root = ThemedTk(theme="arc")
    app = MainUI(root)
    root.mainloop() 