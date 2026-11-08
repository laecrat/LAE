#!/usr/bin/env python3
"""
LAE - AI Assistant
An AI assistant that can open websites, apps and run programs as instructed.
"""

import sys
import argparse
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


def main():
    parser = argparse.ArgumentParser(description="LAE - AI Assistant")
    parser.add_argument("action", choices=["open", "search", "run", "execute"], help="Action to perform")
    parser.add_argument("target", help="Target (URL, app name, or command)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    lae = LAE()
    result = lae.execute(args.action, args.target)

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())