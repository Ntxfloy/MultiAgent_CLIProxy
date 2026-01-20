"""Git worktree manager for task isolation."""

import subprocess
from pathlib import Path
from typing import Optional


class WorktreeManager:
    """Manage git worktrees for task isolation."""
    
    def __init__(self, base_dir: str = ".multiagent/worktrees"):
        """
        Initialize worktree manager.
        
        Args:
            base_dir: Base directory for worktrees
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_worktree(self, task_id: str, base_branch: str = "main") -> Path:
        """
        Create new worktree for task.
        
        Args:
            task_id: Unique task identifier
            base_branch: Base branch to branch from
        
        Returns:
            Path to worktree directory
        """
        worktree_path = self.base_dir / task_id
        branch_name = f"task/{task_id}"
        
        # git worktree add -b task/123 .multiagent/worktrees/task-123 main
        cmd = [
            "git", "worktree", "add",
            "-b", branch_name,
            str(worktree_path),
            base_branch
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        return worktree_path
    
    def commit_checkpoint(self, worktree_path: Path, message: str):
        """
        Create checkpoint commit in worktree.
        
        Args:
            worktree_path: Path to worktree
            message: Commit message
        """
        # git -C <worktree> add -A
        subprocess.run(
            ["git", "-C", str(worktree_path), "add", "-A"],
            check=True, capture_output=True, text=True
        )
        
        # git -C <worktree> commit -m "message"
        subprocess.run(
            ["git", "-C", str(worktree_path), "commit", "-m", message],
            check=True, capture_output=True, text=True
        )
    
    def merge_back(self, task_id: str, target_branch: str = "main", no_commit: bool = True):
        """
        Merge worktree branch back to target.
        
        Args:
            task_id: Task identifier
            target_branch: Target branch to merge into
            no_commit: If True, stage changes without committing (for review)
        """
        branch_name = f"task/{task_id}"
        
        # git checkout main
        subprocess.run(
            ["git", "checkout", target_branch],
            check=True, capture_output=True, text=True
        )
        
        # git merge --no-commit task/123 (or without --no-commit)
        merge_cmd = ["git", "merge"]
        if no_commit:
            merge_cmd.append("--no-commit")
        merge_cmd.append(branch_name)
        
        subprocess.run(merge_cmd, check=True, capture_output=True, text=True)
    
    def cleanup(self, task_id: str, delete_branch: bool = False):
        """
        Remove worktree and optionally delete branch.
        
        Args:
            task_id: Task identifier
            delete_branch: If True, also delete the branch
        """
        worktree_path = self.base_dir / task_id
        branch_name = f"task/{task_id}"
        
        # git worktree remove .multiagent/worktrees/task-123
        subprocess.run(
            ["git", "worktree", "remove", str(worktree_path)],
            check=True, capture_output=True, text=True
        )
        
        if delete_branch:
            # git branch -D task/123
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                check=True, capture_output=True, text=True
            )
    
    def list_worktrees(self) -> list:
        """
        List all worktrees.
        
        Returns:
            List of worktree info dicts
        """
        # git worktree list --porcelain
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            check=True, capture_output=True, text=True
        )
        
        worktrees = []
        current = {}
        
        for line in result.stdout.strip().split("\n"):
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line.split(" ", 1)[1]}
            elif line.startswith("branch "):
                current["branch"] = line.split(" ", 1)[1]
            elif line == "":
                if current:
                    worktrees.append(current)
                    current = {}
        
        if current:
            worktrees.append(current)
        
        return worktrees
