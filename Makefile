install:
	pip install -r requirements.txt
	pip install watchdog

dev:
	# python run_with_reload.py
	debugpy --listen 5678 run_with_reload.py

format:
	black .
