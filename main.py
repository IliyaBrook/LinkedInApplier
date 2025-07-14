import os

from ui import run

DB_DIR = "DB"
FILTERS_FILE = os.path.join(DB_DIR, "user_filters.json")
AUTOFILL_FILE = os.path.join(DB_DIR, "form_autofill.json")
BROWSER_FILE = os.path.join(DB_DIR, "browser_settings.json")

if __name__ == "__main__":
    run()

