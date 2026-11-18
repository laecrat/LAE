#!/usr/bin/env python3
"""
File Controller - Finds files by name using Windows search and opens them.

Search order:
  1. Everything CLI (es.exe) if installed — instant, uses the Windows index
  2. PowerShell recursive search of the user's common folders
     (Desktop, Documents, Downloads, Pictures, Videos, Music, OneDrive)
  If nothing is found, a clear "Not found" status is returned — Explorer
  is never opened automatically.
"""

import os
import re
import shutil
import subprocess
import ctypes
import platform
import difflib

# Folders searched when Everything is not available
USER_DIRS = ["Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music", "OneDrive"]

# Fuzzy gate for filename matching, same idea as app matching: only guess
# fuzzily when the query is 4+ characters.
FUZZY_THRESHOLD = 0.6
FUZZY_MIN_QUERY_LEN = 4


class FileController:
    """Searches for files by name on Windows and opens them."""

    def __init__(self):
        self.system = platform.system()

    # ------------------------------------------------------------- public
    def open_file(self, name: str) -> str:
        """Find a file whose name contains/matches `name` and open it."""
        query = name.strip().strip('"').strip("'")
        if not query:
            return "❌ No file name given"
        if self.system != "Windows":
            return "❌ File search is only supported on Windows"
        try:
            results = self.search(query)
            if not results:
                return f"❌ Not found: no file matching '{query}' on this PC"
            best = self._rank(results, query)[0]
            if self._shell_open(best):
                return f"📂 Opened: {best}"
            return f"❌ Could not open: {best}"
        except Exception as e:
            return f"❌ File search failed for '{name}': {str(e)}"

    # ------------------------------------------------------------- search
    def search(self, query: str, limit: int = 20) -> list:
        """Return candidate file paths matching the query."""
        es = shutil.which("es")
        if es:
            try:
                out = self._run(["es", "-n", str(limit), query], timeout=10)
                paths = [l.strip() for l in out.splitlines() if l.strip() and os.path.isfile(l.strip())]
                if paths:
                    return paths
            except Exception:
                pass
        return self._search_user_dirs(query, limit)

    def _search_user_dirs(self, query: str, limit: int) -> list:
        home = os.path.expanduser("~")
        dirs = [os.path.join(home, d) for d in USER_DIRS]
        dirs = [d for d in dirs if os.path.isdir(d)]
        if not dirs:
            return []
        # Escape single quotes for embedding in PowerShell single-quoted strings
        q = query.replace("'", "''")
        dir_list = ",".join(f"'{d.replace(chr(39), chr(39)*2)}'" for d in dirs)
        ps = (
            "$dirs=@(" + dir_list + ");"
            f"$q='{q}';"
            "foreach($d in $dirs){"
            "Get-ChildItem -LiteralPath $d -Recurse -File -ErrorAction SilentlyContinue | "
            "Where-Object { $_.Name -like ('*'+$q+'*') } | "
            f"Select-Object -First {limit} -ExpandProperty FullName"
            "}"
        )
        try:
            out = self._run(["powershell", "-NoProfile", "-Command", ps], timeout=25)
            return [l.strip() for l in out.splitlines() if l.strip() and os.path.isfile(l.strip())]
        except Exception:
            return []

    # ------------------------------------------------------------- ranking
    def _rank(self, paths: list, query: str) -> list:
        """Best matches first: exact name, then prefix, then substring, then fuzzy."""
        ql = query.lower()

        def score(p):
            fname = os.path.basename(p).lower()
            base = os.path.splitext(fname)[0]
            if fname == ql:
                return (0, 0, len(p))
            if base == ql:
                return (0, 1, len(p))
            if fname.startswith(ql):
                return (1, 0, len(p))
            if ql in fname:
                return (2, 0, len(p))
            if len(query) >= FUZZY_MIN_QUERY_LEN:
                s = difflib.SequenceMatcher(None, ql.replace(" ", ""), fname.replace(" ", "")).ratio()
                if s >= FUZZY_THRESHOLD:
                    return (3, -s, len(p))
            return (9, 0, len(p))

        return sorted(paths, key=score)

    # ------------------------------------------------------------- helpers
    def _run(self, cmd, timeout):
        kwargs = {"capture_output": True, "text": True, "timeout": timeout}
        if self.system == "Windows":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            kwargs["startupinfo"] = si
        r = subprocess.run(cmd, **kwargs)
        return r.stdout or ""

    def _shell_open(self, path: str) -> bool:
        try:
            r = ctypes.windll.shell32.ShellExecuteW(None, "open", path, None, None, 1)
            return r > 32
        except Exception:
            try:
                os.startfile(path)
                return True
            except Exception:
                return False

    def _open_explorer_search(self, query: str):
        safe = re.sub(r'[<>:"/\\|?*]', "", query)
        uri = f"search-ms:query={safe}"
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "open", uri, None, None, 1)
        except Exception:
            subprocess.Popen(["explorer.exe", uri],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
