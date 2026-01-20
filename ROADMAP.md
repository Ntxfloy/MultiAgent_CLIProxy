# MultiAgent_CLIProxy → Auto-Claude-like System: ROADMAP

**Last Updated:** 2026-01-20  
**Status:** Active Development  
**Version:** 1.0.0-alpha

---

## 1. Vision & Non-Goals

### Vision
Transform MultiAgent_CLIProxy from a 500-line prototype into a **production-ready autonomous coding framework** with Auto-Claude-level infrastructure:

- **CLI-first**: No Electron UI, pure command-line interface
- **Provider-agnostic**: OpenAI-compatible endpoints (CLIProxy, OpenAI, local models)
- **Worktree isolation**: Each task in separate git worktree (no file conflicts)
- **Structured QA**: JSON-based validation loop with recurring issue detection
- **Security**: 3-layer command validation (parser → validator → profile)
- **State persistence**: Atomic writes, checkpoint/resume capability
- **Crash recovery**: Resume from last checkpoint after failures

### Non-Goals (Explicitly Out of Scope)
- ❌ Electron/Web UI (CLI only)
- ❌ Claude Code OAuth/subscriptions (provider-agnostic)
- ❌ Linear/GitHub integrations (maybe later)
- ❌ Graphiti memory system (too complex for MVP)
- ❌ Parallel agent terminals (sequential execution for MVP)

---

## 2. Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  multiagent init | spec new | run | status | logs | resume  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Core Pipeline                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Planning │→ │   Impl   │→ │   Test   │→ │  Review  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       ↓              ↓              ↓              ↓         │
│  State Machine with Phases (checkpoint/resume)              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Worktree Manager                            │
│  • create_worktree(task_id, base_branch)                    │
│  • commit_checkpoint(message)                               │
│  • merge_back(--no-commit for review)                       │
│  • cleanup()                                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Shell Runner                               │
│  • Allowlist: git, npm, pytest, etc.                        │
│  • Denylist: rm -rf, sudo, curl | bash                      │
│  • cwd restriction: only inside worktree                    │
│  • stdout/stderr logging                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    QA Loop                                   │
│  Reviewer → JSON output {approved: bool, issues: [...]}     │
│  If not approved → Fixer agent with error context           │
│  Max 50 iterations, recurring issue detection               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. MVP Scope (Week 1)

**Goal:** Basic CLI + worktrees + shell policy + QA + state

### Features
- ✅ CLI commands: init, spec new, run, status, logs, worktree list
- ✅ Config loader: base_url, api_key, model mapping
- ✅ Worktree manager: create, commit, merge, cleanup
- ✅ Shell runner: allowlist/denylist, cwd restriction, logging
- ✅ State persistence: atomic writes (tmp+rename), load/save
- ✅ Basic QA loop: JSON validation, fix request generation

### Deliverables
- Working CLI with 6 commands
- Isolated task execution in worktrees
- Safe shell command execution
- Checkpoint/resume capability
- Unit tests for core modules

---

## 4. V1 Scope (Weeks 2-3)

**Goal:** State machine phases + recovery + advanced QA

### Features
- ✅ State machine: planning → impl → test → review phases
- ✅ Subtask tracking: implementation_plan.json
- ✅ Crash recovery: resume from last phase
- ✅ Advanced QA: recurring issue detection (fuzzy matching)
- ✅ Provider abstraction: easy model swapping
- ✅ Spec format: YAML schema with requirements/constraints

### Deliverables
- Phase-based execution pipeline
- Robust error recovery
- Self-correcting QA loop
- Provider-agnostic model layer
- Integration tests

---

## 5. Module Map

```
MultiAgent_CLIProxy/
├── cli/
│   ├── __init__.py
│   ├── main.py              # CLI entrypoint (argparse/typer)
│   └── commands.py          # Command implementations
├── core/
│   ├── __init__.py
│   ├── worktree_manager.py  # Git worktree operations
│   ├── shell_runner.py      # Safe command execution
│   ├── state_store.py       # Atomic state persistence
│   ├── qa_loop.py           # Structured validation
│   ├── pipeline.py          # State machine phases
│   ├── config_loader.py     # Config management
│   ├── engine.py            # (existing, refactor later)
│   ├── resilient_client.py  # (existing, keep)
│   └── swarm.py             # (existing, keep)
├── agents/
│   ├── __init__.py
│   ├── registry_v3.py       # (existing, keep)
│   └── prompts/             # Prompt templates
│       ├── architect.txt
│       ├── coder.txt
│       ├── reviewer.txt
│       └── fixer.txt
├── tools/
│   ├── __init__.py
│   └── file_ops.py          # (existing, keep)
├── tests/
│   ├── test_worktree.py
│   ├── test_shell_runner.py
│   ├── test_state_store.py
│   └── test_qa_loop.py
├── .multiagent/             # Hidden state directory
│   ├── tasks/               # Task state files
│   ├── worktrees/           # Git worktrees
│   └── logs/                # Execution logs
├── config.py                # (existing, keep)
├── run_factory.py           # (existing, mark deprecated)
├── requirements.txt
└── README.md
```

---

## 6. Reference Index (Old Planning Files)

**These files are ARCHIVE/REFERENCE ONLY. ROADMAP.md is the single source of truth.**

| File | Status | Useful Sections | Notes |
|------|--------|-----------------|-------|
| **START_HERE.md** | Archive | Quick overview | Good intro, but superseded |
| **PLANNING_INDEX.md** | Archive | Document navigation | Useful for understanding planning history |
| **IMPLEMENTATION_ROADMAP.md** | Reference | First 10 commits | Detailed commit specs (use as guide) |
| **UPGRADE_PLAN.md** | Reference | Architecture diagrams, CLI UX | 1258 lines of detailed specs |
| **UPGRADE_PLAN_PART2.md** | Reference | QA loop, model layer | 600 lines on validation |
| **UPGRADE_SUMMARY.md** | Archive | High-level overview | Quick reference |
| **UPGRADE_SUMMARY_V2.md** | Archive | Deep analysis insights | Key findings from Auto-Claude study |
| **REPO_ANALYSIS.md** | Reference | Comparison with Auto-Claude | 2000 lines of detailed comparison |
| **DEEP_ANALYSIS.md** | Reference | Critical patterns | What to copy, what to skip |
| **ANALYSIS_COMPLETE.md** | Archive | Analysis summary | Completion marker |
| **PLANNING_COMPLETE.md** | Archive | Planning summary | Completion marker |
| **UPGRADE_PLAN_PART3.md** | Delete | Empty file | No content |

**Action Items:**
- Keep all files for reference (don't delete)
- Add note to each: "ARCHIVED - See ROADMAP.md for current plan"
- Use IMPLEMENTATION_ROADMAP.md as detailed guide for commits

---

## 7. First 5 Commits (Detailed)

### Commit 1: Project Structure & CLI Foundation
**Files:** cli/main.py, cli/commands.py, core/__init__.py, .multiagent/
**Goal:** Basic CLI with command stubs
**Test:** `python -m cli.main --help` shows all commands

### Commit 2: Worktree Manager MVP
**Files:** core/worktree_manager.py, tests/test_worktree.py
**Goal:** Create/commit/merge/cleanup worktrees
**Test:** Unit tests pass, manual worktree creation works

### Commit 3: Safe Shell Runner MVP
**Files:** core/shell_runner.py, tests/test_shell_runner.py
**Goal:** Allowlist/denylist, cwd restriction, logging
**Test:** Blocked commands raise errors, allowed commands log

### Commit 4: State Persistence + Resume
**Files:** core/state_store.py, tests/test_state_store.py
**Goal:** Atomic writes, load/save state.json
**Test:** State survives crashes, resume works

### Commit 5: Basic QA Loop
**Files:** core/qa_loop.py, tests/test_qa_loop.py
**Goal:** JSON validation, fix request generation
**Test:** Mock reviewer output triggers fixer agent

---

## 8. Success Criteria

### MVP (Week 1)
- [ ] CLI runs without errors
- [ ] Worktrees isolate tasks
- [ ] Shell commands are validated
- [ ] State persists across runs
- [ ] QA loop validates code

### V1 (Week 3)
- [ ] State machine phases work
- [ ] Crash recovery restores state
- [ ] Recurring issues detected
- [ ] Provider swapping works
- [ ] Integration tests pass

---

## 9. Next Actions

1. ✅ Create ROADMAP.md (this file)
2. ✅ Create PROGRESS.md (Kanban tracker)
3. ⏳ Commit 1: Project structure
4. ⏳ Commit 2: Worktree manager
5. ⏳ Commit 3: Shell runner

**See PROGRESS.md for detailed task tracking.**
