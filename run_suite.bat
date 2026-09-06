@echo off
set ROOT=%~dp0
set PYTHONPATH=%ROOT%src
python -m qingyuan_os suite --examples "%ROOT%examples" --output "%ROOT%outputs\reference"
