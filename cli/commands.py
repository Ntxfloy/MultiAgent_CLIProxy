"""Command implementations for MultiAgent_CLIProxy CLI."""

import json
import os
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_multiagent_dir():
    """Get .multiagent directory path."""
    return get_project_root() / ".multiagent"


def get_config_path():
    """Get config file path."""
    return get_project_root() / ".multiagent" / "config.json"


def cmd_init(args):
    """Initialize configuration."""
    print("🚀 Initializing MultiAgent_CLIProxy...")
    
    # Create .multiagent directory structure
    multiagent_dir = get_multiagent_dir()
    multiagent_dir.mkdir(exist_ok=True)
    (multiagent_dir / "tasks").mkdir(exist_ok=True)
    (multiagent_dir / "worktrees").mkdir(exist_ok=True)
    (multiagent_dir / "logs").mkdir(exist_ok=True)
    
    # Default config
    config = {
        "provider": args.provider,
        "base_url": args.base_url or "http://127.0.0.1:8317/v1",
        "api_key": args.api_key or "test-key-123",
        "models": {
            "architect": "gpt-5.2-codex",
            "reviewer": "gpt-5.2-codex",
            "manager": "gemini-2.5-pro",
            "coder": "gemini-2.5-flash",
            "tester": "gemini-2.5-pro"
        },
        "fallback_chains": {
            "architect": ["gpt-5.2-codex", "gpt-5.1-codex-max", "gemini-2.5-pro"],
            "reviewer": ["gpt-5.2-codex", "gpt-5.1-codex-max", "gemini-2.5-pro"],
            "manager": ["gemini-2.5-pro", "gpt-5.1", "gpt-5.2"],
            "coder": ["gemini-2.5-flash", "gpt-5-codex-mini", "gemini-3-flash-preview"],
            "tester": ["gemini-2.5-pro", "gpt-5.1", "gpt-5.2"]
        },
        "max_iterations": 50,
        "worktree_base": ".multiagent/worktrees"
    }
    
    # Save config
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_path}")
    print(f"   Provider: {config['provider']}")
    print(f"   Base URL: {config['base_url']}")
    print(f"   Models: {len(config['models'])} roles configured")
    
    return 0


def cmd_spec_new(args):
    """Create new task specification."""
    print(f"📝 Creating new specification: {args.name}")
    
    spec_dir = get_project_root() / "specs"
    spec_dir.mkdir(exist_ok=True)
    
    spec_path = spec_dir / f"{args.name}.yaml"
    
    if spec_path.exists():
        print(f"❌ Specification already exists: {spec_path}")
        return 1
    
    # Template spec
    spec_template = f"""# Task Specification: {args.name}
# Created: {datetime.now().isoformat()}

name: {args.name}
description: |
  Brief description of the task

requirements:
  - Requirement 1
  - Requirement 2
  - Requirement 3

constraints:
  - No breaking changes
  - Maintain test coverage
  - Follow existing code style

acceptance_criteria:
  - Criterion 1
  - Criterion 2
  - Criterion 3

files_to_modify:
  - path/to/file1.py
  - path/to/file2.py

files_to_create:
  - path/to/new_file.py

tests_required:
  - Unit tests for new functionality
  - Integration tests if needed

notes: |
  Additional context or notes
"""
    
    with open(spec_path, "w") as f:
        f.write(spec_template)
    
    print(f"✅ Specification created: {spec_path}")
    print(f"   Edit the file to add requirements and constraints")
    
    return 0


def cmd_spec_list(args):
    """List all task specifications."""
    print("📋 Task Specifications:")
    
    spec_dir = get_project_root() / "specs"
    
    if not spec_dir.exists():
        print("   (none)")
        return 0
    
    specs = list(spec_dir.glob("*.yaml"))
    
    if not specs:
        print("   (none)")
        return 0
    
    for spec_path in sorted(specs):
        print(f"   - {spec_path.stem}")
    
    return 0


def cmd_run(args):
    """Execute a task specification."""
    print(f"🚀 Running task: {args.spec_name}")
    print(f"   Max iterations: {args.max_iterations}")
    print()
    print("⚠️  NOT IMPLEMENTED YET")
    print("   This will be implemented in TASK-006 (State Machine Pipeline)")
    print()
    print("   Expected flow:")
    print("   1. Load spec from specs/{args.spec_name}.yaml")
    print("   2. Create worktree for task")
    print("   3. Run state machine: planning → impl → test → review")
    print("   4. QA loop with max iterations")
    print("   5. Merge back to main (--no-commit)")
    
    return 1


def cmd_status(args):
    """Show task status."""
    print("📊 Task Status:")
    
    tasks_dir = get_multiagent_dir() / "tasks"
    
    if not tasks_dir.exists():
        print("   (no tasks)")
        return 0
    
    if args.task_id:
        # Show specific task
        task_file = tasks_dir / f"{args.task_id}.json"
        if not task_file.exists():
            print(f"❌ Task not found: {args.task_id}")
            return 1
        
        with open(task_file) as f:
            state = json.load(f)
        
        print(f"\n   Task ID: {state.get('task_id')}")
        print(f"   Phase: {state.get('phase', 'unknown')}")
        print(f"   Status: {state.get('status', 'unknown')}")
        print(f"   Created: {state.get('created_at', 'unknown')}")
        print(f"   Updated: {state.get('updated_at', 'unknown')}")
    else:
        # Show all tasks
        task_files = list(tasks_dir.glob("*.json"))
        
        if not task_files:
            print("   (no tasks)")
            return 0
        
        for task_file in sorted(task_files):
            with open(task_file) as f:
                state = json.load(f)
            
            task_id = state.get('task_id', task_file.stem)
            phase = state.get('phase', 'unknown')
            status = state.get('status', 'unknown')
            
            print(f"   - {task_id}: {phase} ({status})")
    
    return 0


def cmd_logs(args):
    """Show task logs."""
    print("📜 Task Logs:")
    
    logs_dir = get_multiagent_dir() / "logs"
    
    if not logs_dir.exists():
        print("   (no logs)")
        return 0
    
    if args.task_id:
        log_file = logs_dir / f"{args.task_id}.log"
        if not log_file.exists():
            print(f"❌ Log not found: {args.task_id}")
            return 1
        
        with open(log_file) as f:
            lines = f.readlines()
        
        # Show last N lines
        tail_lines = lines[-args.tail:]
        print()
        for line in tail_lines:
            print(f"   {line.rstrip()}")
    else:
        # Show latest log
        log_files = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not log_files:
            print("   (no logs)")
            return 0
        
        latest_log = log_files[0]
        print(f"   Latest: {latest_log.name}")
        
        with open(latest_log) as f:
            lines = f.readlines()
        
        tail_lines = lines[-args.tail:]
        print()
        for line in tail_lines:
            print(f"   {line.rstrip()}")
    
    return 0


def cmd_worktree_list(args):
    """List all worktrees."""
    print("🌳 Git Worktrees:")
    print()
    print("⚠️  NOT IMPLEMENTED YET")
    print("   This will be implemented in TASK-002 (Worktree Manager)")
    print()
    print("   Expected output:")
    print("   - task-123: .multiagent/worktrees/task-123 (branch: task/123)")
    print("   - task-456: .multiagent/worktrees/task-456 (branch: task/456)")
    
    return 1


def cmd_resume(args):
    """Resume interrupted task."""
    print(f"🔄 Resuming task: {args.task_id}")
    print()
    print("⚠️  NOT IMPLEMENTED YET")
    print("   This will be implemented in TASK-007 (Crash Recovery)")
    print()
    print("   Expected flow:")
    print("   1. Load state from .multiagent/tasks/{args.task_id}.json")
    print("   2. Restore worktree")
    print("   3. Continue from last phase")
    
    return 1
