# Next Session Guide

**Date:** 2026-01-20  
**Status:** MVP Complete (5/5 tasks done)  
**For:** Next AI assistant continuing this project

---

## 🎯 What's Done (MVP)

✅ **TASK-001**: CLI foundation (8 commands, argparse-based)  
✅ **TASK-002**: Worktree manager (git worktree isolation)  
✅ **TASK-003**: Shell runner (allowlist/denylist security)  
✅ **TASK-004**: State store (atomic writes, persistence)  
✅ **TASK-005**: QA loop (JSON validation, recurring issues)

**Stats:**
- 7 commits pushed to GitHub
- 9 core modules created
- 22 unit tests (all passing)
- 0 compilation errors

---

## 📋 Next Steps (V1 - Weeks 2-3)

**Priority order:**

### TASK-006: State Machine Pipeline
**Goal:** Phase-based execution (planning → impl → test → review)

**Files to create:**
- `core/pipeline.py` - StateMachine class
- `tests/test_pipeline.py` - Unit tests

**Key features:**
- Phases with dependencies
- Checkpoint after each phase
- Phase transitions with validation

**Reference:** See IMPLEMENTATION_ROADMAP.md lines 200-350

---

### TASK-007: Crash Recovery
**Goal:** Resume from last checkpoint

**Files to modify:**
- `cli/commands.py` - Implement `cmd_resume()`
- `core/pipeline.py` - Add resume logic

**Key features:**
- Load state from .multiagent/tasks/{task_id}.json
- Restore worktree
- Continue from interrupted phase

---

### TASK-008: Advanced QA (Fuzzy Matching)
**Goal:** Better recurring issue detection

**Files to modify:**
- `core/qa_loop.py` - Add fuzzy matching (difflib)
- `tests/test_qa_loop.py` - Add fuzzy tests

**Key features:**
- Fuzzy string matching for similar issues
- Issue history tracking
- Self-correction prompts

---

### TASK-009: Provider Abstraction
**Goal:** Easy model swapping

**Files to create:**
- `core/model_client.py` - Abstract client interface
- `tests/test_model_client.py` - Unit tests

**Key features:**
- Unified interface for OpenAI/CLIProxy/local
- Fallback chain support (already in config)
- Easy provider switching

---

### TASK-010: Integration Tests
**Goal:** End-to-end testing

**Files to create:**
- `tests/integration/test_e2e.py`

**Key features:**
- Full workflow: spec → run → review → merge
- Real git operations (in test repo)
- Real shell commands (safe subset)

---

## 🚨 Important Notes

### DO NOT:
- ❌ Create new planning files (ROADMAP.md is source of truth)
- ❌ Make massive code changes in one commit
- ❌ Skip tests (every module needs tests)
- ❌ Use absolute paths outside workspace

### DO:
- ✅ Follow commit-by-commit approach (atomic commits)
- ✅ Update PROGRESS.md after each task
- ✅ Run tests before committing: `python -m unittest tests.test_* -v`
- ✅ Check compilation: `python -m compileall <files>`
- ✅ Push to GitHub after each commit: `git push`

---

## 🔧 Quick Commands

**Run CLI:**
```bash
cd testkiro/MultiAgent_CLIProxy
python -m cli.main --help
python -m cli.main init
python -m cli.main spec new test-task
```

**Run tests:**
```bash
python -m unittest discover tests -v
python -m unittest tests.test_worktree -v
```

**Check status:**
```bash
git status
git log --oneline -5
```

---

## 📚 Key Files

**Source of truth:**
- `ROADMAP.md` - Architecture, plan, modules
- `PROGRESS.md` - Task tracker (Kanban)

**Reference (detailed specs):**
- `IMPLEMENTATION_ROADMAP.md` - Commit-by-commit guide
- `UPGRADE_PLAN.md` - Full architecture (1258 lines)
- `DEEP_ANALYSIS.md` - Critical patterns from Auto-Claude

**Code:**
- `cli/main.py` - CLI entrypoint
- `cli/commands.py` - Command implementations
- `core/` - Core modules (5 files)
- `tests/` - Unit tests (4 files)

---

## 🎨 Code Style

- Docstrings for all public methods
- Type hints where helpful
- Keep functions small (<50 lines)
- Prefer composition over inheritance
- Use pathlib.Path for file paths
- Atomic operations (tmp+rename for writes)

---

## 🐛 Known Issues

None currently. All tests passing.

---

## 💡 Tips for Next AI

1. **Read PROGRESS.md first** - it has the current status
2. **Follow TASK-006 next** - state machine is critical
3. **Keep commits small** - easier to review and revert
4. **Test everything** - no code without tests
5. **Update docs** - PROGRESS.md after each task
6. **Push often** - don't keep work local

---

## 📞 Context for User

User wants:
- CLI-first (no UI)
- Provider-agnostic (OpenAI-compatible endpoints)
- Auto-Claude-level infrastructure
- Worktree isolation
- Structured QA
- Security (command validation)
- Crash recovery

User does NOT want:
- Electron UI
- Claude Code subscriptions
- Massive code dumps
- New planning files

---

## 🚀 Start Next Session With

```
Hi! I'm continuing the MultiAgent_CLIProxy upgrade.

I've read NEXT_SESSION.md and PROGRESS.md.
MVP is complete (5/5 tasks).

Ready to start TASK-006 (State Machine Pipeline)?
I'll work commit-by-commit with tests.
```

---

Good luck! 🎯
