# Deep Analysis: Auto-Claude Architecture

## Executive Summary

После глубокого изучения Auto-Claude (50K+ LOC, 1544 файла), выявлены **критические архитектурные паттерны**, которые делают систему production-ready:

### 🎯 Ключевые открытия

1. **State Machine с фазами** - не просто "запустить агента", а строгий пайплайн: planning → implementation → test → review → iterate
2. **Worktree изоляция** - каждая задача в отдельном git worktree с автокоммитами
3. **Structured QA Loop** - JSON-протокол валидации с recurring issue detection
4. **3-layer Security** - parser → validator → profile (allowlist + stack detection)
5. **Crash Recovery** - checkpoint/resume через implementation_plan.json
6. **Memory System** - Graphiti для cross-session learning
7. **Provider Abstraction** - через ClaudeSDKClient (легко адаптировать)

### ❌ Что НЕ нужно копировать

- Electron UI (мы делаем CLI)
- Claude Code OAuth (мы провайдер-агностичны)
- Linear/GitHub интеграции (опционально потом)
- Graphiti memory (сложно, можно упростить)

### ✅ Что КРИТИЧНО взять

1. **Worktree Manager** - полная изоляция задач
2. **QA Loop** - structured validation с JSON
3. **Security System** - command validation
4. **State Machine** - phase-based execution
5. **Implementation Plan** - subtask tracking

---

##
 1. Worktree Architecture (КРИТИЧНО)

### Как работает в Auto-Claude

```python
# apps/backend/core/worktree.py (1405 строк!)

class WorktreeManager:
    def __init__(self, project_dir, base_branch):
        self.worktrees_dir = project_dir / ".auto-claude/worktrees/tasks"
        self.base_branch = base_branch or self._detect_base_branch()
    
    def create_worktree(self, spec_name):
        # 1. Создаёт worktree: .auto-claude/worktrees/tasks/{spec-name}/
        # 2. Создаёт branch: auto-claude/{spec-name}
        # 3. Базируется на origin/{base_branch} (remote preferred!)
        worktree_path = self.worktrees_dir / spec_name
        branch_name = f"auto-claude/{spec_name}"
        
        # Fetch latest from remote (GitHub = source of truth)
        self._run_git(["fetch", "origin", self.base_branch])
        
        # Create worktree from remote ref
        self._run_git([
            "worktree", "add", "-b", branch_name,
            str(worktree_path), f"origin/{self.base_branch}"
        ])
    
    def merge_worktree(self, spec_name, no_commit=False):
        # Merge с --no-commit для review в IDE
        # Автоматически unstage gitignored files!
        if no_commit:
            self._run_git(["merge", "--no-ff", "--no-commit", branch])
            self._unstage_gitignored_files()  # ВАЖНО!
    
    def _unstage_gitignored_files(self):
        # Убирает из stage файлы, которые gitignored в main
        # Например, .auto-claude/specs/* не должны попасть в main
        staged = self._run_git(["diff", "--cached", "--name-only"])
        for file in staged:
            if self._is_gitignored(file) or file.startswith(".auto-claude/"):
                self._run_git(["reset", "HEAD", "--", file])
```

### Почему это критично

1. **Zero file conflicts** - каждая задача в своём worktree
2. **Parallel execution** - можно работать над 3-5 задачами одновременно
3. **Safe merge** - `--no-commit` позволяет review перед коммитом
4. **Clean state** - gitignored files не попадают в main

### Что взять для CLI

```python
# core/worktree_manager.py (упрощённая версия)

class WorktreeManager:
    """Manages git worktrees for task isolation."""
    
    def __init__(self, project_dir: Path, base_branch: str = "main"):
        self.project_dir = project_dir
        self.base_branch = base_branch
        self.worktrees_dir = project_dir / ".multiagent/worktrees"
    
    def create_worktree(self, task_id: str) -> Path:
        """Create isolated worktree for task."""
        worktree_path = self.worktrees_dir / task_id
        branch_name = f"multiagent/{task_id}"
        
        # Fetch latest
        run_git(["fetch", "origin", self.base_branch])
        
        # Create worktree
        run_git([
            "worktree", "add", "-b", branch_name,
            str(worktree_path), f"origin/{self.base_branch}"
        ])
        
        return worktree_path
    
    def merge_worktree(self, task_id: str, no_commit: bool = False) -> bool:
        """Merge worktree back to base branch."""
        branch = f"multiagent/{task_id}"
        
        # Switch to base
        run_git(["checkout", self.base_branch])
        
        # Merge
        args = ["merge", "--no-ff", branch]
        if no_commit:
            args.append("--no-commit")
        else:
            args.extend(["-m", f"multiagent: {task_id}"])
        
        result = run_git(args)
        
        if no_commit and result.returncode == 0:
            self._unstage_gitignored_files()
        
        return result.returncode == 0
    
    def _unstage_gitignored_files(self):
        """Remove gitignored files from stage."""
        staged = run_git(["diff", "--cached", "--name-only"]).stdout.split("\n")
        for file in staged:
            if not file.strip():
                continue
            # Check if gitignored
            check = run_git(["check-ignore", file])
            if check.returncode == 0:
                run_git(["reset", "HEAD", "--", file])
            # Always unstage .multiagent/ files
            if file.startswith(".multiagent/"):
                run_git(["reset", "HEAD", "--", file])
```



---

## 2. QA Loop Architecture (КРИТИЧНО)

### Как работает в Auto-Claude

```python
# apps/backend/qa/loop.py

async def run_qa_validation_loop(project_dir, spec_dir, model):
    """
    Self-validating QA loop:
    1. QA Reviewer validates against acceptance criteria
    2. If rejected → QA Fixer applies fixes
    3. Loop until approved or max iterations (50)
    
    Enhanced with:
    - Recurring issue detection (3+ occurrences → escalate)
    - Iteration history tracking
    - Self-correction on errors
    """
    
    MAX_QA_ITERATIONS = 50
    MAX_CONSECUTIVE_ERRORS = 3
    
    qa_iteration = 0
    consecutive_errors = 0
    last_error_context = None
    
    while qa_iteration < MAX_QA_ITERATIONS:
        qa_iteration += 1
        
        # Run QA Reviewer
        status, response = await run_qa_agent_session(
            client, project_dir, spec_dir, qa_iteration,
            previous_error=last_error_context  # Self-correction!
        )
        
        if status == "approved":
            # Record successful iteration
            record_iteration(spec_dir, qa_iteration, "approved", [])
            return True
        
        elif status == "rejected":
            # Get issues from QA report
            qa_status = get_qa_signoff_status(spec_dir)
            current_issues = qa_status.get("issues_found", [])
            
            # Check for recurring issues BEFORE recording
            history = get_iteration_history(spec_dir)
            has_recurring, recurring_issues = has_recurring_issues(
                current_issues, history
            )
            
            # Record iteration
            record_iteration(spec_dir, qa_iteration, "rejected", current_issues)
            
            if has_recurring:
                # Escalate to human
                await escalate_to_human(spec_dir, recurring_issues, qa_iteration)
                return False
            
            # Run QA Fixer
            fix_status, fix_response = await run_qa_fixer_session(
                fix_client, spec_dir, qa_iteration
            )
            
            if fix_status == "error":
                break
        
        elif status == "error":
            consecutive_errors += 1
            
            # Build error context for self-correction
            last_error_context = {
                "error_type": "missing_implementation_plan_update",
                "error_message": response,
                "consecutive_errors": consecutive_errors,
                "expected_action": "You MUST update implementation_plan.json..."
            }
            
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                return False
    
    return False
```

### Recurring Issue Detection

```python
# apps/backend/qa/report.py

RECURRING_ISSUE_THRESHOLD = 3
ISSUE_SIMILARITY_THRESHOLD = 0.8

def has_recurring_issues(current_issues, history):
    """
    Check if any current issues appeared 3+ times in history.
    Uses fuzzy matching (SequenceMatcher) to detect similar issues.
    """
    historical_issues = []
    for record in history:
        historical_issues.extend(record.get("issues", []))
    
    recurring = []
    
    for current in current_issues:
        occurrence_count = 1  # Current occurrence
        
        for historical in historical_issues:
            similarity = _issue_similarity(current, historical)
            if similarity >= ISSUE_SIMILARITY_THRESHOLD:
                occurrence_count += 1
        
        if occurrence_count >= RECURRING_ISSUE_THRESHOLD:
            recurring.append({
                **current,
                "occurrence_count": occurrence_count
            })
    
    return len(recurring) > 0, recurring

def _issue_similarity(issue1, issue2):
    """Calculate similarity between two issues."""
    key1 = _normalize_issue_key(issue1)
    key2 = _normalize_issue_key(issue2)
    return SequenceMatcher(None, key1, key2).ratio()

def _normalize_issue_key(issue):
    """Create normalized key for comparison."""
    title = (issue.get("title") or "").lower().strip()
    file = (issue.get("file") or "").lower().strip()
    line = issue.get("line") or ""
    return f"{title}|{file}|{line}"
```

### QA Signoff Protocol (JSON)

```python
# apps/backend/qa/criteria.py

def get_qa_signoff_status(spec_dir):
    """
    Read qa_signoff from implementation_plan.json.
    
    Expected format:
    {
        "qa_signoff": {
            "status": "approved" | "rejected",
            "timestamp": "2026-01-20T...",
            "qa_session": 5,
            
            # If approved:
            "report_file": "qa_report.md",
            "tests_passed": {"unit": "10/10", "integration": "5/5"},
            "verified_by": "qa_agent",
            
            # If rejected:
            "issues_found": [
                {
                    "type": "critical",
                    "title": "Missing error handling",
                    "location": "src/api.py:45",
                    "fix_required": "Add try-catch block"
                }
            ],
            "fix_request_file": "QA_FIX_REQUEST.md"
        }
    }
    """
    plan = load_implementation_plan(spec_dir)
    return plan.get("qa_signoff")

def is_qa_approved(spec_dir):
    """Check if QA approved the build."""
    status = get_qa_signoff_status(spec_dir)
    return status and status.get("status") == "approved"
```

### Что взять для CLI

```python
# core/qa_loop.py

class QALoop:
    """Structured QA validation loop."""
    
    MAX_ITERATIONS = 50
    RECURRING_THRESHOLD = 3
    
    async def run(self, task_dir: Path, model: str) -> bool:
        """Run QA validation loop."""
        iteration = 0
        
        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            
            # Run reviewer
            status = await self.run_reviewer(task_dir, iteration)
            
            if status == "approved":
                self.record_iteration(task_dir, iteration, "approved", [])
                return True
            
            elif status == "rejected":
                issues = self.get_issues(task_dir)
                
                # Check recurring
                if self.has_recurring_issues(task_dir, issues):
                    self.escalate_to_human(task_dir, issues)
                    return False
                
                self.record_iteration(task_dir, iteration, "rejected", issues)
                
                # Run fixer
                await self.run_fixer(task_dir, iteration)
        
        return False
    
    def has_recurring_issues(self, task_dir, current_issues):
        """Detect recurring issues (3+ occurrences)."""
        history = self.load_history(task_dir)
        
        for issue in current_issues:
            count = 1
            for record in history:
                for hist_issue in record["issues"]:
                    if self.similarity(issue, hist_issue) >= 0.8:
                        count += 1
            
            if count >= self.RECURRING_THRESHOLD:
                return True
        
        return False
    
    def similarity(self, issue1, issue2):
        """Calculate issue similarity."""
        from difflib import SequenceMatcher
        key1 = f"{issue1['title']}|{issue1.get('file', '')}"
        key2 = f"{issue2['title']}|{issue2.get('file', '')}"
        return SequenceMatcher(None, key1, key2).ratio()
```



---

## 3. Security System (КРИТИЧНО)

### 3-Layer Architecture

```python
# apps/backend/security/

# Layer 1: Parser (parser.py)
def extract_commands(command_string):
    """
    Extract command names from shell string.
    Handles: pipes, &&, ||, ;, subshells, quotes
    
    Cross-platform: Windows paths (C:\...) and POSIX paths
    Fallback parser for malformed commands
    """
    # Try shlex.split() first
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        # Malformed - use regex fallback
        return _fallback_extract_commands(command_string)
    
    commands = []
    expect_command = True
    
    for token in tokens:
        if token in ("|", "||", "&&", "&"):
            expect_command = True
        elif expect_command and not token.startswith("-"):
            cmd = _cross_platform_basename(token)
            commands.append(cmd)
            expect_command = False
    
    return commands

# Layer 2: Validators (validator.py, *_validators.py)
VALIDATORS = {
    "git": validate_git_command,
    "rm": validate_rm_command,
    "chmod": validate_chmod_command,
    "pkill": validate_pkill_command,
    # ... 20+ validators
}

def validate_git_command(command):
    """Validate git commands with secret scanning."""
    # Block dangerous operations
    if "git config" in command:
        if any(danger in command for danger in ["user.email", "user.name"]):
            return ValidationResult(
                allowed=False,
                reason="Modifying git config is not allowed"
            )
    
    # Scan commits for secrets
    if "git commit" in command:
        return validate_git_commit(command)
    
    return ValidationResult(allowed=True)

def validate_rm_command(command):
    """Validate rm commands to prevent data loss."""
    # Block dangerous patterns
    dangerous = [
        "rm -rf /",
        "rm -rf ~",
        "rm -rf *",
        "rm -rf .",
    ]
    
    for pattern in dangerous:
        if pattern in command:
            return ValidationResult(
                allowed=False,
                reason=f"Dangerous rm pattern: {pattern}"
            )
    
    return ValidationResult(allowed=True)

# Layer 3: Profile (profile.py)
class SecurityProfile:
    """
    Security profile with 3 command tiers:
    1. Base commands (always allowed)
    2. Stack commands (detected from project)
    3. Custom commands (user allowlist)
    """
    
    def __init__(self, project_dir):
        self.base_commands = BASE_COMMANDS  # ls, cat, grep, etc.
        self.stack_commands = self._detect_stack(project_dir)
        self.custom_commands = self._load_custom(project_dir)
    
    def _detect_stack(self, project_dir):
        """Auto-detect project stack and allow relevant commands."""
        commands = set()
        
        # Node.js
        if (project_dir / "package.json").exists():
            commands.update(["npm", "node", "npx", "yarn", "pnpm"])
        
        # Python
        if (project_dir / "requirements.txt").exists():
            commands.update(["python", "python3", "pip", "pip3", "pytest"])
        
        # Rust
        if (project_dir / "Cargo.toml").exists():
            commands.update(["cargo", "rustc"])
        
        # Docker
        if (project_dir / "Dockerfile").exists():
            commands.update(["docker", "docker-compose"])
        
        return commands
    
    def is_allowed(self, command):
        """Check if command is allowed."""
        cmd = extract_commands(command)[0]
        
        # Check tiers
        if cmd in self.base_commands:
            return True
        if cmd in self.stack_commands:
            return True
        if cmd in self.custom_commands:
            return True
        
        return False
```

### Что взять для CLI

```python
# core/security.py

class SecurityManager:
    """Command validation and security."""
    
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
        """Check if command is in allowlist."""
        return (
            cmd in self.BASE_COMMANDS or
            cmd in self.stack_commands
        )
    
    def _detect_stack(self) -> set[str]:
        """Auto-detect project stack."""
        commands = set()
        
        if (self.project_dir / "package.json").exists():
            commands.update(["npm", "node", "npx"])
        
        if (self.project_dir / "requirements.txt").exists():
            commands.update(["python", "pip", "pytest"])
        
        return commands
    
    def _load_validators(self) -> dict:
        """Load command validators."""
        return {
            "git": self._validate_git,
            "rm": self._validate_rm,
            "chmod": self._validate_chmod,
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
```



---

## 4. State Machine & Implementation Plan

### Implementation Plan Structure

```python
# apps/backend/implementation_plan/plan.py

@dataclass
class ImplementationPlan:
    """Complete implementation plan with progress tracking."""
    
    feature: str
    workflow_type: WorkflowType  # FEATURE, BUGFIX, REFACTOR
    phases: list[Phase]
    
    # Status tracking (synced with UI)
    status: str  # backlog, in_progress, ai_review, human_review, done
    planStatus: str  # pending, in_progress, review, completed
    
    # QA signoff
    qa_signoff: dict | None
    
    # Recovery
    recoveryNote: str | None
    
    def get_next_subtask(self) -> tuple[Phase, Subtask] | None:
        """Get next subtask respecting dependencies."""
        for phase in self.get_available_phases():
            pending = phase.get_pending_subtasks()
            if pending:
                return phase, pending[0]
        return None
    
    def get_available_phases(self) -> list[Phase]:
        """Get phases whose dependencies are satisfied."""
        completed_phases = {p.phase for p in self.phases if p.is_complete()}
        available = []
        
        for phase in self.phases:
            if phase.is_complete():
                continue
            deps_met = all(d in completed_phases for d in phase.depends_on)
            if deps_met:
                available.append(phase)
        
        return available
    
    async def async_save(self, path: Path):
        """Async save with atomic write (prevents corruption)."""
        self._update_timestamps_and_status()
        data = self.to_dict()
        
        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            functools.partial(write_json_atomic, path, data)
        )

@dataclass
class Phase:
    """Group of subtasks with dependencies."""
    
    phase: int
    name: str
    type: PhaseType  # SETUP, IMPLEMENTATION, TESTING, DOCUMENTATION
    subtasks: list[Subtask]
    depends_on: list[int]  # Phase dependencies
    parallel_safe: bool  # Can subtasks run in parallel?
    
    def is_complete(self) -> bool:
        """Check if all subtasks done."""
        return all(s.status == SubtaskStatus.COMPLETED for s in self.subtasks)

@dataclass
class Subtask:
    """Single unit of work."""
    
    id: str
    description: str
    status: SubtaskStatus  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    
    # Scoping
    service: str | None  # backend, frontend, worker
    files_to_modify: list[str]
    files_to_create: list[str]
    
    # Verification
    verification: Verification | None
    
    # Tracking
    started_at: str | None
    completed_at: str | None
    session_id: int | None
    
    def start(self, session_id: int):
        """Mark as in progress."""
        self.status = SubtaskStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()
        self.session_id = session_id
    
    def complete(self, output: str | None = None):
        """Mark as done."""
        self.status = SubtaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
```

### Phase Configuration

```python
# apps/backend/phase_config.py

# Model per phase (Auto profile)
DEFAULT_PHASE_MODELS = {
    "spec": "sonnet",
    "planning": "sonnet",
    "coding": "sonnet",
    "qa": "sonnet",
}

# Thinking level per phase
DEFAULT_PHASE_THINKING = {
    "spec": "medium",
    "planning": "high",
    "coding": "medium",
    "qa": "high",
}

def get_phase_model(spec_dir, phase, cli_model=None):
    """
    Get model for phase.
    Priority: CLI arg > task_metadata.json > defaults
    """
    if cli_model:
        return resolve_model_id(cli_model)
    
    metadata = load_task_metadata(spec_dir)
    if metadata and metadata.get("isAutoProfile"):
        return resolve_model_id(
            metadata["phaseModels"].get(phase, DEFAULT_PHASE_MODELS[phase])
        )
    
    return resolve_model_id(DEFAULT_PHASE_MODELS[phase])
```

### Что взять для CLI

```python
# core/implementation_plan.py

@dataclass
class ImplementationPlan:
    """Task implementation plan."""
    
    task_id: str
    description: str
    phases: list[Phase]
    status: str  # pending, in_progress, review, completed
    
    def get_next_subtask(self) -> Subtask | None:
        """Get next subtask respecting dependencies."""
        for phase in self.phases:
            if not self._phase_ready(phase):
                continue
            
            for subtask in phase.subtasks:
                if subtask.status == "pending":
                    return subtask
        
        return None
    
    def _phase_ready(self, phase: Phase) -> bool:
        """Check if phase dependencies satisfied."""
        for dep_id in phase.depends_on:
            dep_phase = self._get_phase(dep_id)
            if not dep_phase.is_complete():
                return False
        return True
    
    def save(self, path: Path):
        """Save plan atomically."""
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        temp_path.replace(path)  # Atomic on POSIX

@dataclass
class Phase:
    """Phase with subtasks."""
    
    id: int
    name: str
    subtasks: list[Subtask]
    depends_on: list[int]
    
    def is_complete(self) -> bool:
        return all(s.status == "completed" for s in self.subtasks)

@dataclass
class Subtask:
    """Single unit of work."""
    
    id: str
    description: str
    status: str  # pending, in_progress, completed, failed
    files: list[str]
    started_at: str | None = None
    completed_at: str | None = None
```



---

## 5. Crash Recovery & State Persistence

### Recovery System

```python
# apps/backend/services/recovery.py

class RecoveryManager:
    """Handles crash recovery and state restoration."""
    
    def can_resume(self, spec_dir: Path) -> bool:
        """Check if build can be resumed."""
        plan_file = spec_dir / "implementation_plan.json"
        if not plan_file.exists():
            return False
        
        plan = ImplementationPlan.load(plan_file)
        
        # Can resume if:
        # 1. Plan exists
        # 2. Not all subtasks completed
        # 3. Status is in_progress
        return (
            plan.status == "in_progress" and
            not self._all_subtasks_complete(plan)
        )
    
    def resume_build(self, spec_dir: Path):
        """Resume interrupted build."""
        plan = ImplementationPlan.load(spec_dir / "implementation_plan.json")
        
        # Find last completed subtask
        last_session = self._get_last_session_id(plan)
        
        # Continue from next subtask
        next_work = plan.get_next_subtask()
        if next_work:
            phase, subtask = next_work
            return self._resume_from_subtask(
                spec_dir, plan, phase, subtask, last_session + 1
            )
        
        return False
```

### Atomic State Updates

```python
# core/file_utils.py

def write_json_atomic(path: Path, data: dict, **kwargs):
    """
    Write JSON atomically to prevent corruption on crash.
    
    Uses temp file + rename for atomic operation.
    """
    temp_path = path.with_suffix(".tmp")
    
    # Write to temp file
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, **kwargs)
    
    # Atomic rename (POSIX guarantee)
    temp_path.replace(path)
```

### Что взять для CLI

```python
# core/recovery.py

class RecoveryManager:
    """Crash recovery and resume."""
    
    def can_resume(self, task_dir: Path) -> bool:
        """Check if task can be resumed."""
        plan_file = task_dir / "plan.json"
        if not plan_file.exists():
            return False
        
        plan = ImplementationPlan.load(plan_file)
        return plan.status == "in_progress"
    
    def resume(self, task_dir: Path) -> bool:
        """Resume interrupted task."""
        plan = ImplementationPlan.load(task_dir / "plan.json")
        
        # Find next subtask
        next_subtask = plan.get_next_subtask()
        if not next_subtask:
            return False
        
        # Continue execution
        return self._execute_from_subtask(task_dir, plan, next_subtask)

# core/atomic_write.py

def atomic_write_json(path: Path, data: dict):
    """Write JSON atomically."""
    temp = path.with_suffix(".tmp")
    with open(temp, "w") as f:
        json.dump(data, f, indent=2)
    temp.replace(path)  # Atomic
```

---

## 6. Provider Abstraction

### ClaudeSDKClient Wrapper

```python
# apps/backend/core/client.py

def create_client(
    project_dir: Path,
    spec_dir: Path,
    model: str,
    agent_type: str,
    max_thinking_tokens: int | None = None
) -> ClaudeSDKClient:
    """
    Create Claude SDK client with project context.
    
    This is the ONLY place where Claude Code API is used.
    Easy to replace with OpenAI/Anthropic/etc.
    """
    from claude_agent_sdk import ClaudeSDKClient
    
    return ClaudeSDKClient(
        project_dir=str(project_dir),
        model=model,
        max_thinking_tokens=max_thinking_tokens,
        # ... other config
    )

# Usage in agent sessions:
async def run_agent_session(client: ClaudeSDKClient, ...):
    """Run agent session (provider-agnostic)."""
    await client.query(prompt)
    
    async for msg in client.receive_response():
        if msg_type == "AssistantMessage":
            for block in msg.content:
                if block_type == "TextBlock":
                    print(block.text)
                elif block_type == "ToolUseBlock":
                    # Handle tool call
                    pass
```

### Что взять для CLI

```python
# core/model_client.py

class ModelClient(ABC):
    """Abstract model client interface."""
    
    @abstractmethod
    async def query(self, prompt: str):
        """Send query to model."""
        pass
    
    @abstractmethod
    async def receive_response(self):
        """Receive streaming response."""
        pass

class OpenAIClient(ModelClient):
    """OpenAI-compatible client."""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    
    async def query(self, prompt: str):
        """Send query."""
        self.messages = [{"role": "user", "content": prompt}]
    
    async def receive_response(self):
        """Receive streaming response."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield TextBlock(text=chunk.choices[0].delta.content)
            elif chunk.choices[0].delta.tool_calls:
                yield ToolUseBlock(...)

# Factory
def create_client(provider: str, **kwargs) -> ModelClient:
    """Create model client."""
    if provider == "openai":
        return OpenAIClient(**kwargs)
    elif provider == "anthropic":
        return AnthropicClient(**kwargs)
    elif provider == "cliproxy":
        return OpenAIClient(
            base_url="http://localhost:8000/v1",
            **kwargs
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
```



---

## 7. Улучшенный План Разработки

### Архитектура (обновлённая)

```
multiagent-cli/
├── cli/
│   ├── main.py              # CLI entry point
│   ├── commands.py          # Command handlers
│   └── config.py            # Configuration
├── core/
│   ├── worktree_manager.py  # Git worktree isolation
│   ├── implementation_plan.py # Task planning
│   ├── qa_loop.py           # QA validation loop
│   ├── security.py          # Command validation
│   ├── model_client.py      # Provider abstraction
│   ├── recovery.py          # Crash recovery
│   └── atomic_write.py      # Atomic file operations
├── agents/
│   ├── planner.py           # Planning agent
│   ├── coder.py             # Coding agent
│   ├── qa_reviewer.py       # QA reviewer agent
│   └── qa_fixer.py          # QA fixer agent
├── prompts/
│   ├── planner.md
│   ├── coder.md
│   ├── qa_reviewer.md
│   └── qa_fixer.md
└── .multiagent/
    ├── tasks/               # Task definitions
    ├── worktrees/           # Git worktrees
    └── logs/                # Execution logs
```

### Первые 10 коммитов (обновлённые)

#### Commit 1: CLI Foundation (2h)
```bash
# Создать структуру
mkdir -p cli core agents prompts tests .multiagent/{tasks,worktrees,logs}

# cli/main.py
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", help="Task ID")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    
    if args.resume:
        handle_resume(args.task)
    else:
        handle_run(args.task)

# cli/commands.py
def handle_run(task_id: str):
    """Run a task."""
    task_dir = Path(f".multiagent/tasks/{task_id}")
    if not task_dir.exists():
        print(f"Task not found: {task_id}")
        return
    
    # TODO: Execute task
    print(f"Running task: {task_id}")

def handle_resume(task_id: str):
    """Resume interrupted task."""
    # TODO: Recovery logic
    print(f"Resuming task: {task_id}")
```

#### Commit 2: Worktree Manager (4h)
```python
# core/worktree_manager.py

class WorktreeManager:
    """Git worktree isolation."""
    
    def __init__(self, project_dir: Path, base_branch: str = "main"):
        self.project_dir = project_dir
        self.base_branch = base_branch
        self.worktrees_dir = project_dir / ".multiagent/worktrees"
    
    def create_worktree(self, task_id: str) -> Path:
        """Create isolated worktree."""
        worktree_path = self.worktrees_dir / task_id
        branch_name = f"multiagent/{task_id}"
        
        # Fetch latest
        run_git(["fetch", "origin", self.base_branch])
        
        # Create worktree
        run_git([
            "worktree", "add", "-b", branch_name,
            str(worktree_path), f"origin/{self.base_branch}"
        ])
        
        return worktree_path
    
    def merge_worktree(self, task_id: str, no_commit: bool = False) -> bool:
        """Merge worktree back."""
        branch = f"multiagent/{task_id}"
        
        run_git(["checkout", self.base_branch])
        
        args = ["merge", "--no-ff", branch]
        if no_commit:
            args.append("--no-commit")
        
        result = run_git(args)
        
        if no_commit and result.returncode == 0:
            self._unstage_gitignored_files()
        
        return result.returncode == 0
    
    def _unstage_gitignored_files(self):
        """Remove gitignored files from stage."""
        staged = run_git(["diff", "--cached", "--name-only"]).stdout.split("\n")
        for file in staged:
            if not file.strip():
                continue
            check = run_git(["check-ignore", file])
            if check.returncode == 0 or file.startswith(".multiagent/"):
                run_git(["reset", "HEAD", "--", file])

def run_git(args: list[str], cwd: Path = None) -> subprocess.CompletedProcess:
    """Run git command."""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )
```

#### Commit 3: Security System (4h)
```python
# core/security.py

class SecurityManager:
    """Command validation."""
    
    BASE_COMMANDS = {
        "ls", "cat", "grep", "find", "echo", "pwd",
        "mkdir", "touch", "cp", "mv", "git"
    }
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.stack_commands = self._detect_stack()
    
    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate command."""
        commands = self._extract_commands(command)
        
        for cmd in commands:
            if not self._is_allowed(cmd):
                return False, f"Command not allowed: {cmd}"
            
            # Run validators
            if cmd == "git" and "git config" in command:
                return False, "git config not allowed"
            if cmd == "rm" and any(p in command for p in ["rm -rf /", "rm -rf ~"]):
                return False, "Dangerous rm pattern"
        
        return True, ""
    
    def _is_allowed(self, cmd: str) -> bool:
        return cmd in self.BASE_COMMANDS or cmd in self.stack_commands
    
    def _detect_stack(self) -> set[str]:
        """Auto-detect project stack."""
        commands = set()
        
        if (self.project_dir / "package.json").exists():
            commands.update(["npm", "node", "npx"])
        if (self.project_dir / "requirements.txt").exists():
            commands.update(["python", "pip", "pytest"])
        
        return commands
    
    def _extract_commands(self, command: str) -> list[str]:
        """Extract command names."""
        import shlex
        try:
            tokens = shlex.split(command)
        except ValueError:
            return []
        
        commands = []
        expect_command = True
        
        for token in tokens:
            if token in ("|", "||", "&&"):
                expect_command = True
            elif expect_command and not token.startswith("-"):
                commands.append(token.split("/")[-1])
                expect_command = False
        
        return commands
```

#### Commit 4: Model Client (3h)
```python
# core/model_client.py

from abc import ABC, abstractmethod
from openai import AsyncOpenAI

class ModelClient(ABC):
    """Abstract model client."""
    
    @abstractmethod
    async def query(self, prompt: str):
        pass
    
    @abstractmethod
    async def receive_response(self):
        pass

class OpenAIClient(ModelClient):
    """OpenAI-compatible client."""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.messages = []
    
    async def query(self, prompt: str):
        self.messages = [{"role": "user", "content": prompt}]
    
    async def receive_response(self):
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {"type": "text", "text": chunk.choices[0].delta.content}

def create_client(provider: str, **kwargs) -> ModelClient:
    """Create model client."""
    if provider == "openai":
        return OpenAIClient(**kwargs)
    elif provider == "cliproxy":
        return OpenAIClient(
            base_url="http://localhost:8000/v1",
            **kwargs
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

#### Commit 5: Implementation Plan (3h)
```python
# core/implementation_plan.py

@dataclass
class ImplementationPlan:
    """Task implementation plan."""
    
    task_id: str
    description: str
    phases: list[Phase]
    status: str  # pending, in_progress, review, completed
    
    def get_next_subtask(self) -> Subtask | None:
        """Get next subtask."""
        for phase in self.phases:
            if not self._phase_ready(phase):
                continue
            for subtask in phase.subtasks:
                if subtask.status == "pending":
                    return subtask
        return None
    
    def _phase_ready(self, phase: Phase) -> bool:
        """Check if phase dependencies satisfied."""
        for dep_id in phase.depends_on:
            dep_phase = self._get_phase(dep_id)
            if not dep_phase.is_complete():
                return False
        return True
    
    def save(self, path: Path):
        """Save plan atomically."""
        from core.atomic_write import atomic_write_json
        atomic_write_json(path, self.to_dict())
    
    @classmethod
    def load(cls, path: Path):
        """Load plan."""
        with open(path) as f:
            return cls.from_dict(json.load(f))

@dataclass
class Phase:
    id: int
    name: str
    subtasks: list[Subtask]
    depends_on: list[int]
    
    def is_complete(self) -> bool:
        return all(s.status == "completed" for s in self.subtasks)

@dataclass
class Subtask:
    id: str
    description: str
    status: str
    files: list[str]
    started_at: str | None = None
    completed_at: str | None = None
```



#### Commit 6: QA Loop (5h)
```python
# core/qa_loop.py

class QALoop:
    """Structured QA validation loop."""
    
    MAX_ITERATIONS = 50
    RECURRING_THRESHOLD = 3
    
    def __init__(self, model_client: ModelClient, security: SecurityManager):
        self.client = model_client
        self.security = security
    
    async def run(self, task_dir: Path) -> bool:
        """Run QA validation loop."""
        iteration = 0
        
        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            
            # Run reviewer
            status, issues = await self.run_reviewer(task_dir, iteration)
            
            if status == "approved":
                self.record_iteration(task_dir, iteration, "approved", [])
                return True
            
            elif status == "rejected":
                # Check recurring
                if self.has_recurring_issues(task_dir, issues):
                    self.escalate_to_human(task_dir, issues)
                    return False
                
                self.record_iteration(task_dir, iteration, "rejected", issues)
                
                # Run fixer
                await self.run_fixer(task_dir, iteration, issues)
        
        return False
    
    async def run_reviewer(self, task_dir, iteration):
        """Run QA reviewer."""
        prompt = self.load_prompt("qa_reviewer", task_dir)
        
        await self.client.query(prompt)
        
        response = ""
        async for msg in self.client.receive_response():
            if msg["type"] == "text":
                response += msg["text"]
                print(msg["text"], end="", flush=True)
        
        # Parse QA signoff from plan.json
        plan = ImplementationPlan.load(task_dir / "plan.json")
        qa_signoff = plan.qa_signoff
        
        if qa_signoff and qa_signoff["status"] == "approved":
            return "approved", []
        elif qa_signoff and qa_signoff["status"] == "rejected":
            return "rejected", qa_signoff["issues_found"]
        else:
            return "error", []
    
    async def run_fixer(self, task_dir, iteration, issues):
        """Run QA fixer."""
        # Create fix request
        fix_request = self.create_fix_request(issues)
        (task_dir / "QA_FIX_REQUEST.md").write_text(fix_request)
        
        prompt = self.load_prompt("qa_fixer", task_dir)
        
        await self.client.query(prompt)
        
        async for msg in self.client.receive_response():
            if msg["type"] == "text":
                print(msg["text"], end="", flush=True)
    
    def has_recurring_issues(self, task_dir, current_issues):
        """Detect recurring issues."""
        history = self.load_history(task_dir)
        
        for issue in current_issues:
            count = 1
            for record in history:
                for hist_issue in record["issues"]:
                    if self.similarity(issue, hist_issue) >= 0.8:
                        count += 1
            
            if count >= self.RECURRING_THRESHOLD:
                return True
        
        return False
    
    def similarity(self, issue1, issue2):
        """Calculate issue similarity."""
        from difflib import SequenceMatcher
        key1 = f"{issue1['title']}|{issue1.get('file', '')}"
        key2 = f"{issue2['title']}|{issue2.get('file', '')}"
        return SequenceMatcher(None, key1, key2).ratio()
    
    def record_iteration(self, task_dir, iteration, status, issues):
        """Record QA iteration."""
        history_file = task_dir / "qa_history.json"
        
        history = []
        if history_file.exists():
            history = json.loads(history_file.read_text())
        
        history.append({
            "iteration": iteration,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "issues": issues
        })
        
        from core.atomic_write import atomic_write_json
        atomic_write_json(history_file, history)
```

#### Commit 7: Recovery System (4h)
```python
# core/recovery.py

class RecoveryManager:
    """Crash recovery."""
    
    def can_resume(self, task_dir: Path) -> bool:
        """Check if task can be resumed."""
        plan_file = task_dir / "plan.json"
        if not plan_file.exists():
            return False
        
        plan = ImplementationPlan.load(plan_file)
        return plan.status == "in_progress"
    
    def resume(self, task_dir: Path, worktree_mgr, qa_loop) -> bool:
        """Resume interrupted task."""
        plan = ImplementationPlan.load(task_dir / "plan.json")
        
        # Find next subtask
        next_subtask = plan.get_next_subtask()
        if not next_subtask:
            # All subtasks done, run QA
            return qa_loop.run(task_dir)
        
        # Continue execution
        return self._execute_from_subtask(
            task_dir, plan, next_subtask, worktree_mgr
        )

# core/atomic_write.py

def atomic_write_json(path: Path, data: dict):
    """Write JSON atomically."""
    temp = path.with_suffix(".tmp")
    with open(temp, "w") as f:
        json.dump(data, f, indent=2)
    temp.replace(path)  # Atomic on POSIX
```

#### Commit 8: Planner Agent (3h)
```python
# agents/planner.py

class PlannerAgent:
    """Planning agent."""
    
    def __init__(self, model_client: ModelClient):
        self.client = model_client
    
    async def create_plan(self, task_dir: Path, description: str) -> ImplementationPlan:
        """Create implementation plan."""
        prompt = self.load_prompt(task_dir, description)
        
        await self.client.query(prompt)
        
        response = ""
        async for msg in self.client.receive_response():
            if msg["type"] == "text":
                response += msg["text"]
        
        # Parse plan from response
        plan = self.parse_plan(response, description)
        
        # Save plan
        plan.save(task_dir / "plan.json")
        
        return plan
    
    def load_prompt(self, task_dir, description):
        """Load planner prompt."""
        template = Path("prompts/planner.md").read_text()
        
        return template.format(
            task_description=description,
            project_context=self.get_project_context(task_dir)
        )
    
    def parse_plan(self, response, description):
        """Parse plan from response."""
        # TODO: Parse JSON from response
        # For now, return dummy plan
        return ImplementationPlan(
            task_id="task-001",
            description=description,
            phases=[],
            status="pending"
        )
```

#### Commit 9: Coder Agent (3h)
```python
# agents/coder.py

class CoderAgent:
    """Coding agent."""
    
    def __init__(self, model_client: ModelClient, security: SecurityManager):
        self.client = model_client
        self.security = security
    
    async def execute_subtask(self, task_dir: Path, subtask: Subtask) -> bool:
        """Execute a subtask."""
        prompt = self.load_prompt(task_dir, subtask)
        
        await self.client.query(prompt)
        
        async for msg in self.client.receive_response():
            if msg["type"] == "text":
                print(msg["text"], end="", flush=True)
            elif msg["type"] == "tool_call":
                # Validate command
                if msg["tool"] == "bash":
                    allowed, reason = self.security.validate_command(msg["command"])
                    if not allowed:
                        print(f"\n❌ Command blocked: {reason}")
                        continue
        
        # Mark subtask as completed
        subtask.status = "completed"
        subtask.completed_at = datetime.now().isoformat()
        
        return True
    
    def load_prompt(self, task_dir, subtask):
        """Load coder prompt."""
        template = Path("prompts/coder.md").read_text()
        
        return template.format(
            subtask_description=subtask.description,
            files_to_modify=subtask.files,
            project_context=self.get_project_context(task_dir)
        )
```

#### Commit 10: Integration & Tests (6h)
```python
# cli/commands.py (updated)

async def handle_run(task_id: str):
    """Run a task."""
    task_dir = Path(f".multiagent/tasks/{task_id}")
    project_dir = Path.cwd()
    
    # Initialize managers
    worktree_mgr = WorktreeManager(project_dir)
    security = SecurityManager(project_dir)
    client = create_client("cliproxy", api_key="dummy", model="gpt-4")
    
    # Create worktree
    worktree_path = worktree_mgr.create_worktree(task_id)
    
    # Create plan
    planner = PlannerAgent(client)
    plan = await planner.create_plan(task_dir, "Implement feature X")
    
    # Execute subtasks
    coder = CoderAgent(client, security)
    while True:
        next_subtask = plan.get_next_subtask()
        if not next_subtask:
            break
        
        await coder.execute_subtask(worktree_path, next_subtask)
        plan.save(task_dir / "plan.json")
    
    # Run QA
    qa_loop = QALoop(client, security)
    approved = await qa_loop.run(task_dir)
    
    if approved:
        # Merge worktree
        worktree_mgr.merge_worktree(task_id, no_commit=True)
        print("✅ Task completed! Review changes and commit.")
    else:
        print("❌ QA validation failed. Manual intervention required.")

# tests/test_worktree.py

def test_create_worktree():
    """Test worktree creation."""
    mgr = WorktreeManager(Path("/tmp/test"))
    worktree = mgr.create_worktree("test-001")
    assert worktree.exists()
    assert (worktree / ".git").exists()

def test_merge_worktree():
    """Test worktree merge."""
    mgr = WorktreeManager(Path("/tmp/test"))
    success = mgr.merge_worktree("test-001", no_commit=True)
    assert success

# tests/test_security.py

def test_validate_command():
    """Test command validation."""
    security = SecurityManager(Path("/tmp/test"))
    
    # Allowed
    allowed, _ = security.validate_command("ls -la")
    assert allowed
    
    # Blocked
    allowed, reason = security.validate_command("rm -rf /")
    assert not allowed
    assert "Dangerous" in reason
```

---

## 8. Итоговые рекомендации

### Что делать СЕЙЧАС

1. **Начать с Commit 1-3** (CLI + Worktree + Security) - это фундамент
2. **Протестировать worktree изоляцию** - убедиться, что нет конфликтов
3. **Реализовать Commit 4-5** (Model Client + Plan) - базовая функциональность
4. **Добавить Commit 6** (QA Loop) - критично для качества
5. **Завершить Commit 7-10** - полная система

### Что НЕ делать

- ❌ Не копировать Electron UI
- ❌ Не интегрировать Graphiti memory (сложно)
- ❌ Не добавлять Linear/GitHub интеграции сразу
- ❌ Не пытаться сделать всё за раз

### Timeline

- **Week 1 (MVP):** Commits 1-5 (CLI + Worktree + Security + Model + Plan) = 16h
- **Week 2 (QA):** Commits 6-7 (QA Loop + Recovery) = 9h
- **Week 3 (Agents):** Commits 8-10 (Planner + Coder + Integration) = 12h
- **Total:** 37 hours (примерно 1 неделя full-time)

### Success Criteria

✅ Можно создать task и запустить его  
✅ Task выполняется в изолированном worktree  
✅ Команды валидируются перед выполнением  
✅ QA loop проверяет результат  
✅ Можно resume после crash  
✅ Можно merge результат в main  

