#!/usr/bin/env python3
"""
Command Executor - Handles system power management commands.
"""

import subprocess
import platform


class CommandExecutor:
    """Executes power management commands."""

    def __init__(self):
        self.system = platform.system()

    def power_command(self, action: str) -> str:
        """Execute Windows power management commands."""
        if self.system != "Windows":
            return "❌ Power commands are only supported on Windows"

        action = action.lower().strip()
        commands = {
            "lock": ["rundll32.exe", "user32.dll,LockWorkStation"],
            "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
            "hibernate": ["shutdown", "/h"],
            "signout": ["shutdown", "/l"],
            "logoff": ["shutdown", "/l"],
            "shutdown": ["shutdown", "/s", "/t", "0"],
            "restart": ["shutdown", "/r", "/t", "0"],
            "reboot": ["shutdown", "/r", "/t", "0"],
        }

        if action not in commands:
            return f"❌ Unknown power action: {action}. Use: lock, sleep, hibernate, signout/logoff, shutdown, restart/reboot"

        cmd = commands[action]
        try:
            if action == "sleep":
                # Prevent sleep if media is playing (pass 0 to allow sleep)
                subprocess.run(["powercfg", "/requestsoverride", "PROCESS", "firefox.exe", "", "", "0"], capture_output=True)
            subprocess.Popen(cmd, shell=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
            return f"✅ Executing: {action}"
        except Exception as e:
            return f"❌ Failed to execute {action}: {str(e)}"

    def help(self) -> str:
        """Show available power commands."""
        return """Power commands:
  lock (L)       - Lock the workstation
  sleep (S)      - Put laptop to sleep
  hibernate      - Hibernate the system
  signout (O)    - Sign out / logoff
  shutdown (D)   - Shutdown the system
  restart        - Restart the system

Run with: lae <command>
Example: lae lock
Example: lae shutdown
"""