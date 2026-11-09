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


def _load_config():
    try:
        cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(cfg_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


DEFAULT_ENGINE = "brave"


def load_hotkey():
    """Read hotkey from config.json next to this file; fall back to default."""
    return _load_config().get("features", {}).get("hotkey", DEFAULT_HOTKEY)


def load_default_engine():
    """Default search engine from config.json (features.browser.default_engine)."""
    return _load_config().get("features", {}).get("browser", {}).get("default_engine", DEFAULT_ENGINE)


HOTKEY = load_hotkey()
DEFAULT_SEARCH_ENGINE = load_default_engine()

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

    def search_website(self, query: str, website: str = None) -> str:
        return self.browser.search(query, website or DEFAULT_SEARCH_ENGINE)

    def open_app(self, app_name: str) -> str:
        return self.app_controller.open(app_name)

    def run_command(self, command: str) -> str:
        return self.executor.run(command)

    def execute(self, action: str, target: str) -> str:
        if action == "open" and self._is_url(target):
            return self.open_website(target)
        elif action == "search":
            return self.search_website(target)
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

        # Overlay window — translucent dark panel that floats above everything
        BG = '#11111b'
        self.win = tk.Toplevel(self.root)
        self.win.title("LAE")
        self.win.geometry("460x96")
        self.win.resizable(False, False)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)   # always on top: desktop, apps, browsers
        self.win.configure(bg=BG)
        try:
            self.win.attributes("-alpha", 0.92)  # translucent so background shows through
        except tk.TclError:
            pass
        self.win.withdraw()  # start hidden

        # Open at the CENTER of the screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.win.geometry(f"460x96+{(sw - 460) // 2}+{(sh - 96) // 2}")

        self.win.bind("<Return>", self.on_enter)
        self.win.bind("<Escape>", lambda e: self.hide())
        # click anywhere outside this window -> disappear
        self.win.bind("<FocusOut>", self._on_focus_out)
        # drag the window by its title label or background (not the text box)
        self.win.bind("<ButtonPress-1>", self._start_drag)
        self.win.bind("<B1-Motion>", self._on_drag)

        frame = tk.Frame(self.win, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.title_label = tk.Label(frame, text="LAE", bg=BG, fg='#89b4fa',
                                    font=("Segoe UI", 11, "bold"))
        self.title_label.pack(anchor=tk.W, padx=10)
        self.title_label.bind("<ButtonPress-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)

        self.entry = tk.Entry(frame, font=("Segoe UI", 14), bg='#1e1e2e', fg='#cdd6f4',
                              insertbackground='#89b4fa', relief=tk.FLAT,
                              highlightthickness=2, highlightbackground='#89b4fa',
                              highlightcolor='#89b4fa')
        self.entry.pack(fill=tk.X, padx=10, pady=(4, 2))

        self.result_label = tk.Label(frame, text="", bg=BG, fg='#f9e2af',
                                     font=("Segoe UI", 9), wraplength=440, justify=tk.LEFT)
        self.result_label.pack(fill=tk.X, padx=10)

        # Live status from controllers -> shown in the window (thread-safe)
        self.lae.app_controller.on_status = lambda m: event_queue.put(("status", m))

        # Pre-warm the installed-app cache in the background so first search is instant
        threading.Thread(target=self.lae.app_controller.get_installed_apps,
                         kwargs={"refresh": True}, daemon=True).start()

        # Tray icon
        self.tray = None
        self._make_tray()

        # Poll event queue every 50ms (tkinter runs in main thread)
        self.root.after(50, self.poll_events)

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
                elif isinstance(msg, tuple) and msg[0] == "status":
                    self.result_label.config(text=msg[1], fg='#a6e3a1')
                elif msg == "hide_later":
                    self._hide_later()
        except queue.Empty:
            pass
        self.root.after(30, self.poll_events)

    def show(self):
        self.win.deiconify()
        self.win.lift()
        self.win.attributes("-topmost", True)
        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        # Robustly put the cursor in the typing bar without any click.
        # Overrideredirect windows need several delayed attempts to accept focus.
        def _focus():
            self.win.lift()
            self.win.attributes("-topmost", True)
            self.win.focus_force()
            self.entry.focus_force()
            self.entry.focus_set()
            self.entry.icursor(tk.END)
        self.win.after(0, _focus)
        self.win.after(50, _focus)
        self.win.after(150, _focus)
        self.win.after(400, _focus)

    def hide(self):
        self.win.withdraw()

    def _start_drag(self, event):
        if event.widget is self.entry:
            self._dragging = False
            return
        self._dragging = True
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        if not getattr(self, "_dragging", False):
            return
        x = self.win.winfo_x() + event.x - self._drag_x
        y = self.win.winfo_y() + event.y - self._drag_y
        self.win.geometry(f"+{x}+{y}")

    def _on_focus_out(self, event=None):
        # hide when focus truly leaves the LAE window (click outside)
        def check():
            f = self.win.focus_get()
            mine = (self.win, self.entry, self.result_label, self.title_label)
            if f not in mine:
                self.hide()
        self.win.after(150, check)

    def on_enter(self, event=None):
        cmd = self.entry.get().strip()
        if not cmd:
            return
        self.entry.delete(0, tk.END)
        # Immediate status so it never feels late, then run work off the UI thread
        self.result_label.config(text=f"⏳ {cmd}", fg='#f9e2af')
        threading.Thread(target=self._run_cmd, args=(cmd,), daemon=True).start()

    def _run_cmd(self, cmd):
        result = self.execute_command(cmd)
        event_queue.put(("status", result[:150]))
        event_queue.put("hide_later")

    def _hide_later(self):
        self.win.after(2200, self.hide)

    def execute_command(self, command: str) -> str:
        raw = command.strip()
        cmd = raw.lower()
        if "open website" in cmd or "open site" in cmd:
            url = raw.lower().replace("open website", "").replace("open site", "").strip()
            if url and "." in url and not url.startswith(("http", "www")):
                url = f"https://www.{url}"
            return self.lae.open_website(url)
        if cmd.startswith("search "):
            parts = raw.split()
            if len(parts) >= 3 and parts[1].lower() in ("on", "at", "in"):
                return self.lae.search_website(" ".join(parts[3:]), parts[2])
            return self.lae.search_website(raw.replace(parts[0], "", 1).strip())
        if cmd.startswith("open app "):
            # keep original case so app matching can prefer the case you typed
            return self.lae.open_app(raw[len("open app"):].strip())
        if cmd.startswith("open "):
            target_raw = raw[len("open"):].strip()
            target = target_raw.lower()
            if "." in target and not self.lae._is_app(target):
                if not target.startswith(("http", "www")):
                    target = f"https://www.{target}"
                return self.lae.open_website(target)
            return self.lae.open_app(target_raw)
        if cmd.startswith("run ") or cmd.startswith("execute "):
            return self.lae.run_command(raw.split(None, 1)[1].strip())
        return self.lae.run_command(raw)

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