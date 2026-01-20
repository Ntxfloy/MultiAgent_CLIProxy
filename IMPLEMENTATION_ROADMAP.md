# Implementation Roadmap: First 10 Commits

## Overview

This document provides the exact sequence of commits to transform MultiAgent_CLIProxy into a production-ready system. Each commit is atomic, testable, and builds on the previous one.

---

## Commit 1: Project Structure & CLI Foundation

**Branch:** `feature/cli-foundation`

**Changes:**
```
CREATE cli/
CREATE cli/__init__.py
CREATE cli/main.py          # Argparse-based CLI router
CREATE cli/commands.py       # Command implementations
CREATE core/
CREATE core/__init__.py
MODIFY run_factory.py        # Keep as legacy, add deprecation notice
CREATE .multiagent/          # Hidden directory for state
CREATE .multiagent/.gitignore
```

**Files:**

`cli/main.py`:
```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog="multiagent")
    subparsers = parser.add_subparsers(dest="command")
    
    # init
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--provider", default="cliproxy")
    init_parser.add_argument("--base-url")
    
    # spec
    spec_parser = subparsers.add_parser("spec")
    spec_sub = spec_parser.add_subparsers(dest="spec_command")
    spec_sub.add_parser("list")
    spec_new = spec_sub.add_parser("new")
    spec_new.add_argument("name")
    
    # run
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("spec_name")
    run_parser.add_argument("--isolated", action="store_true")
    
    args = parser.parse_args()
    
    if args.command == "init":
        from cli.commands import cmd_init
        cmd_init(args)
    elif args.command == "spec":
        from cli.commands import cmd_spec
        cmd_spec(args)
    elif args.command == "run":
        from cli.commands import cmd_run
        cmd_run(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

**Test:** `python -m cli.main --help` should show commands

**Duration:** 2 hours

---

## Commit 2: Worktree Manager (Core Isolation)

**Branch:** `feature/worktree-manager`

**Changes:**
```
CREATE core/worktree.py      # WorktreeManager class
CREATE core/exceptions.py    # Custom exceptions
MODIFY cli/commands.py       # Add worktree commands
```

**Key Implementation:**
- `WorktreeManager.create_worktree(spec_name)` → creates `.multiagent/worktrees/{spec}/`
- `WorktreeManager.merge_worktree(spec_name)` → merges back to main
- `WorktreeManager.list_worktrees()` → lists all active worktrees

**Test:**
```bash
cd test-project
python -m cli.main init
python -m cli.main spec new test-spec
# Should create .multiagent/specs/test-spec/
```

**Duration:** 4 hours

---

## Commit 3: Shell Runner with Security

**Branch:** `feature/shell-runner`

**Changes:**
```
CREATE core/shell_runner.py  # ShellRunner class
CREATE core/stack_detector.py # StackDetector class
CREATE .multiagent-allowlist.example
MODIFY core/worktree.py      # Integrate shell runner
```

**Key Implementation:**
- `ShellRunner.execute(command)` → validates + executes
- `ShellRunner.validate_command(command)` → allowlist check
- `StackDetector.detect_stack()` → auto-detect commands

**Test:**
```python
runner = ShellRunner(Path.cwd())
result = runner.execute("ls -la")  # Should work
result = runner.execute("rm -rf /")  # Should raise SecurityError
```

**Duration:** 4 hours

---

## Commit 4: Model Client Interface

**Branch:** `feature/model-client`

**Changes:**
```
CREATE core/model_client.py  # Abstract ModelClient
CREATE core/providers/
CREATE core/providers/__init__.py
CREATE core/providers/openai_compatible.py
MODIFY config.py             # Add provider config
```

**Key Implementation:**
- Abstract `ModelClient` interface
- `OpenAICompatibleProvider` implementation
- Support for tools, JSON mode

**Test:**
```python
client = OpenAICompatibleProvider(
    base_url="http://127.0.0.1:8317/v1",
    api_key="test-key-123",
    model="gpt-5.2-codex"
)
response = await client.complete([
    ModelMessage(role="user", content="Say hello")
])
assert response.content
```

**Duration:** 3 hours

---

## Commit 5: Basic QA Loop

**Branch:** `feature/qa-loop`

**Changes:**
```
CREATE core/qa_loop.py       # QALoop class
CREATE prompts/
CREATE prompts/qa_reviewer.md
CREATE prompts/qa_fixer.md
MODIFY cli/commands.py       # Add qa command
```

**Key Implementation:**
- `QALoop.run_validation_loop()` → reviewer + fixer cycle
- JSON-based approval protocol
- Iteration tracking

**Test:**
```bash
# Create test spec with simple task
python -m cli.main run test-spec --isolated
# Should run QA loop, create qa_report.json
```

**Duration:** 5 hours

---

## Commit 6: Implementation Plan & State Machine

**Branch:** `feature/state-machine`

**Changes:**
```
CREATE core/orchestrator.py  # StateOrchestrator class
CREATE core/implementation_plan.py # Plan management
CREATE core/phases.py        # Phase definitions
MODIFY cli/commands.py       # Use orchestrator in run command
```

**Key Implementation:**
- State machine: PLANNING → IMPLEMENTATION → TESTING → QA_REVIEW → COMPLETE
- `implementation_plan.json` format
- Phase transitions with validation

**Test:**
```bash
python -m cli.main run complex-spec --isolated
# Should create implementation_plan.json with phases
# Should execute phases in order
```

**Duration:** 6 hours

---

## Commit 7: Fallback & Retry Logic

**Branch:** `feature/fallback-retry`

**Changes:**
```
CREATE core/model_client_with_fallback.py
MODIFY config.py             # Add fallback chains
MODIFY core/orchestrator.py  # Use fallback client
```

**Key Implementation:**
- `ModelClientWithFallback` wraps primary + fallback clients
- Exponential backoff on rate limits
- Automatic client switching on errors

**Test:**
```python
# Mock primary client to fail
# Should automatically use fallback
```

**Duration:** 3 hours

---

## Commit 8: Crash Recovery

**Branch:** `feature/crash-recovery`

**Changes:**
```
CREATE core/recovery.py      # Recovery detection
MODIFY cli/commands.py       # Add resume command
MODIFY core/orchestrator.py  # Checkpoint after each phase
```

**Key Implementation:**
- Detect interrupted sessions on startup
- Offer resume/discard options
- Save checkpoints after each phase

**Test:**
```bash
python -m cli.main run test-spec --isolated
# Kill process mid-execution
python -m cli.main resume test-spec
# Should continue from last checkpoint
```

**Duration:** 4 hours

---

## Commit 9: Logging & Debugging

**Branch:** `feature/logging`

**Changes:**
```
CREATE core/logger.py        # Structured logger
MODIFY all core/*.py         # Add logging calls
CREATE cli/debug.py          # Debug commands
```

**Key Implementation:**
- Phase-based logging
- Secret redaction
- Log rotation
- Debug command to view state

**Test:**
```bash
python -m cli.main logs test-spec --tail 50
python -m cli.main debug test-spec --show-state
```

**Duration:** 3 hours

---

## Commit 10: Integration Tests & Documentation

**Branch:** `feature/tests-docs`

**Changes:**
```
CREATE tests/
CREATE tests/test_worktree.py
CREATE tests/test_shell_runner.py
CREATE tests/test_qa_loop.py
CREATE tests/test_orchestrator.py
UPDATE README.md             # Complete usage guide
CREATE ARCHITECTURE.md       # System design doc
```

**Key Implementation:**
- Unit tests for each core module
- Integration test: full task execution
- Documentation with examples

**Test:**
```bash
pytest tests/ -v
# All tests should pass
```

**Duration:** 6 hours

---

## Total Effort: 40 hours (1 week)

## Migration from Current Codebase

### Keep (Reuse)
- `config.py` - Extend with new provider config
- `requirements.txt` - Add new dependencies
- `agents/registry_v3.py` - Convert to prompt templates
- `core/resilient_client.py` - Merge into fallback logic

### Refactor
- `run_factory.py` → `cli/commands.py` (cmd_run)
- `core/swarm.py` → `core/orchestrator.py` (state machine)
- `tools/file_ops.py` → integrate into ShellRunner

### Remove
- `test_all_models.py` - Replace with provider tests
- `core/engine.py` - Unused, remove

### New Structure
```
MultiAgent_CLIProxy/
├── cli/
│   ├── __init__.py
│   ├── main.py
│   ├── commands.py
│   └── debug.py
├── core/
│   ├── __init__.py
│   ├── worktree.py
│   ├── shell_runner.py
│   ├── stack_detector.py
│   ├── model_client.py
│   ├── orchestrator.py
│   ├── qa_loop.py
│   ├── implementation_plan.py
│   ├── recovery.py
│   ├── logger.py
│   └── providers/
│       ├── __init__.py
│       └── openai_compatible.py
├── prompts/
│   ├── planner.md
│   ├── coder.md
│   ├── qa_reviewer.md
│   └── qa_fixer.md
├── tests/
│   ├── test_worktree.py
│   ├── test_shell_runner.py
│   ├── test_qa_loop.py
│   └── test_orchestrator.py
├── .multiagent/
│   ├── config.yaml
│   ├── specs/
│   └── worktrees/
├── config.py (legacy, deprecated)
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

---

## Definition of Done (V1)

### Functional Requirements
- ✅ Can create spec via CLI
- ✅ Can run task in isolated worktree
- ✅ QA loop validates with JSON protocol
- ✅ Can merge worktree back to main
- ✅ Crash recovery works
- ✅ Commands execute safely (allowlist)
- ✅ Fallback to alternative models works

### Quality Requirements
- ✅ 80%+ test coverage
- ✅ All core modules have unit tests
- ✅ Integration test passes end-to-end
- ✅ Documentation complete
- ✅ No known critical bugs

### Performance Requirements
- ✅ Can handle 3-5 parallel tasks
- ✅ Worktree creation < 5s
- ✅ QA iteration < 2 min
- ✅ Full task completion < 30 min (simple task)

---

## 10 Most Likely Failures & Mitigations

### 1. **Git Worktree Conflicts**
**Failure:** Two specs try to create same branch name  
**Mitigation:** Use unique branch names: `multiagent/{spec-name}-{timestamp}`

### 2. **Model Rate Limits**
**Failure:** Hit rate limit, all fallbacks exhausted  
**Mitigation:** Exponential backoff + queue system + user notification

### 3. **QA Loop Infinite Iteration**
**Failure:** QA never approves, hits 50 iterations  
**Mitigation:** Escalation file + human review prompt + iteration history

### 4. **Shell Command Injection**
**Failure:** Agent crafts malicious command that bypasses allowlist  
**Mitigation:** Regex validation + argument parsing + path restrictions

### 5. **Disk Space Exhaustion**
**Failure:** Too many worktrees fill disk  
**Mitigation:** Auto-cleanup old worktrees + disk usage warnings + size limits

### 6. **Merge Conflicts**
**Failure:** Worktree merge conflicts with main  
**Mitigation:** Abort merge + notify user + manual resolution guide

### 7. **State Corruption**
**Failure:** implementation_plan.json becomes invalid  
**Mitigation:** JSON schema validation + backup before write + recovery mode

### 8. **Network Failures**
**Failure:** API endpoint unreachable mid-task  
**Mitigation:** Retry logic + checkpoint state + resume capability

### 9. **Tool Call Parsing Errors**
**Failure:** Model returns malformed tool calls  
**Mitigation:** Strict JSON validation + error feedback to model + retry

### 10. **Memory Leaks**
**Failure:** Long-running tasks consume too much memory  
**Mitigation:** Process isolation + memory limits + periodic restarts

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Set up development environment**
3. **Create feature branches** for each commit
4. **Start with Commit 1** (CLI foundation)
5. **Test each commit** before moving to next
6. **Dogfood early** - use the system to build itself
7. **Iterate based on feedback**

**Target:** V1 ready in 3-4 weeks


---

# UPDATED ROADMAP (After Deep Analysis)

## Critical Implementation Details

### Commit 2 (UPDATED): Worktree Manager - Production Version

**Time:** 8-10 hours (increased from 4h due to complexity)

**Why longer:** Auto-Claude's worktree manager is 1405 lines with critical features we missed.

```python
# core/worktree_manager.py

import subprocess
import time
from pathlib import Path, PurePosixPath, PureWindowsPath

class WorktreeManager:
    """Git worktree isolation with production features."""
    
    def __init__(self, project_dir: Path, base_branch: str = "main"):
        self.project_dir = project_dir
        self.base_branch = base_branch or self._detect_base_branch()
        self.worktrees_dir = project_dir / ".multiagent/worktrees"
    
    def _detect_base_branch(self) -> str:
        """
        Detect base branch with priority:
        1. DEFAULT_BRANCH env var
        2. Auto-detect main/master
        3. Current branch (with warning)
        """
        # Check env var
        env_branch = os.getenv("DEFAULT_BRANCH")
        if env_branch:
            result = run_git(["rev-parse", "--verify", env_branch])
            if result.returncode == 0:
                return env_branch
        
        # Auto-detect main/master
        for branch in ["main", "master"]:
            result = run_git(["rev-parse", "--verify", branch])
            if result.returncode == 0:
                return branch
        
        # Fallback to current
        current = run_git(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
        print(f"Warning: Using current branch '{current}' as base")
        return current
    
    def _check_branch_namespace_conflict(self) -> str | None:
        """
        Check if 'multiagent' branch exists (blocks 'multiagent/*').
        """
        result = run_git(["rev-parse", "--verify", "multiagent"])
        if result.returncode == 0:
            return "multiagent"
        return None
    
    def create_worktree(self, task_id: str) -> Path:
        """Create worktree from remote (source of truth)."""
        worktree_path = self.worktrees_dir / task_id
        branch_name = f"multiagent/{task_id}"
        
        # Check for namespace conflict
        conflicting = self._check_branch_namespace_conflict()
        if conflicting:
            raise WorktreeError(
                f"Branch '{conflicting}' blocks creating 'multiagent/*' branches.\n"
                f"Fix: git branch -m {conflicting} {conflicting}-backup"
            )
        
        # Remove existing if present
        if worktree_path.exists():
            run_git(["worktree", "remove", "--force", str(worktree_path)])
        
        # Delete branch if exists
        run_git(["branch", "-D", branch_name])
        
        # CRITICAL: Fetch latest from remote
        print(f"Fetching latest {self.base_branch} from origin...")
        fetch_result = run_git(["fetch", "origin", self.base_branch])
        if fetch_result.returncode != 0:
            print(f"Warning: Could not fetch from origin: {fetch_result.stderr}")
        
        # CRITICAL: Use origin/{base_branch}, not local branch
        remote_ref = f"origin/{self.base_branch}"
        check_remote = run_git(["rev-parse", "--verify", remote_ref])
        
        if check_remote.returncode == 0:
            start_point = remote_ref
            print(f"Creating worktree from remote: {remote_ref}")
        else:
            start_point = self.base_branch
            print(f"Remote not found, using local: {self.base_branch}")
        
        # Create worktree
        result = run_git([
            "worktree", "add", "-b", branch_name,
            str(worktree_path), start_point
        ])
        
        if result.returncode != 0:
            raise WorktreeError(f"Failed to create worktree: {result.stderr}")
        
        print(f"Created worktree: {worktree_path.name} on branch {branch_name}")
        return worktree_path
    
    def _unstage_gitignored_files(self):
        """
        CRITICAL: Unstage gitignored files after --no-commit merge.
        Prevents .multiagent/ files from leaking to main.
        """
        # Get staged files
        result = run_git(["diff", "--cached", "--name-only"])
        if result.returncode != 0 or not result.stdout.strip():
            return
        
        staged_files = result.stdout.strip().split("\n")
        files_to_unstage = set()
        
        # Check which files are gitignored
        check_result = run_git(
            ["check-ignore", "--stdin"],
            input_data="\n".join(staged_files)
        )
        
        if check_result.stdout.strip():
            for file in check_result.stdout.strip().split("\n"):
                if file.strip():
                    files_to_unstage.add(file.strip())
        
        # ALWAYS unstage .multiagent/ files
        for file in staged_files:
            file = file.strip()
            if not file:
                continue
            # Normalize path separators (Windows support)
            normalized = file.replace("\\", "/")
            if normalized.startswith(".multiagent/"):
                files_to_unstage.add(file)
        
        if files_to_unstage:
            print(f"Unstaging {len(files_to_unstage)} gitignored file(s)...")
            for file in files_to_unstage:
                run_git(["reset", "HEAD", "--", file])
    
    def merge_worktree(self, task_id: str, no_commit: bool = False) -> bool:
        """Merge worktree back to base branch."""
        worktree_path = self.worktrees_dir / task_id
        if not worktree_path.exists():
            print(f"No worktree found: {task_id}")
            return False
        
        branch_name = f"multiagent/{task_id}"
        
        # Switch to base branch
        current = run_git(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
        if current != self.base_branch:
            result = run_git(["checkout", self.base_branch])
            if result.returncode != 0:
                print(f"Error: Could not checkout {self.base_branch}")
                return False
        
        # Merge
        merge_args = ["merge", "--no-ff", branch_name]
        if no_commit:
            merge_args.append("--no-commit")
        else:
            merge_args.extend(["-m", f"multiagent: {task_id}"])
        
        result = run_git(merge_args)
        
        if result.returncode != 0:
            output = (result.stdout + result.stderr).lower()
            if "already up to date" in output:
                print(f"Branch {branch_name} is already up to date.")
                return True
            if "conflict" in output:
                print("Merge conflict! Aborting...")
                run_git(["merge", "--abort"])
                return False
            print(f"Merge failed: {result.stderr}")
            run_git(["merge", "--abort"])
            return False
        
        if no_commit:
            # CRITICAL: Unstage gitignored files
            self._unstage_gitignored_files()
            print(f"Changes from {branch_name} staged. Review and commit when ready.")
        else:
            print(f"Successfully merged {branch_name}")
        
        return True
    
    def remove_worktree(self, task_id: str, delete_branch: bool = False):
        """Remove worktree and optionally delete branch."""
        worktree_path = self.worktrees_dir / task_id
        branch_name = f"multiagent/{task_id}"
        
        if worktree_path.exists():
            result = run_git(["worktree", "remove", "--force", str(worktree_path)])
            if result.returncode == 0:
                print(f"Removed worktree: {task_id}")
            else:
                print(f"Warning: Could not remove worktree: {result.stderr}")
                import shutil
                shutil.rmtree(worktree_path, ignore_errors=True)
        
        if delete_branch:
            run_git(["branch", "-D", branch_name])
            print(f"Deleted branch: {branch_name}")
        
        run_git(["worktree", "prune"])

def run_git(args: list[str], cwd: Path = None, input_data: str = None, timeout: int = 60):
    """Run git command with timeout."""
    cmd = ["git"] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=True,
            text=True,
            input=input_data,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            cmd, -1, "", f"Command timed out after {timeout}s"
        )

class WorktreeError(Exception):
    """Worktree operation error."""
    pass
```

**Tests:**
```python
# tests/test_worktree.py

def test_create_worktree_from_remote():
    """Test worktree created from remote, not local."""
    mgr = WorktreeManager(Path("/tmp/test"))
    worktree = mgr.create_worktree("test-001")
    
    # Check branch points to origin/main
    result = run_git(["rev-parse", "HEAD"], cwd=worktree)
    local_sha = result.stdout.strip()
    
    result = run_git(["rev-parse", "origin/main"])
    remote_sha = result.stdout.strip()
    
    assert local_sha == remote_sha

def test_unstage_gitignored_files():
    """Test gitignored files are unstaged after merge."""
    mgr = WorktreeManager(Path("/tmp/test"))
    
    # Create worktree and add .multiagent/ file
    worktree = mgr.create_worktree("test-002")
    (worktree / ".multiagent/task.json").write_text("{}")
    run_git(["add", "."], cwd=worktree)
    run_git(["commit", "-m", "test"], cwd=worktree)
    
    # Merge with --no-commit
    mgr.merge_worktree("test-002", no_commit=True)
    
    # Check .multiagent/ file is NOT staged
    result = run_git(["diff", "--cached", "--name-only"])
    assert ".multiagent/" not in result.stdout

def test_branch_namespace_conflict():
    """Test detection of branch namespace conflict."""
    # Create conflicting branch
    run_git(["branch", "multiagent"])
    
    mgr = WorktreeManager(Path("/tmp/test"))
    
    with pytest.raises(WorktreeError, match="blocks creating"):
        mgr.create_worktree("test-003")
```

---

### Commit 3 (UPDATED): Security System - Production Version

**Time:** 8-10 hours (increased from 4h)

**Why longer:** Need cross-platform parser, fallback parser, stack detection, 10+ validators.

```python
# core/security.py

import re
import shlex
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Command validation result."""
    allowed: bool
    reason: str = ""

class SecurityManager:
    """Command validation with 3-layer architecture."""
    
    BASE_COMMANDS = {
        "ls", "cat", "grep", "find", "echo", "pwd",
        "mkdir", "touch", "cp", "mv", "head", "tail",
        "wc", "sort", "uniq", "diff", "git"
    }
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.stack_commands = self._detect_stack()
        self.validators = self._load_validators()
    
    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate command for execution."""
        # Extract commands
        commands = self._extract_commands(command)
        
        if not commands:
            return False, "Could not parse command"
        
        for cmd in commands:
            # Check allowlist
            if not self._is_allowed(cmd):
                return False, f"Command not allowed: {cmd}"
            
            # Run validator
            if cmd in self.validators:
                result = self.validators[cmd](command)
                if not result.allowed:
                    return False, result.reason
        
        return True, ""
    
    def _is_allowed(self, cmd: str) -> bool:
        """Check if command in allowlist."""
        return (
            cmd in self.BASE_COMMANDS or
            cmd in self.stack_commands
        )
    
    def _detect_stack(self) -> set[str]:
        """Auto-detect project stack."""
        commands = set()
        
        # Node.js
        if (self.project_dir / "package.json").exists():
            commands.update(["npm", "node", "npx", "yarn", "pnpm"])
            
            # Check for frameworks
            try:
                pkg = json.loads((self.project_dir / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                if "vite" in deps:
                    commands.add("vite")
                if "next" in deps:
                    commands.add("next")
            except:
                pass
        
        # Python
        if (self.project_dir / "requirements.txt").exists():
            commands.update(["python", "python3", "pip", "pytest"])
        
        if (self.project_dir / "pyproject.toml").exists():
            commands.update(["poetry", "pdm"])
        
        # Rust
        if (self.project_dir / "Cargo.toml").exists():
            commands.update(["cargo", "rustc"])
        
        # Docker
        if (self.project_dir / "Dockerfile").exists():
            commands.update(["docker", "docker-compose"])
        
        return commands
    
    def _extract_commands(self, command_string: str) -> list[str]:
        """Extract command names with fallback parser."""
        # Check for Windows paths
        if self._contains_windows_path(command_string):
            return self._fallback_extract_commands(command_string)
        
        try:
            tokens = shlex.split(command_string)
        except ValueError:
            # Malformed - use fallback
            return self._fallback_extract_commands(command_string)
        
        commands = []
        expect_command = True
        
        for token in tokens:
            if token in ("|", "||", "&&", "&"):
                expect_command = True
            elif expect_command and not token.startswith("-"):
                cmd = self._cross_platform_basename(token)
                commands.append(cmd)
                expect_command = False
        
        return commands
    
    def _cross_platform_basename(self, path: str) -> str:
        """Extract basename from Windows OR POSIX path."""
        path = path.strip("'\"")
        
        # Windows path?
        if "\\" in path or (len(path) >= 2 and path[1] == ":"):
            return PureWindowsPath(path).name
        
        return PurePosixPath(path).name
    
    def _contains_windows_path(self, command: str) -> bool:
        """Check if command contains Windows paths."""
        return bool(re.search(r"[A-Za-z]:\\|\\[A-Za-z][A-Za-z0-9_\\/]", command))
    
    def _fallback_extract_commands(self, command_string: str) -> list[str]:
        """Fallback parser for malformed commands."""
        parts = re.split(r"\s*(?:&&|\|\||\|)\s*|;\s*", command_string)
        
        commands = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Skip variable assignments
            part = re.sub(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", part)
            
            # Extract first token
            match = re.match(r'^(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))', part)
            if match:
                token = match.group(1) or match.group(2) or match.group(3)
                cmd = self._cross_platform_basename(token)
                commands.append(cmd)
        
        return commands
    
    def _load_validators(self) -> dict:
        """Load command validators."""
        return {
            "git": self._validate_git,
            "rm": self._validate_rm,
            "chmod": self._validate_chmod,
            "pkill": self._validate_pkill,
        }
    
    def _validate_git(self, command: str) -> ValidationResult:
        """Validate git commands."""
        if "git config" in command:
            return ValidationResult(False, "git config not allowed")
        return ValidationResult(True)
    
    def _validate_rm(self, command: str) -> ValidationResult:
        """Validate rm commands."""
        dangerous = ["rm -rf /", "rm -rf ~", "rm -rf *"]
        for pattern in dangerous:
            if pattern in command:
                return ValidationResult(False, f"Dangerous: {pattern}")
        return ValidationResult(True)
    
    def _validate_chmod(self, command: str) -> ValidationResult:
        """Validate chmod commands."""
        if "chmod 777" in command:
            return ValidationResult(False, "chmod 777 is insecure")
        return ValidationResult(True)
    
    def _validate_pkill(self, command: str) -> ValidationResult:
        """Validate pkill commands."""
        if "pkill -9" in command:
            return ValidationResult(False, "pkill -9 is too aggressive")
        return ValidationResult(True)
```

**Tests:**
```python
# tests/test_security.py

def test_cross_platform_basename():
    """Test basename extraction from Windows and POSIX paths."""
    security = SecurityManager(Path("/tmp/test"))
    
    # Windows paths
    assert security._cross_platform_basename("C:\\Python\\python.exe") == "python.exe"
    assert security._cross_platform_basename("D:\\tools\\npm.cmd") == "npm.cmd"
    
    # POSIX paths
    assert security._cross_platform_basename("/usr/bin/python") == "python"
    assert security._cross_platform_basename("./node_modules/.bin/vite") == "vite"

def test_fallback_parser():
    """Test fallback parser for malformed commands."""
    security = SecurityManager(Path("/tmp/test"))
    
    # Unclosed quote (shlex fails)
    commands = security._extract_commands('echo "hello')
    assert "echo" in commands
    
    # Windows path (shlex fails)
    commands = security._extract_commands('C:\\Python\\python.exe --version')
    assert "python.exe" in commands

def test_stack_detection():
    """Test auto-detection of project stack."""
    # Create test project
    project_dir = Path("/tmp/test-project")
    project_dir.mkdir(exist_ok=True)
    
    # Add package.json
    (project_dir / "package.json").write_text('{"dependencies": {"vite": "^4.0.0"}}')
    
    security = SecurityManager(project_dir)
    
    # Check detected commands
    assert "npm" in security.stack_commands
    assert "node" in security.stack_commands
    assert "vite" in security.stack_commands

def test_validate_dangerous_commands():
    """Test validation of dangerous commands."""
    security = SecurityManager(Path("/tmp/test"))
    
    # Dangerous rm
    allowed, reason = security.validate_command("rm -rf /")
    assert not allowed
    assert "Dangerous" in reason
    
    # Dangerous chmod
    allowed, reason = security.validate_command("chmod 777 file.txt")
    assert not allowed
    assert "insecure" in reason
    
    # Safe commands
    allowed, _ = security.validate_command("ls -la")
    assert allowed
```

