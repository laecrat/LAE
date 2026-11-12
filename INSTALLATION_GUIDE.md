# LAE - AI Assistant Installation & User Guide

## Table of Contents
1. [What is LAE?](#what-is-lae)
2. [System Requirements](#system-requirements)
3. [Installation Methods (Windows)](#installation-methods-windows)
4. [Installation Methods (macOS/Linux)](#installation-methods-macoslinux)
5. [First-Time Setup](#first-time-setup)
6. [How to Run LAE](#how-to-run-lae)
7. [Usage Guide](#usage-guide)
8. [Configuration](#configuration)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## What is LAE?

**LAE** (Launcher and Assistant for Everything) is a Windows-first AI assistant that:
- Opens websites and searches the web
- Launches installed applications
- Runs system commands
- Provides a floating translucent command bar
- Works with hotkeys and system tray

**Hotkey**: `Win + `` ` `` (Win key + backtick)

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10/11, macOS, Linux | Windows 11 |
| Python | 3.8+ | 3.13 |
| RAM | 50 MB | 100 MB |
| Disk | 10 MB | 20 MB |

**Dependencies** (installed via pip):
- requests >= 2.28.0
- urllib3 >= 1.26.0
- keyboard >= 0.13.5
- pystray >= 0.19.0
- pyautogui >= 0.9.54
- psutil >= 5.9.0
- pillow >= 9.0.0

---

## Installation Methods (Windows)

### Method 1: Using install.bat (RECOMMENDED)

**Step 1:** Open PowerShell as Administrator
- Press `Win + X`
- Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

**Step 2:** Navigate to LAE directory
```powershell
cd "C:\path\to\LAE"
```

**Step 3:** Run the installation script
```powershell
.\install.bat
```

**What this does:**
- Checks if Python 3.8+ is installed
- Installs all Python dependencies via `pip install -r requirements.txt`
- Runs validation tests
- Reports success/failure

---

### Method 2: Manual Installation (Windows)

**Step 1:** Open Command Prompt or PowerShell
```powershell
# Navigate to LAE directory
cd "C:\path\to\LAE"
```

**Step 2:** Check Python installation
```powershell
python --version
# Should output: Python 3.8.x or higher
# If not found, download from: https://python.org/downloads
```

**Step 3:** Install dependencies
```powershell
pip install -r requirements.txt
```

**Step 4:** Verify installation
```powershell
python test_installation.py
```

---

### Method 3: Using setup.sh via Git Bash (Windows)

**Step 1:** Install Git for Windows if not already installed
- Download from: https://git-scm.com/download/win

**Step 2:** Open Git Bash in the LAE directory
```bash
# Right-click in LAE folder → "Git Bash Here"
# OR
cd /c/path/to/LAE
```

**Step 3:** Run setup script
```bash
./setup.sh
```

**What this does:**
- Checks Python version
- Creates a virtual environment
- Activates the virtual environment
- Installs dependencies
- Initializes git repository if needed

---

### Method 4: One-Click Desktop Shortcut

**Step 1:** Create desktop shortcut
```powershell
# Run from PowerShell in LAE directory
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

**What this does:**
- Creates `LAE.lnk` on your desktop
- Double-click the shortcut to launch LAE in background
- No console window appears

---

### Method 5: Auto-Start on Windows Login

**Step 1:** Enable auto-start
```powershell
# Run from PowerShell in LAE directory
powershell -ExecutionPolicy Bypass -File install_startup.ps1
```

**Step 2:** To disable auto-start later
```powershell
powershell -ExecutionPolicy Bypass -File install_startup.ps1 -Remove
```

**What this does:**
- Creates a shortcut in Windows Startup folder
- LAE launches automatically when you log in
- Runs silently in background (no console)

---

## Installation Methods (macOS/Linux)

### Method 1: Using setup.sh

**Step 1:** Make script executable
```bash
chmod +x setup.sh
```

**Step 2:** Run setup
```bash
./setup.sh
```

**What this does:**
- Checks Python 3.x installation
- Creates virtual environment (`venv`)
- Activates virtual environment
- Installs dependencies
- Initializes git repository

**Step 3:** Activate virtual environment each time
```bash
source venv/bin/activate
```

### Method 2: Manual Installation

```bash
# Navigate to LAE directory
cd /path/to/LAE

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: .\venv\Scripts\activate  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run validation
python test_installation.py
```

---

## First-Time Setup

### Step 1: Verify Dependencies
```powershell
# Windows
python -c "import keyboard, pystray, PIL, requests; print('All dependencies OK')"
```

### Step 2: Test Basic Functionality
```powershell
# Test website opening
python main.py open google.com

# Test search
python main.py search "python tutorials"

# Test app launching
python main.py open app notepad
```

### Step 3: Configure Hotkey (Optional)
Edit `config.json`:
```json
{
  "features": {
    "hotkey": "win+;"
  }
}
```

---

## How to Run LAE

### Mode 1: With Hotkey & Tray Icon (RECOMMENDED)

```powershell
python main.py --hotkey
```

**Features:**
- System tray icon appears in taskbar
- Press `Win + `` ` `` to open the command bar
- Double-click tray icon to show LAE
- Right-click tray icon for options
- No admin required for basic features

**Note:** For full hotkey functionality on Windows, run as Administrator:
```powershell
# Right-click PowerShell → "Run as Administrator"
python main.py --hotkey
```

---

### Mode 2: Always-Visible Window

```powershell
python main.py --window
```

**Features:**
- Window stays visible on screen
- No admin privileges needed
- Drag to move the window
- Click outside to hide

---

### Mode 3: Background Mode (via lae.bat)

```powershell
# Double-click lae.bat, or run:
pythonw main.py --bg
```

**Features:**
- No console window
- Runs silently in background
- Tray icon only
- Ideal for desktop shortcut

---

### Mode 4: One-Shot CLI Commands

```powershell
# Open a website
python main.py open google.com
python main.py open website github.com
python main.py open https://example.com

# Search on default engine (configured in config.json)
python main.py search "machine learning"

# Search on specific site
python main.py search youtube "lofi beats"
python main.py search stackoverflow "python list"
python main.py search github "claude code"

# Open installed applications
python main.py open app notepad
python main.py open app chrome
python main.py open app code

# Run system commands
python main.py run git status
python main.py execute "dir /s"
python main.py run python --version
```

---

## Usage Guide

### Basic Commands

| Command | Action | Example |
|---------|--------|---------|
| `open website <url>` | Open URL in browser | `open website google.com` |
| `open <url>` | Open URL (auto-adds https://www.) | `open github.com` |
| `open app <name>` | Launch installed app | `open app notepad` |
| `search <query>` | Search on default engine | `search python tutorials` |
| `search <site> <query>` | Search specific site | `search youtube lofi` |
| `run <command>` | Run system command | `run git status` |
| `execute <command>` | Alternative to run | `execute ls -la` |
| `lock` or `L` | Lock the workstation | `lock` |
| `sleep` or `S` | Put laptop to sleep | `sleep` |
| `signout` or `O` | Sign out / logoff | `signout` |
| `shutdown` or `D` | Shutdown the system | `shutdown` |
| `restart` | Restart the system | `restart` |
| `hibernate` | Hibernate the system | `hibernate` |

### Bangs (Helium-style Search Shortcuts)

Type `!` + alias + query:

| Bang | Site | Example |
|------|------|---------|
| `!yt` | YouTube | `!yt lofi beats` |
| `!g` | Google | `!g machine learning` |
| `!b` | Brave | `!b rust programming` |
| `!gh` | GitHub | `!gh claude code` |
| `!w` | Wikipedia | `!w artificial intelligence` |
| `!am` | Amazon | `!am wireless mouse` |
| `!maps` | Google Maps | `!maps pizza near me` |

**View all bangs:** See `bangs.txt` in the LAE directory

---

### Special Keys in LAE

| Key | Action |
|-----|--------|
| `Enter` | Execute command |
| `Esc` | Hide the command bar |
| Click outside | Hide the command bar |
| Drag title bar | Move the window |
| Double-click tray icon | Show LAE |
| Right-click tray icon | Quit LAE |

---

## Configuration

### config.json Settings

```json
{
  "features": {
    "hotkey": "win+`",
    "browser": {
      "default_engine": "brave",
      "timeout": 30,
      "auto_open": true
    },
    "app": {
      "safe_mode": true,
      "allow_unknown_apps": false,
      "preferred_browsers": ["chrome", "edge", "firefox"]
    },
    "commands": {
      "safe_mode": true,
      "timeout": 30,
      "max_output_lines": 100
    }
  },
  "integrations": {
    "github": {
      "enabled": true,
      "token": "environment",
      "auto_update": true
    }
  },
  "update": {
    "check_frequency": "daily",
    "auto_update": false,
    "repository": "lae.crat074/lae"
  }
}
```

### Changing the Hotkey

Edit `config.json`:
```json
{
  "features": {
    "hotkey": "win+;"
  }
}
```

**Safe hotkey choices:**
- `win+`` ` (default)
- `win+;`
- `win+'`
- `win+[`
- `alt+`` `

**Avoid these:**
- `alt+space`
- `win+space`
- `win+l`, `win+d`, `win+e`
- `ctrl+space`
- `ctrl+alt+l`

---

## Advanced Features

### 1. Site Search Syntax

```bash
# Search on a specific site
search youtube lofi beats
search stackoverflow python list
search github claude code
search wikipedia artificial intelligence

# With "on/at/in" prepositions
search on reddit programming
search at twitter tech news
```

### 2. Direct Application Launching

LAE automatically finds installed apps:
```bash
open app chrome
open app firefox
open app visual studio code
open app notepad++
open app helium
```

**Matching is case-aware:**
- `boy` → matches "Boy" exactly
- `chrome` → matches "Google Chrome" (case-insensitive)

### 3. Background App Cache

LAE pre-scans installed apps at startup:
- First search is instant
- Cache refreshes in background
- No delay when using LAE

### 4. Safe Mode

By default, LAE blocks dangerous commands:
- `rm -rf /`
- Destructive redirects
- System-damaging operations

Disable in `config.json`:
```json
{
  "features": {
    "commands": {
      "safe_mode": false
    }
  }
}
```

---

## Troubleshooting

### Problem: Hotkey not working

**Solution:**
1. Run PowerShell as Administrator
2. Restart LAE: `python main.py --hotkey`
3. Check `config.json` for conflicting hotkeys

### Problem: Python command not found

**Solution:**
1. Download Python 3.8+ from https://python.org/downloads
2. Check "Add Python to PATH" during installation
3. Restart terminal
4. Run: `python --version`

### Problem: Dependencies fail to install

**Solution:**
```powershell
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt --verbose
```

### Problem: Tray icon not showing

**Solution:**
- Ensure running on Windows (Linux/macOS have limited tray support)
- Try running with: `python main.py --window`

### Problem: Apps not launching

**Solution:**
1. Check if app is installed
2. Try full name: `open app "Google Chrome"`
3. Check if app is in PATH or Start Menu

### Problem: Search not working

**Solution:**
1. Check internet connection
2. Verify default engine in `config.json`
3. Try direct URL: `open website google.com`

### Problem: Need to restart LAE

**Solution:**
- Tray icon: Right-click → Quit, then restart
- Or close terminal and run again: `python main.py --hotkey`

---

## Project Structure

```
LAE/
├── main.py              # Main entry point, GUI, hotkey handler
├── app_controller.py  # App discovery and launching
├── browser_controller.py # Website opening, search engines, bangs
├── command_executor.py  # Safe system command execution
├── config.json          # Configuration file
├── requirements.txt     # Python dependencies
├── lae.bat              # Background launcher (pythonw.exe)
├── create_shortcut.ps1  # Creates desktop shortcut
├── install_startup.ps1  # Adds/removes from Windows startup
├── install.bat          # Windows installation script
├── setup.sh             # Unix/Linux/macOS setup script
├── test_installation.py # Validation script
├── bangs.txt            # Search bangs reference
├── VALIDATION.md        # Pre-commit checks
├── .github/             # GitHub workflows
├── LICENSE              # MIT License
└── README.md            # Project documentation
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                         LAE QUICK START                      │
├─────────────────────────────────────────────────────────────┤
│ INSTALLATION                                                  │
│   Windows:  .\install.bat                                   │
│   Unix:     ./setup.sh                                        │
│   Manual:   pip install -r requirements.txt                 │
├─────────────────────────────────────────────────────────────┤
│ RUNNING                                                       │
│   --hotkey   :  python main.py --hotkey                      │
│   --window   :  python main.py --window                      │
│   --bg       :  python main.py --bg OR double-click lae.bat  │
├─────────────────────────────────────────────────────────────┤
│ COMMANDS                                                      │
│   open website <url>   → Open URL                              │
│   open app <name>      → Launch app                           │
│   search <query>       → Web search                           │
│   search <site> <q>    → Site search                          │
│   !yt <query>          → YouTube bang                         │
│   run <command>        → Execute command                      │
├─────────────────────────────────────────────────────────────┤
│ POWER COMMANDS                                                │
│   lock / L             → Lock workstation                     │
│   sleep / S            → Put to sleep                         │
│   signout / O          → Sign out                             │
│   shutdown / D         → Shutdown system                      │
│   restart              → Restart system                       │
│   hibernate            → Hibernate                            │
├─────────────────────────────────────────────────────────────┤
│ HOTKEY                                                        │
│   Win + `    → Open command bar                               │
│   Enter      → Execute                                         │
│   Esc        → Hide                                            │
│   Click outside → Hide                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Support

- **Email**: lae.crat074@gmail.com
- **GitHub**: https://github.com/laecrat/LAE

---

*🤖 Generated with [Claude Code](https://claude.com/claude-code)*