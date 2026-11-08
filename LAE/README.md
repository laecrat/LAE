# LAE - AI Assistant

**LAE** (LAE = "Launcher and Assistant for Everything") is an AI-powered assistant that can open websites, apps, and run programs as instructed.

## Features

- 🌐 **Open Websites** - Open any URL in your default browser
- 🔍 **Website Search** - Search on specific websites (Google, DuckDuckGo, GitHub, etc.)
- 💻 **Open Applications** - Launch desktop applications by name
- ⚡ **Run Commands** - Execute system commands safely
- ⌨️ **Hotkey Overlay** - Press Alt+Space for instant command window (like Bixby)
- 🛡️ **Safe Mode** - Prevents dangerous operations

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11, macOS, or Linux

### Setup

1. Clone this repository:
```bash
git clone https://github.com/lae-crat074/lae.git
cd lae
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x main.py
```

## Usage

### Hotkey Overlay Mode (Alt+Space) - Like Bixby

This is the main way to use LAE! Press **Alt+Space** to open a small overlay window where you can type commands.

```bash
# Run LAE with hotkey overlay
python main.py --hotkey
# or
python main.py -h
```

### Command Types in Hotkey Mode

Type these commands in the overlay window:

```bash
# Open websites
open website google.com
open website https://www.github.com
open site stackoverflow.com

# Open applications
open chrome
open vscode
open powershell
open app calculator

# Search the web
search python tutorials
search machine learning
search github claude code

# Run system commands
run ls -la
run git status
run python --version
```

### Command Line Interface

```bash
# Open a website
python main.py open https://www.google.com
python main.py open example.com
python main.py open www.github.com

# Search the web
python main.py search "machine learning" --engine google
python main.py search "python tutorials" --engine duckduckgo

# Open an application
python main.py run chrome
python main.py run vscode
python main.py run notepad
python main.py run powershell

# Run a system command
python main.py execute "ls -la"
python main.py execute "git status"
python main.py execute "python --version"
```

### Python API

```python
from main import LAE

# Create an instance
assistant = LAE()

# Open a website
assistant.open_website("https://www.example.com")

# Search on a website
assistant.search_website("your query", "github")

# Open an application
assistant.open_app("chrome")

# Run a command
assistant.run_command("python --version")

# Execute any action
assistant.execute("open", "https://google.com")
assistant.execute("search", "python programming")
assistant.execute("run", "notepad")
assistant.execute("execute", "ls -la")
```

## Supported Applications

### Windows
- notepad, calculator, paint
- chrome, firefox, edge
- powershell, cmd
- visual studio code (vscode)
- file explorer, settings
- task manager, registry

### macOS
- Terminal, Safari
- Chrome, Firefox
- Visual Studio Code
- Finder

### Linux
- gnome-terminal, konsole
- firefox, chrome
- visual studio code

## Supported Search Engines
- Google
- DuckDuckGo
- Bing
- Yahoo
- GitHub (for code search)

## Security

LAE runs in safe mode by default, which:
- Blocks dangerous commands (rm -rf, etc.)
- Requires explicit permissions for global installs
- Prevents data-destructive operations

## Development

### Project Structure
```
LAE/
├── main.py              # Main entry point and CLI with hotkey overlay
├── browser_controller.py # Website and search handling
├── app_controller.py    # Application management
├── command_executor.py  # System command execution
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

### Running Tests
```bash
pytest tests/ -v
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Author

LAE is developed by lae.crat074@gmail.com

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)