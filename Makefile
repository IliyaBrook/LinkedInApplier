install:
	pip install -r requirements.txt
	pip install watchdog

dev:
	python run_with_reload.py
