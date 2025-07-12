import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from ui.filters_tab import FiltersTab
from ui.autofill_tab import AutofillTab
from ui.browser_tab import BrowserTab
from browser_control.browser_manager import BrowserManager
from browser_control.browser_manager import linkedin_url
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

        self.start_btn = ttk.Button(self.root, text="Start", command=self.toggle_bot)
        self.start_btn.pack(pady=10)

    def toggle_bot(self):
        if not self.is_running:
            self.start_browser_thread()
        else:
            self.stop_browser_thread()

    def start_browser_thread(self):
        thread = threading.Thread(target=self._start_browser)
        thread.daemon = True
        thread.start()

    def _start_browser(self):
        try:
            self.browser.start()
            self.root.after(0, self.on_browser_started)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start browser: {e}"))

    def on_browser_started(self):
        self.is_running = True
        self.start_btn.config(text="Stop")

    def stop_browser_thread(self):
        thread = threading.Thread(target=self._stop_browser)
        thread.daemon = True
        thread.start()

    def _stop_browser(self):
        try:
            self.browser.stop()
            self.root.after(0, self.on_browser_stopped)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to stop browser: {e}"))

    def on_browser_stopped(self):
        self.is_running = False
        self.start_btn.config(text="Start")

def run():
    root = ThemedTk(theme="arc")
    app = MainUI(root)
    root.mainloop() 