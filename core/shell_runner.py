"""Safe shell command runner with security policies."""

import subprocess
import re
from pathlib import Path
from typing import Optional, List


class SecurityError(Exception):
    """Raised when command violates security policy."""
    pass


class ShellRunner:
    """Execute shell commands with security validation."""
    
    # Allowed commands (whitelist)
    ALLOWED_COMMANDS = {
        "git", "npm", "yarn", "pnpm", "node", "python", "python3",
        "pip", "pip3", "pytest", "jest", "vitest", "cargo", "rustc",
        "go", "make", "cmake", "gcc", "g++", "clang", "javac", "java",
        "mvn", "gradle", "dotnet", "ruby", "gem", "bundle", "php",
        "composer", "ls", "cat", "echo", "pwd", "which", "type"
    }
    
    # Dangerous patterns (blacklist)
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",
        r"sudo",
        r"su\s+",
        r"\|\s*bash",
        r"\|\s*sh",
        r"eval\s*\(",
        r"exec\s*\(",
        r">\s*/dev/",
        r"curl.*\|",
        r"wget.*\|",
        r"dd\s+if=",
        r"mkfs\.",
        r"format\s+",
        r":\(\)\{.*\}",  # fork bomb
    ]
    
    def __init__(self, allowed_cwd: Optional[Path] = None, log_dir: Optional[Path] = None):
        """
        Initialize shell runner.
        
        Args:
            allowed_cwd: Restrict commands to this directory
            log_dir: Directory for command logs
        """
        self.allowed_cwd = Path(allowed_cwd) if allowed_cwd else None
        self.log_dir = Path(log_dir) if log_dir else Path(".multiagent/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_command(self, command: str) -> None:
        """
        Validate command against security policies.
        
        Args:
            command: Shell command to validate
        
        Raises:
            SecurityError: If command violates policy
        """
        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
        
        # Extract base command
        parts = command.strip().split()
        if not parts:
            raise SecurityError("Empty command")
        
        base_cmd = parts[0]
        
        # Check if command is allowed
        if base_cmd not in self.ALLOWED_COMMANDS:
            raise SecurityError(f"Command not allowed: {base_cmd}")
    
    def run(
        self,
        command: str,
        cwd: Optional[Path] = None,
        timeout: int = 300,
        capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run shell command with validation.
        
        Args:
            command: Shell command to run
            cwd: Working directory (must be within allowed_cwd)
            timeout: Command timeout in seconds
            capture_output: If True, capture stdout/stderr
        
        Returns:
            CompletedProcess with result
        
        Raises:
            SecurityError: If command violates policy
            subprocess.TimeoutExpired: If command times out
        """
        # Validate command
        self.validate_command(command)
        
        # Validate cwd
        if cwd:
            cwd = Path(cwd).resolve()
            if self.allowed_cwd:
                allowed = self.allowed_cwd.resolve()
                if not str(cwd).startswith(str(allowed)):
                    raise SecurityError(f"cwd outside allowed directory: {cwd}")
        
        # Run command
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True
        )
        
        # Log output
        self._log_command(command, result)
        
        return result
    
    def _log_command(self, command: str, result: subprocess.CompletedProcess):
        """Log command execution."""
        log_file = self.log_dir / "shell_commands.log"
        
        with open(log_file, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Command: {command}\n")
            f.write(f"Return code: {result.returncode}\n")
            if result.stdout:
                f.write(f"STDOUT:\n{result.stdout}\n")
            if result.stderr:
                f.write(f"STDERR:\n{result.stderr}\n")
