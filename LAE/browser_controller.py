#!/usr/bin/env python3
"""
Browser Controller - Handles website opening and search functionality.
"""

import webbrowser
import urllib.parse
import subprocess
import platform
import re


class BrowserController:
    """Controls web browsers and website interactions."""

    def __init__(self):
        self.supported_browsers = ["chrome", "firefox", "edge", "safari"]
        self.search_engines = {
            "brave": "https://search.brave.com/search?q=",
            "google": "https://www.google.com/search?q=",
            "duckduckgo": "https://duckduckgo.com/?q=",
            "bing": "https://www.bing.com/search?q=",
            "yahoo": "https://search.yahoo.com/search?p=",
            "github": "https://github.com/search?q="
        }

    def open(self, url: str) -> str:
        """Open a URL in the default browser."""
        try:
            # Clean and normalize URL
            normalized_url = self._normalize_url(url)

            # Open in default browser
            webbrowser.open(normalized_url, new=2)

            return f"✅ Opened: {normalized_url}"
        except Exception as e:
            return f"❌ Failed to open URL: {str(e)}"

    def open_with_browser(self, url: str, browser: str) -> str:
        """Open a URL with a specific browser."""
        try:
            normalized_url = self._normalize_url(url)

            if platform.system() == "Windows":
                # Try to open with specific browser on Windows
                browser_paths = {
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "safari": "safari.exe"  # Rare on Windows
                }

                browser_exe = browser_paths.get(browser.lower(), browser)
                subprocess.Popen([browser_exe, normalized_url], shell=True)
            else:
                webbrowser.open(normalized_url)

            return f"✅ Opened {normalized_url} in {browser}"
        except Exception as e:
            return f"❌ Failed to open in {browser}: {str(e)}"

    def search(self, query: str, engine: str = "brave") -> str:
        """Search using a specific search engine."""
        try:
            if engine.lower() not in self.search_engines:
                engine = "duckduckgo"

            search_url = self.search_engines[engine.lower()] + urllib.parse.quote(query)
            webbrowser.open(search_url)

            return f"🔍 Searched '{query}' on {engine.title()}: {search_url}"
        except Exception as e:
            return f"❌ Search failed: {str(e)}"

    def search_website(self, query: str, website: str) -> str:
        """Search within a specific website."""
        website_search_urls = {
            "github": "https://github.com/search?q=",
            "stackoverflow": "https://stackoverflow.com/search?q=",
            "pypi": "https://pypi.org/search/?q=",
            "npm": "https://www.npmjs.com/search?q=",
            "youtube": "https://www.youtube.com/results?search_query="
        }

        if website.lower() not in website_search_urls:
            return f"❌ Cannot search {website}. Supported: {list(website_search_urls.keys())}"

        search_url = website_search_urls[website.lower()] + urllib.parse.quote(query)
        webbrowser.open(search_url)

        return f"🔍 Searched '{query}' on {website}: {search_url}"

    def _normalize_url(self, url: str) -> str:
        """Normalize and validate a URL."""
        # Remove extra whitespace
        url = url.strip()

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            if url.startswith("www."):
                url = "https://" + url
            else:
                url = "https://www." + url

        return url

    def get_url_preview(self, url: str) -> dict:
        """Get information about a URL without opening it."""
        normalized = self._normalize_url(url)
        return {
            "url": normalized,
            "valid": True,
            "protocol": "https" if "https" in normalized else "http",
            "domain": normalized.split("//")[-1].split("/")[0]
        }