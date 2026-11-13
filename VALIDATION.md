# LAE Validation Guide

## Pre-Commit Validation Steps

Before committing changes, follow these validation steps:

### 1. Syntax Validation

Run Python's syntax checker on all files:

```bash
python -m py_compile main.py browser_controller.py app_controller.py command_executor.py
```

**Expected output:** No output (no errors = all files have valid syntax)

### 2. Run Installation Test

Execute the validation script:

```bash
# Install dependencies first
pip install -r requirements.txt

# Then run validation
python test_installation.py
```

Or on Windows, run the install script:
```cmd
install.bat
```

### 3. Manual Testing (Optional)

Test the basic functionality:

```bash
# Test opening a website (without hotkey mode)
python main.py open https://www.google.com

# Test opening an app
python main.py open chrome

# Test searching
python main.py search "python tutorials"

# Test power management
python main.py lock
```

### 4. Check File Structure

Ensure all required files are present:
- ✅ main.py - Main entry point
- ✅ browser_controller.py - Website handling
- ✅ app_controller.py - Application management
- ✅ command_executor.py - Power management
- ✅ requirements.txt - Dependencies
- ✅ README.md - Documentation
- ✅ LICENSE - MIT License
- ✅ .gitignore - Git ignore rules
- ✅ test_installation.py - Validation script
- ✅ install.bat - Windows installation script
- ✅ VALIDATION.md - This file

## Common Issues

### Issue: ModuleNotFoundError: No module named 'keyboard'
**Solution:** Install the missing module:
```bash
pip install keyboard pystray
```

### Issue: tkinter import errors
**Solution:** tkinter usually comes with Python. If missing:
- **Windows:** Reinstall Python with tkinter selected
- **macOS:** `brew install python-tk`
- **Linux:** `sudo apt-get install python3-tk`

### Issue: Syntax errors after editing
**Solution:** Always run syntax check after making changes:
```bash
python -m py_compile main.py
```

## Validation Results

Run this command to get a quick validation status:
```bash
python test_installation.py
```

## Commit Checklist

Before committing:
- [ ] Run `python -m py_compile main.py` (no errors)
- [ ] Run `python test_installation.py` (all tests pass)
- [ ] Update README.md if needed
- [ ] Test hotkey mode: `python main.py --hotkey` (press Alt+Space to test)
- [ ] Commit with descriptive message

## Rollback Plan

If something breaks after commit:
```bash
git log --oneline -5  # Find recent commits
git reset --hard HEAD~1  # Revert last commit
```

Or to unstage changes:
```bash
git reset HEAD  # Unstage all changes
```