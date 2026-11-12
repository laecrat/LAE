# LAE - AI Assistant

**LAE** (Launcher and Assistant for Everything) is a Windows-first voice/typing assistant: press a hotkey, type a command, and it opens websites, searches the web, launches your installed apps, and runs commands — with a floating translucent command bar.

## Features

- 🌐 **Open websites** — `open website google.com` opens `https://www.google.com`
- 🔍 **Web & site search** — `search python tutorials`, or `search github claude code` to search on a specific site
- 💻 **Smart app launching** — `open app <name>` scans your **real installed apps** (Start Menu shortcuts + UWP/Store apps via `Get-StartApps`) and opens the match. Matching is case-aware: exact case you typed wins (`boy` → `boy`, not `Boy`), otherwise case-insensitive (`girls` → `Girls`), then substring (`chrome` → `Google Chrome`)
- ⚡ **Run commands** — `run git status`, `execute ls -la`
- 🪟 **Floating command bar** — translucent (`-alpha`), always-on-top window that opens at the **center of the screen**
- ⌨️ **Configurable hotkey** — default `win+`` ` (set in `config.json` → `features.hotkey`); conflict-free on Windows. Tray icon (double-click) always works without admin
- 👆 **Auto-focus** — cursor lands in the typing bar automatically, no click needed
- 🖱️ **Draggable** — drag the window by its title/background anywhere on the desktop
- 🙈 **Click-outside-to-hide** — click anywhere else and the bar disappears
- 📶 **Live status** — the bar shows `🔍 Searching…` → `🚀 Opening X…` → `✅ Opened: X`
- ⚡ **Instant first search** — installed-app list is pre-scanned in the background at startup
- 🚫 **No console flash** — apps launch via Win32 `ShellExecuteW` / `explorer.exe`, so no cmd window ever pops up
- 🔁 **Runs in background** — via `pythonw.exe` (no console); survives closing the terminal
- 🖥️ **Desktop shortcut + startup** — one-click launch and auto-start on login
- 🛡️ **Safe mode** — blocks dangerous commands by default

## Installation

### Prerequisites
- Python 3.8+ (3.13 recommended) on Windows 10/11 (macOS/Linux basic support)
- `pip install -r requirements.txt`

### Quick start (Windows)
```powershell
cd LAE
pip install -r requirements.txt
python main.py --hotkey        # tray icon + hotkey (run terminal as Admin for the hotkey)
python main.py --window        # always-visible mini window (no admin needed)
```

### Make it permanent
```powershell
# Desktop shortcut (double-click to start in background, no console)
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

# Auto-start on Windows login
powershell -ExecutionPolicy Bypass -File install_startup.ps1
# undo startup:
powershell -ExecutionPolicy Bypass -File install_startup.ps1 -Remove
```

`lae.bat` launches LAE with `pythonw.exe` (no console window), so it keeps running after you close any terminal.

## Usage

Open LAE with **Win + `` ` ``** (hotkey), **double-click the tray icon**, or the **desktop shortcut**. Then type and press **Enter**:

```bash
open website google.com
open youtube.com
open app helium            # finds installed app by name (case-aware)
open chrome
search python tutorials
search stackoverflow python list
run git status
execute python --version

# Power management commands
lock          # or L     - Lock the workstation
sleep         # or S     - Put laptop to sleep
signout       # or O     - Sign out / logoff
shutdown      # or D     - Shutdown the system
restart       #          - Restart the system
hibernate     #          - Hibernate the system
```

Keys: **Enter** = run · **Esc** = hide · drag the title to move · click outside to dismiss.

### Change the hotkey
Edit `config.json`:
```json
"features": { "hotkey": "win+`", "browser": { "default_engine": "brave" } }
```
Safe two-key choices (avoid `alt+space`, `win+space`, `win+l/d/e/r/c`, `ctrl+space`, `ctrl+alt+l`): `win+`` `, `win+;`, `win+'`, `win+[`, `alt+`` `. Then restart LAE.

### Which search engine am I using?
The default is in `config.json` → `features.browser.default_engine` (currently `brave`). Supported: `brave`, `google`, `duckduckgo`, `bing`, `yahoo`. The opened search URL also reveals it (e.g. `https://search.brave.com/search?q=...`). Change it in `config.json` and restart LAE.

### CLI (one-shot, no GUI)
```bash
python main.py open https://www.google.com
python main.py search "machine learning"
python main.py run chrome
python main.py execute "git status"
python main.py lock        # lock workstation
python main.py sleep       # sleep
python main.py signout     # sign out
python main.py shutdown    # shutdown
```

### Modes
```bash
python main.py --hotkey    # tray + hotkey, hidden window (default)
python main.py --window    # always-visible mini window
python main.py --bg        # background mode for pythonw / launchers
```

## Project structure
```
├── main.py                 # CLI + LAEApp (floating bar, tray, hotkey, drag, focus, power commands)
├── app_controller.py       # installed-app scan + case-aware match + hidden launch
├── browser_controller.py   # websites & search engines
├── command_executor.py     # safe system commands + power management (lock/sleep/signout/shutdown)
├── config.json             # hotkey + settings (edit me)
├── requirements.txt
├── lae.bat                 # background launcher (pythonw, no console)
├── create_shortcut.ps1     # makes LAE.lnk on the Desktop
├── install_startup.ps1     # adds/removes LAE from Windows Startup
├── install.bat / setup.sh  # dependency installers
├── test_installation.py    # validation script (ASCII-safe)
├── VALIDATION.md           # pre-commit checks
├── .github/workflows/update.yml
├── LICENSE
└── README.md
```

## Validation
```bash
python -m py_compile main.py app_controller.py browser_controller.py command_executor.py
python test_installation.py
```

## Security
Safe mode blocks dangerous commands (e.g. `rm -rf`, destructive redirects) and requires explicit permission for global installs.

## License
MIT — see [LICENSE](LICENSE).

## Author
LAE — lae.crat074@gmail.com · GitHub: https://github.com/laecrat/LAE

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
