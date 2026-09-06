@echo off
set ROOT=%~dp0
set PYTHONPATH=%ROOT%src
python -m qingyuan_os demo --output "%ROOT%outputs\demo"
