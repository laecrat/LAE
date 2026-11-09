#!/usr/bin/env python3
"""
Command Executor - Handles system command execution.
"""

import subprocess
import os
import platform
import time
import shutil


class CommandExecutor:
    """Executes system commands safely."""

    def __init__(self):
        self.system = platform.system()
        self.allowed_commands = {
            "echo", "ls", "dir", "pwd", "cd", "whoami", "hostname", "date", "time",
            "python", "python3", "pip", "pip3", "npm", "node", "git", "gh",
            "npm", "npx", "yarn", "pnpm",
            "code", "cursor", "sublime", "atom",
            "chrome", "firefox", "edge",
            "tasklist", "taskkill", "netstat", "ping",
            "clear", "cls",
            "make", "cmake", "gcc", "g++", "clang", "rustc", "cargo",
            "docker", "docker-compose", "kubectl", "helm",
            "kubectl", "k9s",
            "terraform", "ansible", "chef", "puppet",
            "aws", "az", "gcloud",
            "open", "open-url",  # macOS
        }

        self.safe_commands = {
            "ls", "dir", "pwd", "whoami", "date", "time", "hostname", "clear", "cls",
            "echo", "cat", "head", "tail", "grep", "find", "which", "whereis",
            "python", "python3", "pip", "pip3", "node", "npm", "npx", "yarn",
            "git", "gh", "code", "cursor",
            "tasklist", "netstat", "ping"
        }

    def run(self, command: str, timeout: int = 30, safe_mode: bool = True) -> str:
        """Execute a system command."""
        try:
            # Validate command in safe mode
            if safe_mode:
                is_safe, reason = self._is_command_safe(command)
                if not is_safe:
                    return f"⚠️  Blocked (safe mode): {reason}\nCommand: {command}"

            # Parse command
            args = command.split()
            if not args:
                return "❌ Empty command"

            cmd_name = args[0]

            # Determine shell based on platform
            use_shell = cmd_name in ["cd", "echo", "ls", "dir"] or not shutil.which(cmd_name)

            kwargs = {}
            if self.system == "Windows":
                kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = 0  # SW_HIDE
                kwargs["startupinfo"] = si

            if use_shell or self.system == "Windows":
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=True,
                    cwd=os.getcwd(),
                    **kwargs
                )
            else:
                result = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=False,
                    cwd=os.getcwd(),
                    **kwargs
                )

            output = []
            if result.stdout:
                output.append(result.stdout)
            if result.stderr:
                output.append(result.stderr, file=sys.stderr)

            return_code = result.returncode
            return f"$ {command}\n{''.join(output)}{'[exit code: {}]'.format(return_code) if return_code != 0 else ''}"

        except subprocess.TimeoutExpired:
            return f"⏱️  Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return f"❌ Command not found: {args[0]}"
        except PermissionError:
            return f"❌ Permission denied: {args[0]}"
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"

    def run_background(self, command: str, timeout: int = 60) -> str:
        """Run a command in the background."""
        try:
            popen_kwargs = {"shell": True}
            if self.system == "Windows":
                popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = 0
                popen_kwargs["startupinfo"] = si
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
                **popen_kwargs
            )

            return f"🚀 Running in background (PID: {process.pid}): {command}"

        except Exception as e:
            return f"❌ Failed to start background process: {str(e)}"

    def run_interactive(self, command: str) -> str:
        """Run a command interactively (shows output in real-time)."""
        try:
            return f"💻 Interactive mode: {command}\n(Terminal will be opened for this command)"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _is_command_safe(self, command: str) -> tuple:
        """Check if a command is safe to run."""
        if not command:
            return False, "Empty command"

        args = command.split()
        if not args:
            return False, "No command specified"

        cmd_name = args[0]

        # Check for dangerous operations
        dangerous_keywords = [
            "rm -rf", "del /s", "format", "fdisk", "mkfs",
            "chmod 777", "chown", "shutdown", "reboot", "poweroff",
            "dd if=", "mkfs", "mknod",
            ">", ">>", "<", "&&", "||", "|",
            "curl |", "wget |", "pip install -e", "npm install -g"
        ]

        for keyword in dangerous_keywords:
            if keyword in command.lower():
                return False, f"Dangerous keyword detected: {keyword}"

        # Check if command exists
        if not shutil.which(cmd_name) and cmd_name not in ["cd", "echo"]:
            return False, f"Command not found: {cmd_name}"

        return True, "OK"

    def get_env(self, var_name: str = None) -> dict:
        """Get environment variables."""
        if var_name:
            return {var_name: os.environ.get(var_name, "Not set")}
        return dict(os.environ)

    def set_env(self, var_name: str, value: str) -> str:
        """Set an environment variable (temporary)."""
        os.environ[var_name] = value
        return f"✅ Set environment variable: {var_name}={value}"

    def pwd(self) -> str:
        """Get current working directory."""
        return f"📁 Current directory: {os.getcwd()}"

    def cd(self, path: str) -> str:
        """Change directory (returns what would happen, doesn't actually change for the session)."""
        expanded = os.path.expanduser(path)
        if os.path.isdir(expanded):
            return f"📁 Would change to: {expanded}"
        return f"❌ Directory not found: {expanded}"

    def ls(self, path: str = ".") -> str:
        """List directory contents."""
        try:
            expanded = os.path.expanduser(path)
            entries = []

            for entry in os.listdir(expanded):
                full_path = os.path.join(expanded, entry)
                if os.path.isdir(full_path):
                    entries.append(f"📁 {entry}/")
                else:
                    size = os.path.getsize(full_path)
                    entries.append(f"📄 {entry} ({size} bytes)")

            return f"📂 Contents of {expanded}:\n" + "\n".join(entries)
        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"

    def whoami(self) -> str:
        """Get current user."""
        return f"👤 Current user: {os.getlogin()}"

    def help(self) -> str:
        """Show available commands."""
        return f"""Available commands:
{chr(10).join(f'  {cmd}' for cmd in sorted(self.allowed_commands))}

Run any command with: lae execute <command>
Example: lae execute ls -la
"""