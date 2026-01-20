"""State persistence with atomic writes."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class StateStore:
    """Manage task state with atomic writes."""
    
    def __init__(self, state_dir: str = ".multiagent/tasks"):
        """
        Initialize state store.
        
        Args:
            state_dir: Directory for state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, task_id: str, state: Dict[str, Any]):
        """
        Save state atomically (tmp + rename).
        
        Args:
            task_id: Task identifier
            state: State dictionary
        """
        state_file = self.state_dir / f"{task_id}.json"
        tmp_file = self.state_dir / f"{task_id}.json.tmp"
        
        # Add metadata
        state["task_id"] = task_id
        state["updated_at"] = datetime.now().isoformat()
        
        if "created_at" not in state:
            state["created_at"] = state["updated_at"]
        
        # Write to tmp file
        with open(tmp_file, "w") as f:
            json.dump(state, f, indent=2)
        
        # Atomic rename
        os.replace(tmp_file, state_file)
    
    def load(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Load state from file.
        
        Args:
            task_id: Task identifier
        
        Returns:
            State dictionary or None if not found
        """
        state_file = self.state_dir / f"{task_id}.json"
        
        if not state_file.exists():
            return None
        
        with open(state_file) as f:
            return json.load(f)
    
    def exists(self, task_id: str) -> bool:
        """Check if state exists."""
        return (self.state_dir / f"{task_id}.json").exists()
    
    def delete(self, task_id: str):
        """Delete state file."""
        state_file = self.state_dir / f"{task_id}.json"
        if state_file.exists():
            state_file.unlink()
    
    def list_tasks(self) -> list:
        """List all task IDs."""
        return [f.stem for f in self.state_dir.glob("*.json") if not f.name.endswith(".tmp")]
