# Upgrade Plan Summary

> **⚠️ ARCHIVED - 2026-01-20**  
> This file is kept for reference only.  
> **See [ROADMAP.md](./ROADMAP.md) for current plan and [PROGRESS.md](./PROGRESS.md) for task tracking.**

## 📋 Documents Created

1. **UPGRADE_PLAN.md** (1258 lines)
   - Vision & architecture
   - CLI UX spec
   - Execution pipeline
   - Worktree isolation
   - Security & command policy

2. **UPGRADE_PLAN_PART2.md** (600+ lines)
   - QA loop implementation
   - Provider-agnostic model layer
   - Configuration examples

3. **IMPLEMENTATION_ROADMAP.md** (400+ lines)
   - First 10 commits (atomic, testable)
   - Migration plan from current codebase
   - Definition of Done
   - 10 most likely failures + mitigations

4. **REPO_ANALYSIS.md** (existing, 2000+ lines)
   - Detailed comparison of both repos
   - 20 colossal differences
   - Recommendations
   - Risks

---

## 🎯 Quick Reference

### Two Architecture Variants

**Variant A: Minimal MVP (3-5 days)**
- Simple orchestrator
- Basic QA (JSON validation)
- Worktrees + shell runner
- Single provider
- Good for: Prototyping, personal use

**Variant B: Scalable CLI (2-4 weeks)**
- State machine orchestrator
- Advanced QA (recurring detection, escalation)
- Multi-provider with fallback
- Crash recovery
- Queue + workers
- Good for: Production, teams

**Recommended:** Start with A, upgrade to B incrementally

---

### Key Features

| Feature | Current | After Upgrade |
|---------|---------|---------------|
| **Isolation** | Shared workspace | Git worktrees |
| **QA** | Keyword "APPROVED" | JSON protocol + loop |
| **Security** | No execution | Allowlist + validators |
| **State** | None | implementation_plan.json |
| **Recovery** | None | Checkpoint + resume |
| **Providers** | CLIProxy only | Any OpenAI-compatible |
| **Parallelism** | 1 task | 3-5 tasks |

---

### Timeline

**Week 1 (MVP):**
- Day 1-2: CLI + worktrees
- Day 3: Shell runner + security
- Day 4: Model client + QA loop
- Day 5: Integration + testing

**Week 2-3 (V1):**
- Day 6-8: State machine + phases
- Day 9-10: Fallback + retry
- Day 11-12: Crash recovery
- Day 13-14: Logging + debugging
- Day 15: Integration testing

**Week 4 (Polish):**
- Day 16-17: Test suite
- Day 18-19: Documentation
- Day 20: Bug fixes + release

**Total:** 3-4 weeks (160 hours)

---

### First 10 Commits

1. **CLI Foundation** (2h) - Argparse router
2. **Worktree Manager** (4h) - Isolation
3. **Shell Runner** (4h) - Security
4. **Model Client** (3h) - Provider interface
5. **QA Loop** (5h) - JSON validation
6. **State Machine** (6h) - Phases
7. **Fallback Logic** (3h) - Retry
8. **Crash Recovery** (4h) - Resume
9. **Logging** (3h) - Debugging
10. **Tests + Docs** (6h) - Quality

**Total:** 40 hours (1 week)

---

### Critical Paths

**Must Have (MVP):**
1. Worktree isolation → prevents file conflicts
2. QA JSON protocol → reliable approval
3. Shell security → safe execution

**Should Have (V1):**
4. State machine → phase tracking
5. Crash recovery → resume capability
6. Fallback logic → high availability

**Nice to Have (V1.5):**
7. Queue + workers → parallelism
8. Advanced logging → debugging
9. Performance optimizations

---

### Migration Strategy

**Keep:**
- `config.py` - Extend
- `requirements.txt` - Add deps
- `agents/registry_v3.py` - Convert to prompts
- `core/resilient_client.py` - Merge into fallback

**Refactor:**
- `run_factory.py` → `cli/commands.py`
- `core/swarm.py` → `core/orchestrator.py`
- `tools/file_ops.py` → `core/shell_runner.py`

**Remove:**
- `test_all_models.py` - Replace
- `core/engine.py` - Unused

**New Files:** ~20 files (cli/, core/, prompts/, tests/)

---

### Definition of Done

**Functional:**
- ✅ Create spec via CLI
- ✅ Run in isolated worktree
- ✅ QA validates with JSON
- ✅ Merge back to main
- ✅ Crash recovery works
- ✅ Safe command execution

**Quality:**
- ✅ 80%+ test coverage
- ✅ All docs complete
- ✅ No critical bugs

**Performance:**
- ✅ 3-5 parallel tasks
- ✅ Worktree creation < 5s
- ✅ QA iteration < 2 min

---

### Risk Mitigation

**Top 5 Risks:**

1. **Git conflicts** → Unique branch names
2. **Rate limits** → Fallback + backoff
3. **QA infinite loop** → Max iterations + escalation
4. **Command injection** → Allowlist + validation
5. **Disk space** → Auto-cleanup + warnings

---

### CLI Commands (Final)

```bash
# Setup
multiagent init --provider cliproxy --base-url http://127.0.0.1:8317/v1

# Spec management
multiagent spec new add-auth
multiagent spec list
multiagent spec show add-auth

# Execution
multiagent run add-auth --isolated
multiagent resume add-auth
multiagent status add-auth

# QA
multiagent qa add-auth
multiagent qa-report add-auth

# Worktrees
multiagent worktree list
multiagent worktree merge add-auth
multiagent worktree cleanup --older-than 30d

# Review & merge
multiagent review add-auth
multiagent merge add-auth --delete-worktree

# Debugging
multiagent logs add-auth --tail 50
multiagent debug add-auth --show-state

# Queue (V1.5)
multiagent queue add feature-a
multiagent worker start --max-concurrent 3
```

---

### File Structure (Final)

```
MultiAgent_CLIProxy/
├── cli/
│   ├── main.py              # Entry point
│   ├── commands.py          # Command implementations
│   └── debug.py             # Debug commands
├── core/
│   ├── worktree.py          # Worktree manager
│   ├── shell_runner.py      # Safe shell execution
│   ├── stack_detector.py    # Auto-detect stack
│   ├── model_client.py      # Model interface
│   ├── orchestrator.py      # State machine
│   ├── qa_loop.py           # QA validation
│   ├── implementation_plan.py # Plan management
│   ├── recovery.py          # Crash recovery
│   ├── logger.py            # Structured logging
│   └── providers/
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
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

---

### Next Actions

**Immediate (Today):**
1. Review all plan documents
2. Set up git branches
3. Create `.multiagent/` directory structure

**Week 1 (MVP):**
1. Implement commits 1-5 (CLI, worktrees, QA)
2. Test each commit
3. Dogfood on simple task

**Week 2-3 (V1):**
1. Implement commits 6-9 (state machine, recovery)
2. Integration testing
3. Bug fixes

**Week 4 (Polish):**
1. Implement commit 10 (tests, docs)
2. Performance testing
3. Release V1

---

### Success Metrics

**MVP Success:**
- Can run 1 task end-to-end
- QA approves correctly
- No file conflicts
- Commands are safe

**V1 Success:**
- Can run 3-5 parallel tasks
- Recovers from crashes
- 80%+ test coverage
- Docs complete

**V1.5 Success:**
- Can run 10+ parallel tasks
- Queue system works
- Performance optimized
- Production-ready

---

### Resources

**Reference Implementations:**
- Auto-Claude: `apps/backend/core/worktree.py` (worktrees)
- Auto-Claude: `apps/backend/qa/loop.py` (QA loop)
- Auto-Claude: `apps/backend/security/main.py` (security)

**Dependencies:**
- AutoGen 0.4.x (keep)
- httpx (add for HTTP client)
- pyyaml (add for config)
- pytest (add for tests)

**Documentation:**
- UPGRADE_PLAN.md - Full architecture
- IMPLEMENTATION_ROADMAP.md - Step-by-step guide
- REPO_ANALYSIS.md - Comparison & rationale

---

## 🚀 Ready to Start!

All planning is complete. The path is clear. Time to build!

**First command:**
```bash
git checkout -b feature/cli-foundation
mkdir -p cli core prompts tests .multiagent
touch cli/__init__.py cli/main.py
# Start coding!
```
