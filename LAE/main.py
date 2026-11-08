#!/usr/bin/env python3
"""
LAE - AI Assistant
An AI assistant that can open websites, apps and run programs as instructed.
"""

import sys
import argparse
import threading
import keyboard
import tkinter as tk
from tkinter import ttk, messagebox
from browser_controller import BrowserController
from app_controller import AppController
from command_executor import CommandExecutor


class LAE:
    """Main AI Assistant class that orchestrates all actions."""

    def __init__(self):
        self.browser = BrowserController()
        self.app_controller = AppController()
        self.executor = CommandExecutor()

    def open_website(self, url: str) -> str:
        """Open a website in the default browser."""
        return self.browser.open(url)

    def search_website(self, query: str, website: str = "google") -> str:
        """Search on a specific website."""
        return self.browser.search(query, website)

    def open_app(self, app_name: str) -> str:
        """Open an application."""
        return self.app_controller.open(app_name)

    def run_command(self, command: str) -> str:
        """Run a system command."""
        return self.executor.run(command)

    def execute(self, action: str, target: str) -> str:
        """Execute an action on a target."""
        if action == "open" and self._is_url(target):
            return self.open_website(target)
        elif action == "search" and self._is_website(target):
            return self.search_website(target, "duckduckgo")
        elif action == "run" and self._is_app(target):
            return self.open_app(target)
        elif action == "execute" or action == "run":
            return self.run_command(target)
        else:
            return f"Unknown action '{action}' or target '{target}'"

    def _is_url(self, target: str) -> bool:
        """Check if target is a URL."""
        return target.startswith(("http://", "https://", "www."))

    def _is_website(self, target: str) -> bool:
        """Check if target is a website name."""
        return not self._is_url(target) and "." in target

    def _is_app(self, target: str) -> bool:
        """Check if target is an application."""
        known_apps = ["chrome", "firefox", "edge", "notepad", "calc", "powershell", "cmd", "terminal", "code"]
        return any(app in target.lower() for app in known_apps)


class LAEOverlayWindow:
    """Small overlay window for LAE commands (like Bixby)."""

    def __init__(self, lae_instance):
        self.lae = lae_instance
        self.root = None
        self.entry = None
        self.result_label = None
        self.is_visible = False

    def create_window(self):
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("LAE")
        self.root.geometry("400x150+100+100")
        self.root.resizable(False, False)

        # Remove window decorations (title bar)
        self.root.overrideredirect(True)

        # Make window always on top
        self.root.attributes("-topmost", True)

        # Set window transparency (slight)
        # self.root.attributes("-alpha", 0.95)

        # Style the window
        self.root.configure(bg='#2c2c2c')
        self.root.bind("<Return>", self.process_command)
        self.root.bind("<Escape>", self.hide_window)
        self.root.bind("<FocusOut>", self.auto_hide)

        # Create input frame
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True)

        # Create entry widget
        self.entry = ttk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            width=40
        )
        self.entry.pack(fill=tk.X)
        self.entry.focus_set()

        # Create result label
        self.result_label = ttk.Label(
            input_frame,
            text="",
            font=("Segoe UI", 9),
            foreground="white",
            background="#2c2c2c"
        )
        self.result_label.pack(fill=tk.X, pady=(5, 0))

        # Bind escape to hide
        self.root.bind("<Alt_L>", self._on_alt_press)

    def show_window(self):
        """Show the overlay window."""
        if not self.is_visible:
            self.create_window()
            self.is_visible = True
            self.root.deiconify()
            self.entry.delete(0, tk.END)
            self.entry.focus_set()

    def hide_window(self, event=None):
        """Hide the overlay window."""
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False

    def _on_alt_press(self, event):
        """Handle Alt key press to prevent hiding while holding."""
        pass

    def auto_hide(self, event):
        """Auto-hide window after a short delay."""
        self.root.after(2000, self.hide_window)

    def process_command(self, event=None):
        """Process the typed command."""
        command = self.entry.get().strip()
        if not command:
            return

        result = self.execute_command(command)
        self.result_label.config(text=result)

        # Clear input after processing
        self.entry.delete(0, tk.END)

        # Hide after showing result
        self.root.after(2000, self.hide_window)

    def execute_command(self, command: str) -> str:
        """Parse and execute a natural language command."""
        command = command.lower().strip()

        # Parse different command types

        # "open website google"
        if "open website" in command or "open site" in command:
            url = command.replace("open website", "").replace("open site", "").strip()
            if not url.startswith(("http://", "https://", "www.")):
                url = f"https://www.{url}"
            return self.lae.open_website(url)

        # "open chrome" or "open app chrome"
        if "open" in command:
            if "app" in command:
                app = command.replace("open app", "").strip()
            else:
                app = command.replace("open", "").strip()
            return self.lae.open_app(app)

        # "search python tutorials"
        if command.startswith("search "):
            query = command.replace("search", "").strip()
            return self.lae.search_website(query, "duckduckgo")

        # "search github claude code"
        if command.startswith("search "):
            parts = command.split()
            if len(parts) >= 3 and parts[1] in ["on", "at", "in"]:
                site = parts[2]
                query = " ".join(parts[3:]) if len(parts) > 3 else " ".join(parts[1:])
                return self.lae.search_website(query, site)
            else:
                query = command.replace("search", "").strip()
                return self.lae.search_website(query, "duckduckgo")

        # "run ls" or "execute ls"
        if command.startswith("run ") or command.startswith("execute "):
            cmd = command.replace("run", "").replace("execute", "").strip()
            return self.lae.run_command(cmd)

        # Plain command
        return self.lae.run_command(command)

    def run(self):
        """Run the overlay window mainloop."""
        if self.root:
            self.root.mainloop()


def hotkey_handler():
    """Handler for Alt+Space hotkey."""
    global overlay_window
    if overlay_window:
        overlay_window.show_window()


def main():
    global overlay_window

    parser = argparse.ArgumentParser(description="LAE - AI Assistant")
    parser.add_argument("action", nargs="?", choices=["open", "search", "run", "execute"], help="Action to perform")
    parser.add_argument("target", nargs="?", help="Target (URL, app name, or command)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--hotkey", "-h", action="store_true", help="Run with hotkey overlay (Alt+Space)")

    args = parser.parse_args()

    lae = LAE()

    if args.hotkey or args.action is None:
        # Run with hotkey overlay
        print("LAE is running with hotkey overlay (Alt+Space to activate)")
        print("Press Ctrl+C to exit")

        overlay_window = LAEOverlayWindow(lae)

        # Register hotkey
        keyboard.add_hotkey('alt+space', hotkey_handler)

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\nExiting LAE...")
        finally:
            keyboard.remove_hotkey('alt+space')

    else:
        result = lae.execute(args.action, args.target)
        print(result)
        return 0

    return 0


# Global overlay window instance
overlay_window = None

if __name__ == "__main__":
    sys.exit(main())