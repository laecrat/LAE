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
import time
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
        # route to search_website (handles both sites and engines via resolve_site)
        return self.browser.search_website(query, website or DEFAULT_SEARCH_ENGINE)

    def open_app(self, app_name: str) -> str:
        return self.app_controller.open(app_name)

    def run_command(self, command: str) -> str:
        return self.executor.run(command)

    def execute(self, action: str, target: str) -> str:
        power_actions = {"lock", "l", "sleep", "s", "signout", "o", "logoff", "shutdown", "d", "restart", "reboot", "hibernate", "h", "r"}
        if action.lower() in power_actions:
            return self.executor.power_command(action)
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

        # Overlay window — white liquid-glass CAPSULE, only "LAE" on the left
        W, H = 430, 88
        FILL = '#ffffff'           # white glass body
        INK = '#1a1a2e'            # text on white glass
        self.win = tk.Toplevel(self.root)
        self.win.title("LAE")
        self.win.geometry(f"{W}x{H}")
        self.win.resizable(False, False)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)   # always on top: desktop, apps, browsers
        self.win.configure(bg='#000000')
        try:
            self.win.attributes("-alpha", 0.55)                 # liquid-glass translucency
            self.win.attributes("-transparentcolor", '#000000')  # corners cut out -> capsule
        except tk.TclError:
            pass
        self.win.withdraw()  # start hidden

        # Open at the CENTER of the screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.win.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        self.win.bind("<Return>", self.on_enter)
        self.win.bind("<Escape>", lambda e: self.hide())
        self.win.bind("<FocusOut>", self._on_focus_out)          # click outside -> hide
        self.win.bind("<ButtonPress-1>", self._start_drag)       # drag the capsule
        self.win.bind("<B1-Motion>", self._on_drag)

        # Single clean pill (left+right arcs + middle rect), all same fill, no seams
        self.canvas = tk.Canvas(self.win, width=W, height=H, bg='#000000', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        r = H // 2
        self.canvas.create_oval(1, 1, 1 + 2 * r, H - 1, fill=FILL, outline=FILL)
        self.canvas.create_rectangle(r, 1, W - r, H - 1, fill=FILL, outline=FILL)
        self.canvas.create_oval(W - 1 - 2 * r, 1, W - 1, H - 1, fill=FILL, outline=FILL)
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # Only "LAE" on the left of the top row
        self.title_label = tk.Label(self.win, text="LAE", bg=FILL, fg=INK,
                                    font=("Segoe UI", 14, "bold"))
        self.canvas.create_window(24, 26, window=self.title_label, anchor='w')
        self.title_label.bind("<ButtonPress-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)

        # Typing bar fills the rest of the top row (status no longer overlaps it)
        self.entry = tk.Entry(self.win, font=("Segoe UI", 14), bg=FILL, fg=INK,
                              insertbackground=INK, relief=tk.FLAT,
                              highlightthickness=0, borderwidth=0)
        self.canvas.create_window(84, 26, window=self.entry, anchor='w',
                                  width=W - 104, height=30)

        # status on its own row at the bottom of the capsule, left-aligned
        self.result_label = tk.Label(self.win, text="", bg=FILL, fg='#666688',
                                     font=("Segoe UI", 9), anchor='w')
        self.canvas.create_window(24, 62, window=self.result_label, anchor='nw',
                                  width=W - 48)

        # Small ✕ close button at the top-right corner
        self.close_btn = tk.Label(self.win, text="✕", bg=FILL, fg=INK,
                                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                                  width=2, height=1)
        self.canvas.create_window(W - 6, 4, window=self.close_btn, anchor='ne')
        self.close_btn.bind("<Button-1>", lambda e: self.hide())

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

    def _draw_polyhedron(self, c):
        """Wireframe 3D polyhedron logo (the shape from the image) on a canvas."""
        c.delete("all")
        outer = [(15, 2), (27, 10), (23, 27), (7, 27), (3, 10)]
        inner = [(15, 8), (22, 12), (20, 22), (10, 22), (8, 12)]
        for p in (outer, inner):
            for i in range(5):
                x1, y1 = p[i]
                x2, y2 = p[(i + 1) % 5]
                c.create_line(x1, y1, x2, y2, fill='#cdd6f4', width=1)
        for o, i in zip(outer, inner):
            c.create_line(o[0], o[1], i[0], i[1], fill='#89b4fa', width=1)

    def _make_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (64, 64), color=(17, 17, 27))
            dc = ImageDraw.Draw(img)
            dc.rounded_rectangle([4, 4, 60, 60], radius=16, fill=(28, 28, 40), outline=(90, 90, 140))
            s = 2  # scale 30->60
            outer = [(15 * s - 15, 2 * s - 2), (27 * s - 15, 10 * s - 2), (23 * s - 15, 27 * s - 2),
                     (7 * s - 15, 27 * s - 2), (3 * s - 15, 10 * s - 2)]
            inner = [(15 * s - 15, 8 * s - 2), (22 * s - 15, 12 * s - 2), (20 * s - 15, 22 * s - 2),
                     (10 * s - 15, 22 * s - 2), (8 * s - 15, 12 * s - 2)]
            for p in (outer, inner):
                dc.line(p + [p[0]], fill=(205, 214, 244), width=2)
            for o, i in zip(outer, inner):
                dc.line([o, i], fill=(137, 180, 250), width=2)

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
        self._shown_at = time.time()
        self.win.deiconify()
        self.win.lift()
        self.win.attributes("-topmost", True)
        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        self._focus_entry()

    def _focus_entry(self):
        """Put keyboard focus into the entry without any click, without flicker.
        Toggling overrideredirect makes Windows redraw the frame (visible flicker),
        so instead we call SetForegroundWindow on the raw HWND — this works on
        borderless windows and doesn't repaint them."""
        if getattr(self, "_focusing", False):
            return
        self._focusing = True
        def grab():
            try:
                # Bring the borderless window to the foreground via Win32
                try:
                    hwnd = int(self.win.frame(), 16)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass
                self.win.lift()
                self.win.attributes("-topmost", True)
                self.win.focus_force()
                self.entry.focus_force()
                self.entry.icursor(tk.END)
            except tk.TclError:
                pass
            finally:
                self._focusing = False
        for d in (0, 30, 80, 200, 400):
            self.win.after(d, grab)

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
        # hide when focus truly leaves the LAE window (click outside).
        # Ignore the focus flurry right after showing (first ~0.8s) so the
        # window isn't hidden before our focus_force attempts land.
        def check():
            if time.time() - getattr(self, "_shown_at", 0) < 0.8:
                return
            f = self.win.focus_get()
            mine = (self.win, self.entry, self.result_label, self.title_label, self.close_btn)
            if f not in mine:
                self.hide()
        self.win.after(200, check)

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
        # Helium-style bangs: !yt <query>, !g <query>, !pin <query> ...
        if raw.startswith("!"):
            parts = raw.split(None, 1)
            bang = parts[0][1:]
            query = parts[1] if len(parts) > 1 else ""
            return self.lae.browser.bang_search(bang, query)
        if "open website" in cmd or "open site" in cmd:
            url = raw.lower().replace("open website", "").replace("open site", "").strip()
            if url and "." in url and not url.startswith(("http", "www")):
                url = f"https://www.{url}"
            return self.lae.open_website(url)
        if cmd.startswith("search "):
            parts = raw.split()
            # "search on/at/in <site> <query>"  OR  "search <site> <query>"
            if len(parts) >= 3 and parts[1].lower() in ("on", "at", "in"):
                return self.lae.search_website(" ".join(parts[3:]), parts[2])
            if len(parts) >= 3 and self.lae.browser.resolve_site(parts[1])[1] is not None:
                return self.lae.search_website(" ".join(parts[2:]), parts[1])
            # plain web search on default engine
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
        # Power management commands: lock/L, sleep/S, signout/O, shutdown/D
        power_map = {
            "lock": "lock", "l": "lock",
            "sleep": "sleep", "s": "sleep",
            "signout": "signout", "logoff": "signout", "o": "signout",
            "shutdown": "shutdown", "d": "shutdown",
            "restart": "restart", "reboot": "restart", "r": "restart",
            "hibernate": "hibernate", "h": "hibernate",
        }
        if cmd in power_map:
            return self.lae.executor.power_command(power_map[cmd])
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
    parser.add_argument("action", nargs="?", choices=["open", "search", "run", "execute", "lock", "sleep", "signout", "shutdown", "restart", "hibernate", "l", "s", "o", "d", "h", "r"])
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