#!/usr/bin/env python3
"""
MultiAgent_CLIProxy CLI - Main entrypoint

Usage:
    multiagent init [--provider cliproxy] [--base-url URL]
    multiagent spec new <name>
    multiagent spec list
    multiagent run <spec-name>
    multiagent status [<task-id>]
    multiagent logs [<task-id>]
    multiagent worktree list
    multiagent resume <task-id>
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands import (
    cmd_init,
    cmd_spec_new,
    cmd_spec_list,
    cmd_run,
    cmd_status,
    cmd_logs,
    cmd_worktree_list,
    cmd_resume,
)


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="multiagent",
        description="Auto-Claude-like autonomous coding framework (CLI-first, provider-agnostic)",
    )
    parser.add_argument("--version", action="version", version="1.0.0-alpha")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize configuration"
    )
    init_parser.add_argument(
        "--provider",
        default="cliproxy",
        choices=["cliproxy", "openai", "custom"],
        help="Model provider (default: cliproxy)"
    )
    init_parser.add_argument(
        "--base-url",
        help="Base URL for API (default: http://127.0.0.1:8317/v1)"
    )
    init_parser.add_argument(
        "--api-key",
        help="API key (default: test-key-123)"
    )
    
    # spec commands
    spec_parser = subparsers.add_parser(
        "spec",
        help="Manage task specifications"
    )
    spec_subparsers = spec_parser.add_subparsers(dest="spec_command")
    
    spec_new_parser = spec_subparsers.add_parser(
        "new",
        help="Create new task specification"
    )
    spec_new_parser.add_argument("name", help="Task name (e.g., 'add-auth')")
    
    spec_list_parser = spec_subparsers.add_parser(
        "list",
        help="List all task specifications"
    )
    
    # run command
    run_parser = subparsers.add_parser(
        "run",
        help="Execute a task specification"
    )
    run_parser.add_argument("spec_name", help="Specification name to run")
    run_parser.add_argument(
        "--max-iterations",
        type=int,
        default=50,
        help="Max QA loop iterations (default: 50)"
    )
    
    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show task status"
    )
    status_parser.add_argument(
        "task_id",
        nargs="?",
        help="Task ID (optional, shows all if omitted)"
    )
    
    # logs command
    logs_parser = subparsers.add_parser(
        "logs",
        help="Show task logs"
    )
    logs_parser.add_argument(
        "task_id",
        nargs="?",
        help="Task ID (optional, shows latest if omitted)"
    )
    logs_parser.add_argument(
        "--tail",
        type=int,
        default=50,
        help="Number of lines to show (default: 50)"
    )
    
    # worktree command
    worktree_parser = subparsers.add_parser(
        "worktree",
        help="Manage git worktrees"
    )
    worktree_subparsers = worktree_parser.add_subparsers(dest="worktree_command")
    
    worktree_list_parser = worktree_subparsers.add_parser(
        "list",
        help="List all worktrees"
    )
    
    # resume command
    resume_parser = subparsers.add_parser(
        "resume",
        help="Resume interrupted task"
    )
    resume_parser.add_argument("task_id", help="Task ID to resume")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handlers
    try:
        if args.command == "init":
            return cmd_init(args)
        elif args.command == "spec":
            if args.spec_command == "new":
                return cmd_spec_new(args)
            elif args.spec_command == "list":
                return cmd_spec_list(args)
            else:
                spec_parser.print_help()
                return 1
        elif args.command == "run":
            return cmd_run(args)
        elif args.command == "status":
            return cmd_status(args)
        elif args.command == "logs":
            return cmd_logs(args)
        elif args.command == "worktree":
            if args.worktree_command == "list":
                return cmd_worktree_list(args)
            else:
                worktree_parser.print_help()
                return 1
        elif args.command == "resume":
            return cmd_resume(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
