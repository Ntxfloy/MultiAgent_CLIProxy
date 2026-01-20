# Progress Tracker (Kanban)

**Last Updated:** 2026-01-20  
**Current Sprint:** MVP (Week 1)

---

## 🎯 In Progress

### TASK-001: Project Structure & CLI Foundation
**Status:** Starting  
**Assignee:** Kiro  
**Started:** 2026-01-20

**Scope:**
- Create directory structure: cli/, core/, agents/prompts/, tests/, .multiagent/
- Implement CLI entrypoint with argparse/typer
- Add command stubs: init, spec new, run, status, logs, worktree list
- Add config loader for base_url, api_key, model mapping
- Update .gitignore for .multiagent/

**Files:**
- `cli/__init__.py`
- `cli/main.py`
- `cli/commands.py`
- `core/__init__.py`
- `core/config_loader.py`
- `.multiagent/.gitignore`
- `agents/prompts/` (directory)
- `tests/` (directory)

**Done Criteria:**
- [ ] `python -m cli.main --help` shows all commands
- [ ] `python -m cli.main init` creates config
- [ ] `python -m cli.main spec new test-task` creates spec file
- [ ] All commands have help text
- [ ] No import errors
- [ ] python -m compileall passes

**Verification Commands:**
```bash
cd testkiro/MultiAgent_CLIProxy
python -m compileall cli/ core/
python -m cli.main --help
python -m cli.main init --help
python -m cli.main spec --help
```

---

## 📋 Next (Top Priority)

### TASK-002: Worktree Manager MVP
**Priority:** High  
**Depends On:** TASK-001

**Scope:**
- Implement `core/worktree_manager.py`
- Methods: create_worktree, commit_checkpoint, merge_back, cleanup
- Git command generation (no direct execution yet)
- Unit tests with mocked git commands

**Files:**
- `core/worktree_manager.py`
- `tests/test_worktree.py`

**Done Criteria:**
- [ ] WorktreeManager class exists
- [ ] All methods implemented
- [ ] Unit tests pass (mocked git)
- [ ] Manual test: create worktree, commit, merge
- [ ] Documentation in docstrings

**Verification Commands:**
```bash
python -m pytest tests/test_worktree.py -v
python -m compileall core/worktree_manager.py
```

---

### TASK-003: Safe Shell Runner MVP
**Priority:** High  
**Depends On:** TASK-001

**Scope:**
- Implement `core/shell_runner.py`
- Allowlist: git, npm, pytest, python, node, etc.
- Denylist: rm -rf, sudo, curl | bash, eval, etc.
- cwd restriction: only inside worktree
- stdout/stderr logging to .multiagent/logs/

**Files:**
- `core/shell_runner.py`
- `tests/test_shell_runner.py`

**Done Criteria:**
- [ ] ShellRunner class exists
- [ ] Allowlist/denylist validation works
- [ ] cwd restriction enforced
- [ ] Blocked commands raise SecurityError
- [ ] Allowed commands log output
- [ ] Unit tests pass

**Verification Commands:**
```bash
python -m pytest tests/test_shell_runner.py -v
python -m compileall core/shell_runner.py
```

---

### TASK-004: State Persistence + Resume
**Priority:** High  
**Depends On:** TASK-001

**Scope:**
- Implement `core/state_store.py`
- Atomic writes: write to tmp file, then rename
- Load/save state.json per task
- Schema: task_id, phase, subtasks, history, metadata

**Files:**
- `core/state_store.py`
- `tests/test_state_store.py`

**Done Criteria:**
- [ ] StateStore class exists
- [ ] Atomic writes work (tmp+rename)
- [ ] Load/save methods implemented
- [ ] State survives crashes (manual test)
- [ ] Unit tests pass

**Verification Commands:**
```bash
python -m pytest tests/test_state_store.py -v
python -m compileall core/state_store.py
```

---

### TASK-005: Basic QA Loop
**Priority:** Medium  
**Depends On:** TASK-001

**Scope:**
- Implement `core/qa_loop.py`
- Reviewer agent outputs JSON: {approved: bool, issues: [...]}
- If not approved → generate fix request for coder
- Max 50 iterations
- Basic recurring issue detection (exact match)

**Files:**
- `core/qa_loop.py`
- `tests/test_qa_loop.py`

**Done Criteria:**
- [ ] QALoop class exists
- [ ] JSON parsing works
- [ ] Fix request generation works
- [ ] Max iterations enforced
- [ ] Unit tests pass (mocked agents)

**Verification Commands:**
```bash
python -m pytest tests/test_qa_loop.py -v
python -m compileall core/qa_loop.py
```

---

## 🔄 Backlog

### TASK-006: State Machine Pipeline
**Priority:** Medium  
**Depends On:** TASK-002, TASK-003, TASK-004

**Scope:**
- Implement `core/pipeline.py`
- Phases: planning → implementation → test → review
- Phase dependencies and transitions
- Checkpoint after each phase

**Files:**
- `core/pipeline.py`
- `tests/test_pipeline.py`

---

### TASK-007: Crash Recovery
**Priority:** Medium  
**Depends On:** TASK-004, TASK-006

**Scope:**
- Resume from last checkpoint
- Restore worktree state
- Continue from interrupted phase

**Files:**
- `cli/commands.py` (resume command)
- `core/pipeline.py` (resume logic)

---

### TASK-008: Advanced QA (Recurring Issues)
**Priority:** Low  
**Depends On:** TASK-005

**Scope:**
- Fuzzy matching for recurring issues
- Issue history tracking
- Self-correction prompts

**Files:**
- `core/qa_loop.py` (enhance)
- `tests/test_qa_loop.py` (add tests)

---

### TASK-009: Provider Abstraction
**Priority:** Low  
**Depends On:** TASK-001

**Scope:**
- Abstract model client interface
- Easy provider swapping (OpenAI, CLIProxy, local)
- Fallback chain support

**Files:**
- `core/model_client.py`
- `tests/test_model_client.py`

---

### TASK-010: Integration Tests
**Priority:** Low  
**Depends On:** TASK-002, TASK-003, TASK-004, TASK-005

**Scope:**
- End-to-end test: spec → run → review → merge
- Real git worktree operations
- Real shell commands (safe subset)

**Files:**
- `tests/integration/test_e2e.py`

---

## ✅ Done

*(No completed tasks yet)*

---

## 📊 Statistics

- **Total Tasks:** 10
- **In Progress:** 1
- **Next:** 4
- **Backlog:** 5
- **Done:** 0
- **Completion:** 0%

---

## 🚨 Blockers

*(None currently)*

---

## 📝 Notes

### Commit Strategy
- Each task = 1 commit (atomic)
- Commit message format: `feat: <task-id> - <description>`
- Example: `feat: TASK-001 - Add CLI foundation and project structure`

### Testing Strategy
- Unit tests for all core modules
- Integration tests after MVP
- Manual testing for git operations

### Documentation Strategy
- Docstrings for all public methods
- README.md updates after each major feature
- ROADMAP.md is source of truth for architecture

---

## 🔗 Quick Links

- [ROADMAP.md](./ROADMAP.md) - Architecture and plan
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Detailed commit specs (reference)
- [UPGRADE_PLAN.md](./UPGRADE_PLAN.md) - Full architecture (reference)
