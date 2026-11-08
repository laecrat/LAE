#!/usr/bin/env python3
"""
LAE - AI Assistant
An AI assistant that can open websites, apps and run programs as instructed.
"""

import sys
import os
import json
import argparse
import threading
import queue
import ctypes
import tkinter as tk
import keyboard
from browser_controller import BrowserController
from app_controller import AppController
from command_executor import CommandExecutor

DEFAULT_HOTKEY = 'win+`'


def load_hotkey():
    """Read hotkey from config.json next to this file; fall back to default."""
    try:
        cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(cfg_path, encoding="utf-8") as f:
            return json.load(f).get("features", {}).get("hotkey", DEFAULT_HOTKEY)
    except Exception:
        return DEFAULT_HOTKEY


HOTKEY = load_hotkey()

# Thread-safe queue: hotkey/tray callbacks put messages here, tkinter mainloop reads them
event_queue = queue.Queue()


def is_admin():
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class LAE:
    """Main AI Assistant class that orchestrates all actions."""

    def __init__(self):
        self.browser = BrowserController()
        self.app_controller = AppController()
        self.executor = CommandExecutor()

    def open_website(self, url: str) -> str:
        return self.browser.open(url)

    def search_website(self, query: str, website: str = "duckduckgo") -> str:
        return self.browser.search(query, website)

    def open_app(self, app_name: str) -> str:
        return self.app_controller.open(app_name)

    def run_command(self, command: str) -> str:
        return self.executor.run(command)

    def execute(self, action: str, target: str) -> str:
        if action == "open" and self._is_url(target):
            return self.open_website(target)
        elif action == "search":
            return self.search_website(target, "duckduckgo")
        elif action == "run" and self._is_app(target):
            return self.open_app(target)
        elif action in ("execute", "run"):
            return self.run_command(target)
        else:
            return f"Unknown action '{action}' or target '{target}'"

    def _is_url(self, target: str) -> bool:
        return target.startswith(("http://", "https://", "www."))

    def _is_app(self, target: str) -> bool:
        known_apps = ["chrome", "firefox", "edge", "notepad", "calc", "powershell", "cmd", "terminal", "code"]
        return any(app in target.lower() for app in known_apps)


class LAEApp:
    """Tkinter application that owns the overlay window and tray icon."""

    def __init__(self, lae_instance):
        self.lae = lae_instance
        self.root = tk.Tk()
        self.root.withdraw()  # hidden until activated

        # Overlay window (created once, shown/hidden)
        self.win = tk.Toplevel(self.root)
        self.win.title("LAE")
        self.win.geometry("420x140")
        self.win.resizable(False, False)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg='#1e1e2e')
        self.win.withdraw()  # start hidden

        # Position top-center
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        self.win.geometry(f"420x140+{(sw - 420) // 2}+80")

        self.win.bind("<Return>", self.on_enter)
        self.win.bind("<Escape>", lambda e: self.hide())

        frame = tk.Frame(self.win, bg='#1e1e2e', padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="LAE Assistant", bg='#1e1e2e', fg='#89b4fa',
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)

        self.entry = tk.Entry(frame, font=("Segoe UI", 13), bg='#313244', fg='#cdd6f4',
                              insertbackground='#cdd6f4', relief=tk.FLAT,
                              highlightthickness=2, highlightbackground='#89b4fa')
        self.entry.pack(fill=tk.X, pady=(8, 4))

        self.result_label = tk.Label(frame, text="", bg='#1e1e2e', fg='#a6e3a1',
                                     font=("Segoe UI", 9), wraplength=390, justify=tk.LEFT)
        self.result_label.pack(fill=tk.X)

        tk.Label(frame, text=f"Enter = run | Esc = hide | Hotkey: {HOTKEY.upper()}",
                 bg='#1e1e2e', fg='#6c7086', font=("Segoe UI", 8)).pack(anchor=tk.W, pady=(4, 0))

        # Tray icon
        self.tray = None
        self._make_tray()

        # Poll event queue every 100ms (tkinter runs in main thread)
        self.root.after(100, self.poll_events)

    def _make_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (64, 64), color='#89b4fa')
            dc = ImageDraw.Draw(img)
            dc.rectangle([16, 16, 48, 48], fill='#1e1e2e')
            dc.text((24, 24), "L", fill='#cdd6f4')

            def on_open(icon, item):
                event_queue.put("show")

            def on_quit(icon, item):
                event_queue.put("quit")

            menu = pystray.Menu(
                pystray.MenuItem(f"Open LAE ({HOTKEY.upper()})", on_open, default=True),
                pystray.MenuItem("Quit", on_quit)
            )
            self.tray = pystray.Icon("LAE", img, "LAE Assistant (Ctrl+Alt+L)", menu)
            threading.Thread(target=self.tray.run, daemon=True).start()
        except Exception as e:
            print(f"[WARN] Tray icon failed: {e}")

    def poll_events(self):
        """Process events from hotkey/tray threads. Runs in tkinter main thread."""
        try:
            while True:
                msg = event_queue.get_nowait()
                if msg == "show":
                    self.show()
                elif msg == "quit":
                    self.quit()
        except queue.Empty:
            pass
        self.root.after(100, self.poll_events)

    def show(self):
        self.win.deiconify()
        self.win.lift()
        self.win.attributes("-topmost", True)
        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.entry.focus_force()

    def hide(self):
        self.win.withdraw()

    def on_enter(self, event=None):
        cmd = self.entry.get().strip()
        if not cmd:
            return
        result = self.execute_command(cmd)
        self.result_label.config(text=result[:150])
        self.entry.delete(0, tk.END)
        self.win.after(2500, self.hide)

    def execute_command(self, command: str) -> str:
        cmd = command.lower().strip()
        if "open website" in cmd or "open site" in cmd:
            url = cmd.replace("open website", "").replace("open site", "").strip()
            if url and "." in url and not url.startswith(("http", "www")):
                url = f"https://www.{url}"
            return self.lae.open_website(url)
        if cmd.startswith("search "):
            parts = cmd.split()
            if len(parts) >= 3 and parts[1] in ("on", "at", "in"):
                return self.lae.search_website(" ".join(parts[3:]), parts[2])
            return self.lae.search_website(cmd.replace("search", "").strip(), "duckduckgo")
        if cmd.startswith("open app "):
            return self.lae.open_app(cmd.replace("open app", "").strip())
        if cmd.startswith("open "):
            target = cmd.replace("open", "").strip()
            if "." in target and not self.lae._is_app(target):
                if not target.startswith(("http", "www")):
                    target = f"https://www.{target}"
                return self.lae.open_website(target)
            return self.lae.open_app(target)
        if cmd.startswith("run ") or cmd.startswith("execute "):
            return self.lae.run_command(cmd.replace("run", "").replace("execute", "").strip())
        return self.lae.run_command(cmd)

    def quit(self):
        keyboard.unhook_all()
        if self.tray:
            self.tray.stop()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="LAE - AI Assistant")
    parser.add_argument("action", nargs="?", choices=["open", "search", "run", "execute"])
    parser.add_argument("target", nargs="?")
    parser.add_argument("--hotkey", "-k", action="store_true",
                        help=f"Run hotkey overlay + tray ({HOTKEY.upper()})")
    parser.add_argument("--window", "-w", action="store_true",
                        help="Show always-visible mini window")
    parser.add_argument("--bg", action="store_true",
                        help="Background mode: tray icon + hotkey, window hidden (for pythonw/no-console)")

    args = parser.parse_args()
    lae = LAE()

    if args.action and args.target:
        print(lae.execute(args.action, args.target))
        return 0

    admin = is_admin()
    print("=" * 55)
    print("LAE AI Assistant")
    print("=" * 55)
    print(f"Admin mode: {'YES' if admin else 'NO (hotkey may fail - run as Admin)'}")
    print(f"Hotkey: {HOTKEY.upper()}")
    print("Tray icon: bottom-right of taskbar, double-click to open")
    print("Ctrl+C to quit")
    print("=" * 55 + "\n")

    app = LAEApp(lae)

    # Register global hotkey -> just puts event in queue (thread-safe)
    def on_hotkey():
        event_queue.put("show")

    try:
        keyboard.add_hotkey(HOTKEY, on_hotkey)
        print(f"[OK] Hotkey '{HOTKEY}' registered")
    except Exception as e:
        print(f"[FAIL] Hotkey registration failed: {e}")

    if args.window:
        app.show()  # visible window mode

    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())