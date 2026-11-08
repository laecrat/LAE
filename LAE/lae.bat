@echo off
REM LAE Launcher - starts LAE in background (no console window)
REM Double-click this file or a desktop shortcut to it
cd /d "%~dp0"
start "" /min pythonw.exe main.py --bg
