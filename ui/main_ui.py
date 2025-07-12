import os
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from ui.filters_tab import FiltersTab
from ui.autofill_tab import AutofillTab
from ui.browser_tab import BrowserTab

DB_DIR = "DB"
FILTERS_FILE = os.path.join(DB_DIR, "user_filters.json")
AUTOFILL_FILE = os.path.join(DB_DIR, "form_autofill.json")
BROWSER_FILE = os.path.join(DB_DIR, "browser_settings.json")

class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Easy Apply Bot")
        self.is_running = False
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
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.config(text="Stop")
            # Здесь будет запуск бота
        else:
            self.start_btn.config(text="Start")
            # Здесь будет остановка бота

def run():
    root = ThemedTk(theme="arc")
    app = MainUI(root)
    root.mainloop() 