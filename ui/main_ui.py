import json
import os
import threading
from tkinter import ttk, messagebox

from ttkthemes import ThemedTk

from browser_control.browser_manager import BrowserManager
from ui.autofill_tab import AutofillTab
from ui.browser_tab import BrowserTab
from .filters_tab import FiltersTab

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

        # Initialize UI attributes
        self.notebook = None
        self.filters_tab = None
        self.autofill_tab = None
        self.browser_tab = None
        self.open_browser_btn = None
        self.start_btn = None

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

        self.open_browser_btn = ttk.Button(
            btn_frame, text="Open Browser", command=self.toggle_browser
        )
        self.open_browser_btn.pack(side="left", padx=5)

        self.start_btn = ttk.Button(
            btn_frame,
            text="Start",
            command=self.toggle_bot,
        )
        self.start_btn.pack(side="left", padx=5)

        self.root.bind("<Configure>", self.on_window_configure)
        self.root.after(200, self.initialize_ui_layout)

    def on_window_configure(self, event):
        if (
            event.widget == self.root
            and self.filters_tab is not None
            and hasattr(self.filters_tab, "arrange_sections")
        ):
            self.root.after_idle(self.filters_tab.arrange_sections)

    def initialize_ui_layout(self):
        if self.filters_tab is not None and hasattr(
            self.filters_tab, "initialize_layout"
        ):
            self.filters_tab.initialize_layout()

    def start_browser_on_launch(self):
        thread = threading.Thread(target=self._start_browser_on_launch)
        thread.daemon = True
        thread.start()

    def _start_browser_on_launch(self):
        try:
            self.browser.start_browser()
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", f"Failed to start browser: {e}"),
            )

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
            self.root.after(
                0, lambda: messagebox.showerror("Error", f"Failed to open browser: {e}")
            )

    def on_browser_opened(self):
        self.browser_open = True
        if self.open_browser_btn is not None:
            self.open_browser_btn.config(text="Close Browser")
        if self.start_btn is not None:
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
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", f"Failed to close browser: {e}"),
            )

    def on_browser_closed(self):
        self.browser_open = False
        if self.open_browser_btn is not None:
            self.open_browser_btn.config(text="Open Browser")
        if self.start_btn is not None:
            self.start_btn.config(state="normal")
        self.is_running = False
        if self.start_btn is not None:
            self.start_btn.config(text="Start")

    def toggle_bot(self):
        if not self.is_running:
            self.is_running = True
            self.bot_should_run = True
            if self.start_btn is not None:
                self.start_btn.config(text="Stop")
            self.start_bot_thread()
        else:
            self.bot_should_run = False
            self.is_running = False
            if self.start_btn is not None:
                self.start_btn.config(text="Start")

    def start_bot_thread(self):
        thread = threading.Thread(target=self._run_bot)
        thread.daemon = True
        thread.start()

    def _run_bot(self):
        try:
            if not self.browser.driver:
                self.root.after(
                    0, lambda: messagebox.showerror("Error", "Browser is not open.")
                )
                self.is_running = False
                self.bot_should_run = False

                def reset_button():
                    if self.start_btn is not None:
                        self.start_btn.config(text="Start")

                self.root.after(0, reset_button)
                return
            current_url = self.browser.driver.current_url
            if "linkedin.com/jobs" in current_url:
                self.browser.process_job_listings(
                    AUTOFILL_FILE, FILTERS_FILE, lambda: self.bot_should_run
                )
            else:
                with open(FILTERS_FILE, "r", encoding="utf-8") as f:
                    filters = json.load(f)
                with open(AUTOFILL_FILE, "r", encoding="utf-8") as f:
                    autofill = json.load(f)
                job_title = autofill.get("textInput", {}).get("jobTitle", "")
                time_code = filters.get("timeFilter", "any")
                easy_apply_only = filters.get("easyApplyOnly", False)
                if self.filters_tab is not None:
                    job_apply_url = self.filters_tab.build_linkedin_job_url(
                        job_title, time_code, easy_apply_only
                    )
                else:
                    job_apply_url = "https://www.linkedin.com/jobs/search/"
                self.browser.go_to_url(job_apply_url)
                self.browser.process_job_listings(
                    AUTOFILL_FILE, FILTERS_FILE, lambda: self.bot_should_run
                )
            self.root.after(0, self.on_bot_stopped)
        except Exception as e:
            self.root.after(
                0, lambda: messagebox.showerror("Error", f"Failed to run bot: {e}")
            )
            self.root.after(0, self.on_bot_stopped)

    def on_bot_stopped(self):
        self.is_running = False
        self.bot_should_run = False
        if self.start_btn is not None:
            self.start_btn.config(text="Start")


def run():
    root = ThemedTk(theme="arc")
    window_width = 750
    window_height = 750

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.title("LinkedIn Easy Apply Bot")

    MainUI(root)
    root.mainloop()
