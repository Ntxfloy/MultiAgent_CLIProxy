"""Tests for worktree manager."""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.worktree_manager import WorktreeManager


class TestWorktreeManager(unittest.TestCase):
    """Test WorktreeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = WorktreeManager(base_dir=".test_worktrees")
    
    @patch('subprocess.run')
    def test_create_worktree(self, mock_run):
        """Test worktree creation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        path = self.manager.create_worktree("test-123", "main")
        
        # Verify git command
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0:3], ["git", "worktree", "add"])
        self.assertIn("task/test-123", args)
        self.assertIn("main", args)
        
        # Verify returned path
        self.assertEqual(path, Path(".test_worktrees/test-123"))
    
    @patch('subprocess.run')
    def test_commit_checkpoint(self, mock_run):
        """Test checkpoint commit."""
        mock_run.return_value = MagicMock(returncode=0)
        
        worktree_path = Path(".test_worktrees/test-123")
        self.manager.commit_checkpoint(worktree_path, "checkpoint: test")
        
        # Should call git add and git commit
        self.assertEqual(mock_run.call_count, 2)
        
        # First call: git add -A
        add_args = mock_run.call_args_list[0][0][0]
        self.assertIn("add", add_args)
        self.assertIn("-A", add_args)
        
        # Second call: git commit
        commit_args = mock_run.call_args_list[1][0][0]
        self.assertIn("commit", commit_args)
        self.assertIn("checkpoint: test", commit_args)
    
    @patch('subprocess.run')
    def test_merge_back_no_commit(self, mock_run):
        """Test merge with --no-commit."""
        mock_run.return_value = MagicMock(returncode=0)
        
        self.manager.merge_back("test-123", "main", no_commit=True)
        
        # Should call git checkout and git merge
        self.assertEqual(mock_run.call_count, 2)
        
        # First call: git checkout main
        checkout_args = mock_run.call_args_list[0][0][0]
        self.assertEqual(checkout_args, ["git", "checkout", "main"])
        
        # Second call: git merge --no-commit
        merge_args = mock_run.call_args_list[1][0][0]
        self.assertIn("merge", merge_args)
        self.assertIn("--no-commit", merge_args)
        self.assertIn("task/test-123", merge_args)
    
    @patch('subprocess.run')
    def test_cleanup(self, mock_run):
        """Test worktree cleanup."""
        mock_run.return_value = MagicMock(returncode=0)
        
        self.manager.cleanup("test-123", delete_branch=True)
        
        # Should call git worktree remove and git branch -D
        self.assertEqual(mock_run.call_count, 2)
        
        # First call: git worktree remove
        remove_args = mock_run.call_args_list[0][0][0]
        self.assertIn("worktree", remove_args)
        self.assertIn("remove", remove_args)
        
        # Second call: git branch -D
        branch_args = mock_run.call_args_list[1][0][0]
        self.assertEqual(branch_args, ["git", "branch", "-D", "task/test-123"])
    
    @patch('subprocess.run')
    def test_list_worktrees(self, mock_run):
        """Test listing worktrees."""
        mock_output = """worktree /path/to/main
branch refs/heads/main

worktree /path/to/worktree1
branch refs/heads/task/123
"""
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
        
        worktrees = self.manager.list_worktrees()
        
        self.assertEqual(len(worktrees), 2)
        self.assertEqual(worktrees[0]["path"], "/path/to/main")
        self.assertEqual(worktrees[0]["branch"], "refs/heads/main")
        self.assertEqual(worktrees[1]["path"], "/path/to/worktree1")
        self.assertEqual(worktrees[1]["branch"], "refs/heads/task/123")


if __name__ == "__main__":
    unittest.main()
