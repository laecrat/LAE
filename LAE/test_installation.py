#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Installation test script for LAE AI Assistant
Run this before committing to verify everything works
"""

import sys
import os

# ASCII-safe symbols for Windows compatibility
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"

def test_syntax():
    """Test all Python files for syntax errors."""
    import py_compile

    files = [
        'main.py',
        'browser_controller.py',
        'app_controller.py',
        'command_executor.py'
    ]

    print("Testing syntax...")
    for f in files:
        if os.path.exists(f):
            try:
                py_compile.compile(f, doraise=True)
                print(f"  {OK} {f} - OK")
            except py_compile.PyCompileError as e:
                print(f"  {FAIL} {f} - Syntax error: {e}")
                return False
        else:
            print(f"  {WARN} {f} - File not found")

    print(f"{OK} All syntax checks passed!\n")
    return True

def test_core_imports():
    """Test importing core modules."""
    print("Testing core imports...")

    try:
        from browser_controller import BrowserController
        print(f"  {OK} BrowserController imported")
    except ImportError as e:
        print(f"  {FAIL} BrowserController import failed: {e}")
        return False

    try:
        from app_controller import AppController
        print(f"  {OK} AppController imported")
    except ImportError as e:
        print(f"  {FAIL} AppController import failed: {e}")
        return False

    try:
        from command_executor import CommandExecutor
        print(f"  {OK} CommandExecutor imported")
    except ImportError as e:
        print(f"  {FAIL} CommandExecutor import failed: {e}")
        return False

    print(f"{OK} All core imports passed!\n")
    return True

def test_lae_class():
    """Test the LAE class instantiation and methods."""
    print("Testing LAE class...")

    try:
        from main import LAE
        lae = LAE()
        print(f"  {OK} LAE instance created")

        # Test URL detection
        assert lae._is_url("https://google.com"), "URL detection failed"
        assert lae._is_url("www.example.com"), "www URL detection failed"
        print(f"  {OK} URL detection works")

        # Test website detection
        assert not lae._is_url("not-a-url"), "URL check failed"
        print(f"  {OK} Website detection works")

        print(f"{OK} LAE class tests passed!\n")
        return True

    except ImportError as e:
        print(f"  {WARN} LAE import requires keyboard module (skip if hotkey not needed)")
        print("  To install: pip install keyboard pystray\n")
        return True  # Not a failure, just skip
    except Exception as e:
        print(f"  {FAIL} LAE class test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("Testing file structure...")

    required_files = [
        'main.py',
        'browser_controller.py',
        'app_controller.py',
        'command_executor.py',
        'requirements.txt',
        'README.md',
        'LICENSE',
        '.gitignore'
    ]

    all_exist = True
    for f in required_files:
        if os.path.exists(f):
            print(f"  {OK} {f}")
        else:
            print(f"  {FAIL} {f} - Missing")
            all_exist = False

    if all_exist:
        print(f"{OK} All required files present!\n")
    return all_exist

def main():
    """Run all tests."""
    print("=" * 50)
    print("LAE Installation Validation")
    print("=" * 50 + "\n")

    results = []
    results.append(test_syntax())
    results.append(test_file_structure())
    results.append(test_core_imports())
    results.append(test_lae_class())

    print("=" * 50)
    if all(results):
        print(f"{OK} All validation tests PASSED!")
        print("\nYou can safely commit your changes.")
        return 0
    else:
        print(f"{FAIL} Some validation tests FAILED!")
        print("\nPlease fix the errors before committing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())