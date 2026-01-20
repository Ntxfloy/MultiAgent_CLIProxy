"""Tests for state store."""

import unittest
import tempfile
import shutil
from pathlib import Path
from core.state_store import StateStore


class TestStateStore(unittest.TestCase):
    """Test StateStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.store = StateStore(state_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load(self):
        """Test saving and loading state."""
        state = {
            "phase": "planning",
            "status": "in_progress",
            "data": {"key": "value"}
        }
        
        self.store.save("test-123", state)
        loaded = self.store.load("test-123")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["phase"], "planning")
        self.assertEqual(loaded["status"], "in_progress")
        self.assertEqual(loaded["task_id"], "test-123")
        self.assertIn("created_at", loaded)
        self.assertIn("updated_at", loaded)
    
    def test_atomic_write(self):
        """Test that writes are atomic."""
        state = {"phase": "test"}
        
        self.store.save("test-456", state)
        
        # Tmp file should not exist after save
        tmp_file = Path(self.test_dir) / "test-456.json.tmp"
        self.assertFalse(tmp_file.exists())
        
        # State file should exist
        state_file = Path(self.test_dir) / "test-456.json"
        self.assertTrue(state_file.exists())
    
    def test_load_nonexistent(self):
        """Test loading nonexistent state."""
        loaded = self.store.load("nonexistent")
        self.assertIsNone(loaded)
    
    def test_exists(self):
        """Test checking if state exists."""
        self.assertFalse(self.store.exists("test-789"))
        
        self.store.save("test-789", {"phase": "test"})
        self.assertTrue(self.store.exists("test-789"))
    
    def test_delete(self):
        """Test deleting state."""
        self.store.save("test-delete", {"phase": "test"})
        self.assertTrue(self.store.exists("test-delete"))
        
        self.store.delete("test-delete")
        self.assertFalse(self.store.exists("test-delete"))
    
    def test_list_tasks(self):
        """Test listing all tasks."""
        self.store.save("task-1", {"phase": "test"})
        self.store.save("task-2", {"phase": "test"})
        self.store.save("task-3", {"phase": "test"})
        
        tasks = self.store.list_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertIn("task-1", tasks)
        self.assertIn("task-2", tasks)
        self.assertIn("task-3", tasks)


if __name__ == "__main__":
    unittest.main()
