#!/usr/bin/env python3
"""
App Controller - Handles application opening and management.
"""

import subprocess
import platform
import os
import shutil


class AppController:
    """Controls desktop applications and programs."""

    def __init__(self):
        self.system = platform.system()
        self.apps_folder = os.path.expanduser("~/AppData/Local") if self.system == "Windows" else "/Applications"

        # Known application mappings
        self.app_mappings = {
            "windows": {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "powershell": "powershell.exe",
                "cmd": "cmd.exe",
                "terminal": "cmd.exe",
                "command prompt": "cmd.exe",
                "settings": "start ms-settings:",
                "file explorer": "explorer.exe",
                "control panel": "control.exe",
                "task manager": "taskmgr.exe",
                "registry": "regedit.exe",
                "disk cleanup": "cleanmgr.exe",
                "defender": "windowsdefender://",
                "edge": "msedge.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "visual studio code": "code.exe",
                "vscode": "code.exe",
                "git bash": "git-bash.exe",
                "github": "GitHub Desktop.exe",
            },
            "darwin": {  # macOS
                "terminal": "Terminal.app",
                "safari": "Safari.app",
                "chrome": "Google Chrome.app",
                "firefox": "Firefox.app",
                "vscode": "Visual Studio Code.app",
                "code": "Visual Studio Code.app",
                "sublime": "Sublime Text.app",
                "finder": "Finder.app",
                "safari": "Safari.app",
            },
            "linux": {
                "terminal": "gnome-terminal",
                "konsole": "konsole",
                "firefox": "firefox",
                "chrome": "google-chrome",
                "code": "code",
                "vscode": "code",
            }
        }

    def open(self, app_name: str) -> str:
        """Open an application by name."""
        try:
            app_name_lower = app_name.lower().strip()

            # Get system-specific app mappings
            if self.system == "Windows":
                apps = self.app_mappings["windows"]
            elif self.system == "Darwin":
                apps = self.app_mappings["darwin"]
            else:
                apps = self.app_mappings["linux"]

            # Check if it's a known app
            if app_name_lower in apps:
                app_exe = apps[app_name_lower]
                return self._launch_windows_app(app_exe) if self.system == "Windows" else self._launch_unix_app(app_exe)

            # Try to find the app
            return self._launch_by_name(app_name)

        except Exception as e:
            return f"❌ Failed to open '{app_name}': {str(e)}"

    def _launch_windows_app(self, app_path: str) -> str:
        """Launch an app on Windows."""
        try:
            # Check if it's a special Windows command
            if app_path.startswith("start "):
                subprocess.Popen(app_path, shell=True)
                return f"✅ Opened: {app_path}"

            # Try to find the executable in PATH
            if shutil.which(app_path):
                subprocess.Popen([app_path], shell=True)
                return f"✅ Opened: {app_path}"

            # Try to run it directly (Windows will find it)
            subprocess.Popen([app_path], shell=True)
            return f"✅ Opened: {app_path}"

        except Exception as e:
            return f"❌ Could not launch {app_path}: {str(e)}"

    def _launch_unix_app(self, app_path: str) -> str:
        """Launch an app on macOS or Linux."""
        try:
            if app_path.endswith(".app"):
                # macOS .app bundle
                subprocess.Popen(["open", "-a", app_path])
                return f"✅ Opened: {app_path}"
            else:
                # Unix executable
                subprocess.Popen([app_path], shell=True)
                return f"✅ Opened: {app_path}"
        except Exception as e:
            return f"❌ Could not launch {app_path}: {str(e)}"

    def _launch_by_name(self, app_name: str) -> str:
        """Try to launch an app by searching for it."""
        try:
            if self.system == "Windows":
                # Try common Windows locations
                possible_paths = [
                    os.path.expandvars(f"%ProgramFiles%\\{app_name}\\{app_name}.exe"),
                    os.path.expandvars(f"%ProgramFiles(x86)%\\{app_name}\\{app_name}.exe"),
                    os.path.expandvars(f"%LOCALAPPDATA%\\{app_name}\\{app_name}.exe"),
                ]

                # Also try with common prefixes
                prefixes = ["", "Google ", "Microsoft "]
                for prefix in prefixes:
                    for path in possible_paths:
                        modified_path = path.replace(app_name, f"{prefix}{app_name}")
                        if os.path.exists(modified_path):
                            subprocess.Popen([modified_path])
                            return f"✅ Opened: {modified_path}"

                return f"❌ Could not find app: {app_name}"
            else:
                # Try using 'open' on macOS or 'which' on Linux
                result = subprocess.run(["which", app_name], capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.Popen([app_name], shell=True)
                    return f"✅ Opened: {app_name}"

                return f"❌ Could not find app: {app_name}"

        except Exception as e:
            return f"❌ Error searching for app '{app_name}': {str(e)}"

    def launch_url(self, url: str) -> str:
        """Open a URL as if it were an app."""
        import webbrowser
        try:
            webbrowser.open(url)
            return f"✅ Opened URL: {url}"
        except Exception as e:
            return f"❌ Failed to open URL: {str(e)}"

    def is_running(self, app_name: str) -> bool:
        """Check if an app is currently running."""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {app_name}"],
                    capture_output=True,
                    text=True
                )
                return app_name.lower() in result.stdout.lower()
            else:
                result = subprocess.run(["pgrep", "-f", app_name], capture_output=True)
                return result.returncode == 0
        except:
            return False

    def get_running_apps(self) -> list:
        """Get list of running applications."""
        try:
            if self.system == "Windows":
                result = subprocess.run(["tasklist"], capture_output=True, text=True)
                lines = result.stdout.strip().split("\n")[4:]  # Skip header
                return [line.split()[0] for line in lines if line.strip()]
            else:
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
                lines = result.stdout.strip().split("\n")[1:]
                return [line.split()[10] for line in lines if line.strip()]
        except:
            return []

    def install(self, app_name: str) -> str:
        """Install an application (if possible)."""
        return f"⚠️  Automatic installation is not available for '{app_name}'"