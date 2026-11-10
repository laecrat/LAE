#!/usr/bin/env python3
"""
App Controller - Handles application opening and management.

On Windows it scans the real installed apps (Start Menu shortcuts for desktop
apps + Get-StartApps for UWP apps) so "open app <name>" finds what you have.
Matching is case-insensitive but prefers the exact case you typed first.
"""

import subprocess
import platform
import os
import shutil
import glob
import json
import ctypes


class AppController:
    """Controls desktop applications and programs."""

    def __init__(self):
        self.system = platform.system()
        self._app_cache = None  # list of (display_name, kind, payload)
        self.on_status = None   # optional callback(str) for live status updates
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
                "explorer": "explorer.exe",
                "control panel": "control.exe",
                "task manager": "taskmgr.exe",
                "registry": "regedit.exe",
                "disk cleanup": "cleanmgr.exe",
                "edge": "msedge.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "visual studio code": "code.exe",
                "vscode": "code.exe",
                "git bash": "git-bash.exe",
            },
            "darwin": {
                "terminal": "Terminal.app",
                "safari": "Safari.app",
                "chrome": "Google Chrome.app",
                "firefox": "Firefox.app",
                "vscode": "Visual Studio Code.app",
                "code": "Visual Studio Code.app",
                "finder": "Finder.app",
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

    def _status(self, msg):
        if self.on_status:
            try:
                self.on_status(msg)
            except Exception:
                pass

    def _shell_execute(self, target: str) -> bool:
        """Launch via Win32 ShellExecuteW — never creates a console window."""
        try:
            r = ctypes.windll.shell32.ShellExecuteW(None, "open", target, None, None, 1)
            return r > 32
        except Exception:
            return False

    # ------------------------------------------------------------------ open
    def _popen_hidden(self, cmd, shell=False):
        """Launch without flashing a console window on Windows."""
        kwargs = {"shell": shell}
        if self.system == "Windows":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE
            kwargs["startupinfo"] = si
        return subprocess.Popen(cmd, **kwargs)

    def open(self, app_name: str) -> str:
        """Open an application by name, searching installed apps on Windows."""
        name = app_name.strip()
        if not name:
            return "❌ No app name given"
        try:
            maps = self.app_mappings.get("windows" if self.system == "Windows" else
                                         ("darwin" if self.system == "Darwin" else "linux"), {})
            if name.lower() in maps:
                raw = maps[name.lower()]
                if self.system == "Windows":
                    if raw.startswith("start "):
                        kind, payload = "uri", raw[6:]
                    else:
                        kind, payload = "exe", raw
                    return self._launch_win(kind, payload, raw)
                return self._launch_unix_app(raw)

            if self.system == "Windows":
                self._status(f"🔍 Searching installed apps for '{name}'…")
                match = self.find_app(name)
                if match:
                    display, kind, payload = match
                    self._status(f"🚀 Opening {display}…")
                    ok = self._launch_win(kind, payload, display)
                    return f"✅ Opened: {display}" if ok else f"❌ Could not open: {display}"
                return f"❌ No installed app matching '{name}'"

            return self._launch_by_name(name)
        except Exception as e:
            return f"❌ Failed to open '{app_name}': {str(e)}"

    def _launch_win(self, kind: str, payload: str, display: str) -> bool:
        """Launch on Windows without any console window (ShellExecute / explorer)."""
        if kind == "lnk":
            return self._shell_execute(payload) or os.path.exists(payload) and self._shell_execute(payload)
        if kind == "uri":
            return self._shell_execute(payload)
        if kind == "exe":
            full = shutil.which(payload) or payload
            return self._shell_execute(full)
        if kind == "uwp":
            self._popen_hidden(["explorer.exe", f"shell:AppsFolder\\{payload}"], shell=False)
            return True
        return self._shell_execute(payload)

    # ------------------------------------------------------- app discovery
    def _scan_installed_apps(self):
        """Build [(display_name, shell_launch_command)] from Start Menu + UWP."""
        apps = {}
        # Desktop apps: Start Menu shortcuts (all users + current user)
        roots = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.path.expanduser("~"), r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
        ]
        for root in roots:
            for lnk in glob.glob(os.path.join(root, "**", "*.lnk"), recursive=True):
                display = os.path.splitext(os.path.basename(lnk))[0]
                apps.setdefault(display.lower(), (display, "lnk", lnk))

        # UWP / Store apps via Get-StartApps
        try:
            ps = ("Get-StartApps | Where-Object {$_.Name -and $_.AppID} | "
                  "Select-Object Name,AppID | ConvertTo-Json -Compress")
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                 capture_output=True, text=True, timeout=20)
            if out.returncode == 0 and out.stdout.strip():
                data = json.loads(out.stdout)
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    name = item.get("Name", "")
                    appid = item.get("AppID", "")
                    if name and appid:
                        apps.setdefault(name.lower(), (name, "uwp", appid))
        except Exception:
            pass
        return list(apps.values())

    def get_installed_apps(self, refresh=False):
        if self._app_cache is None or refresh:
            self._app_cache = self._scan_installed_apps()
        return self._app_cache

    def find_app(self, query: str):
        """Find an installed app using RELATIVE (substring) matching.

        Case rules:
          1. exact match of the query AS TYPED (case-sensitive) wins
          2. otherwise case-insensitive exact match
          3. otherwise relative/substring matches (query inside app name or
             app name inside query); among them prefer the one whose letters
             match the query's case most, then the shortest name.
             e.g. 'boy' -> 'boy' not 'Boy'; 'girls' -> 'Girls'; 'chrome' -> 'Google Chrome'
        Returns (display_name, launcher) or None.
        """
        q = query.strip()
        if not q:
            return None
        apps = self.get_installed_apps()
        ql = q.lower()

        def case_score(display):
            return sum(1 for a, b in zip(display, q) if a == b)

        # 1) exact case as typed
        for entry in apps:
            if entry[0] == q:
                return entry
        # 2) case-insensitive exact
        exact = [e for e in apps if e[0].lower() == ql]
        if exact:
            exact.sort(key=lambda e: (-case_score(e[0]), len(e[0])))
            return exact[0]
        # 3) relative / substring matches
        rel = [e for e in apps if ql in e[0].lower() or e[0].lower() in ql]
        if not rel:
            return None
        rel.sort(key=lambda e: (-case_score(e[0]), len(e[0])))
        return rel[0]

    # ------------------------------------------------------------- launchers
    def _launch_windows_app(self, app_path: str) -> str:
        try:
            if app_path.startswith("start "):
                self._popen_hidden(app_path, shell=True)
                return f"✅ Opened: {app_path}"
            if shutil.which(app_path):
                self._popen_hidden([app_path], shell=True)
                return f"✅ Opened: {app_path}"
            self._popen_hidden([app_path], shell=True)
            return f"✅ Opened: {app_path}"
        except Exception as e:
            return f"❌ Could not launch {app_path}: {str(e)}"

    def _launch_unix_app(self, app_path: str) -> str:
        try:
            if app_path.endswith(".app"):
                subprocess.Popen(["open", "-a", app_path])
            else:
                subprocess.Popen([app_path], shell=True)
            return f"✅ Opened: {app_path}"
        except Exception as e:
            return f"❌ Could not launch {app_path}: {str(e)}"

    def _launch_by_name(self, app_name: str) -> str:
        try:
            if self.system == "Windows":
                for base in (os.path.expandvars("%ProgramFiles%"),
                             os.path.expandvars("%ProgramFiles(x86)%"),
                             os.path.expandvars("%LOCALAPPDATA%")):
                    p = os.path.join(base, app_name, f"{app_name}.exe")
                    if os.path.exists(p):
                        self._popen_hidden([p])
                        return f"✅ Opened: {p}"
                return f"❌ Could not find app: {app_name}"
            result = subprocess.run(["which", app_name], capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.Popen([app_name], shell=True)
                return f"✅ Opened: {app_name}"
            return f"❌ Could not find app: {app_name}"
        except Exception as e:
            return f"❌ Error searching for app '{app_name}': {str(e)}"

    # ------------------------------------------------------------- utilities
    def launch_url(self, url: str) -> str:
        import webbrowser
        try:
            webbrowser.open(url)
            return f"✅ Opened URL: {url}"
        except Exception as e:
            return f"❌ Failed to open URL: {str(e)}"

    def is_running(self, app_name: str) -> bool:
        try:
            if self.system == "Windows":
                r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {app_name}"],
                                   capture_output=True, text=True)
                return app_name.lower() in r.stdout.lower()
            return subprocess.run(["pgrep", "-f", app_name], capture_output=True).returncode == 0
        except Exception:
            return False

    def get_running_apps(self) -> list:
        try:
            if self.system == "Windows":
                r = subprocess.run(["tasklist"], capture_output=True, text=True)
                return [l.split()[0] for l in r.stdout.strip().split("\n")[4:] if l.strip()]
            r = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            return [l.split()[10] for l in r.stdout.strip().split("\n")[1:] if l.strip()]
        except Exception:
            return []

    def install(self, app_name: str) -> str:
        return f"⚠️  Automatic installation is not available for '{app_name}'"
