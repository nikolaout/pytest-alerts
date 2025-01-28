@echo off
python -m pip install --upgrade pip build twine
python scripts/build_and_upload.py
pause
