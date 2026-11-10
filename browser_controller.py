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
        }

        # Searchable sites (name -> search URL prefix). Used by "search <site> <q>"
        # and by bangs (!yt <q>).
        self.sites = {
            "youtube": "https://www.youtube.com/results?search_query=",
            "youtube music": "https://music.youtube.com/search?q=",
            "pinterest": "https://www.pinterest.com/search/pins/?q=",
            "reddit": "https://www.reddit.com/search/?q=",
            "twitter": "https://twitter.com/search?q=",
            "x": "https://twitter.com/search?q=",
            "instagram": "https://www.instagram.com/explore/tags/",
            "facebook": "https://www.facebook.com/search/top?q=",
            "tiktok": "https://www.tiktok.com/search?q=",
            "amazon": "https://www.amazon.com/s?k=",
            "flipkart": "https://www.flipkart.com/search?q=",
            "ebay": "https://www.ebay.com/sch/i.html?_nkw=",
            "wikipedia": "https://en.wikipedia.org/w/index.php?search=",
            "stackoverflow": "https://stackoverflow.com/search?q=",
            "github": "https://github.com/search?q=",
            "pypi": "https://pypi.org/search/?q=",
            "npm": "https://www.npmjs.com/search?q=",
            "medium": "https://medium.com/search?q=",
            "quora": "https://www.quora.com/search?q=",
            "tumblr": "https://www.tumblr.com/search/",
            "flickr": "https://www.flickr.com/search/?text=",
            "vimeo": "https://vimeo.com/search?q=",
            "soundcloud": "https://soundcloud.com/search?q=",
            "spotify": "https://open.spotify.com/search/",
            "twitch": "https://www.twitch.tv/search?term=",
            "discord": "https://discord.com/search?q=",
            "linkedin": "https://www.linkedin.com/search/results/all/?keywords=",
            "imdb": "https://www.imdb.com/find/?q=",
            "maps": "https://www.google.com/maps/search/",
            "news": "https://news.google.com/search?q=",
            "images": "https://www.google.com/search?tbm=isch&q=",
            "videos": "https://www.google.com/search?tbm=vid&q=",
        }

        # Bangs (Helium-style): !yt <query> -> search youtube. Aliases included.
        self.bangs = {
            "yt": "youtube", "youtube": "youtube",
            "ytm": "youtube music", "youtubemusic": "youtube music",
            "pin": "pinterest", "pinterest": "pinterest",
            "r": "reddit", "reddit": "reddit",
            "tw": "twitter", "x": "twitter", "twitter": "twitter",
            "ig": "instagram", "instagram": "instagram",
            "fb": "facebook", "facebook": "facebook",
            "tt": "tiktok", "tiktok": "tiktok",
            "am": "amazon", "az": "amazon", "amazon": "amazon",
            "fk": "flipkart", "flipkart": "flipkart",
            "eb": "ebay", "ebay": "ebay",
            "w": "wikipedia", "wiki": "wikipedia", "wikipedia": "wikipedia",
            "so": "stackoverflow", "stackoverflow": "stackoverflow",
            "gh": "github", "github": "github",
            "pypi": "pypi", "npm": "npm",
            "g": "google", "google": "google",
            "b": "brave", "brave": "brave",
            "ddg": "duckduckgo", "duckduckgo": "duckduckgo",
            "bing": "bing", "yh": "yahoo",
            "maps": "maps", "news": "news", "img": "images", "vid": "videos",
            "vimeo": "vimeo", "flickr": "flickr", "sc": "soundcloud", "soundcloud": "soundcloud",
            "sp": "spotify", "spotify": "spotify", "twitch": "twitch",
            "li": "linkedin", "linkedin": "linkedin", "imdb": "imdb",
            "medium": "medium", "quora": "quora", "tumblr": "tumblr",
        }

        # Homepage for each site (used when a bang is typed with no query)
        self.homepages = {
            "youtube": "https://www.youtube.com",
            "youtube music": "https://music.youtube.com",
            "pinterest": "https://www.pinterest.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "tiktok": "https://www.tiktok.com",
            "amazon": "https://www.amazon.com",
            "flipkart": "https://www.flipkart.com",
            "ebay": "https://www.ebay.com",
            "wikipedia": "https://en.wikipedia.org",
            "stackoverflow": "https://stackoverflow.com",
            "github": "https://github.com",
            "pypi": "https://pypi.org",
            "npm": "https://www.npmjs.com",
            "medium": "https://medium.com",
            "quora": "https://www.quora.com",
            "tumblr": "https://www.tumblr.com",
            "flickr": "https://www.flickr.com",
            "vimeo": "https://vimeo.com",
            "soundcloud": "https://soundcloud.com",
            "spotify": "https://open.spotify.com",
            "twitch": "https://www.twitch.tv",
            "discord": "https://discord.com",
            "linkedin": "https://www.linkedin.com",
            "imdb": "https://www.imdb.com",
            "maps": "https://www.google.com/maps",
            "news": "https://news.google.com",
            "images": "https://www.google.com/imghp",
            "videos": "https://www.google.com",
            "brave": "https://search.brave.com",
            "google": "https://www.google.com",
            "duckduckgo": "https://duckduckgo.com",
            "bing": "https://www.bing.com",
            "yahoo": "https://search.yahoo.com",
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

    def resolve_site(self, name: str):
        """Resolve a site name or bang alias to a search-URL prefix. None if unknown."""
        key = name.lower().strip().lstrip("!")
        if key in self.bangs:
            key = self.bangs[key]
        if key in self.sites:
            return key, self.sites[key]
        if key in self.search_engines:
            return key, self.search_engines[key]
        # fuzzy: startswith match
        for site in self.sites:
            if site.startswith(key) or key.startswith(site):
                return site, self.sites[site]
        return None, None

    def search_website(self, query: str, website: str) -> str:
        """Search within a specific website (name or !bang)."""
        site, base = self.resolve_site(website)
        if base is None:
            return f"❌ Unknown site/bang '{website}'. Try: youtube, pinterest, reddit, wikipedia, github, amazon, maps, images ... or bangs like !yt !pin !w !g"
        search_url = base + urllib.parse.quote(query)
        webbrowser.open(search_url)
        return f"🔍 '{query}' on {site}: {search_url}"

    def bang_search(self, bang: str, query: str) -> str:
        """Helium-style bang: !yt <query>. Bare !yt (no query) opens the site home."""
        site, base = self.resolve_site(bang)
        if base is None:
            return f"❌ Unknown bang !{bang}"
        if not query.strip():
            home = self.homepages.get(site)
            if home:
                webbrowser.open(home)
                return f"🌐 Opened {site}: {home}"
            # fall back to opening the site root derived from the search URL
            home = base.split("?")[0]
            webbrowser.open(home)
            return f"🌐 Opened {site}: {home}"
        return self.search_website(query, bang)

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