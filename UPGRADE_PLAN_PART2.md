# MultiAgent_CLIProxy Upgrade Plan - Part 2

## 7. QA Loop (MUST)

### Overview

Structured QA loop with JSON-based approval protocol, automatic fixing, and recurring issue detection. Replaces keyword-based "APPROVED" check with reliable validation.

### QA Protocol

**File:** `core/qa_loop.py`

```python
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class QAIssue:
    """Single QA issue."""
    id: str
    title: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    file: str | None = None
    line: int | None = None
    suggested_fix: str | None = None

@dataclass
class QAResult:
    """Result of QA review."""
    status: str  # "approved", "rejected"
    iteration: int
    issues_found: list[QAIssue]
    timestamp: datetime
    test_results: dict | None = None

class QALoop:
    """Structured QA validation loop."""
    
    MAX_ITERATIONS = 50
    RECURRING_THRESHOLD = 3
    
    def __init__(
        self,
        spec_dir: Path,
        model_client,
        shell_runner,
        max_iterations: int = 50
    ):
        self.spec_dir = spec_dir
        self.model_client = model_client
        self.shell_runner = shell_runner
        self.max_iterations = max_iterations
        self.history_file = spec_dir / "qa_history.json"
    
    async def run_validation_loop(self) -> QAResult:
        """
        Run QA loop until approved or max iterations.
        
        Returns:
            Final QA result
        """
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- QA Iteration {iteration}/{self.max_iterations} ---")
            
            # Run QA reviewer
            qa_result = await self._run_qa_reviewer(iteration)
            
            # Record iteration
            self._record_iteration(qa_result)
            
            if qa_result.status == "approved":
                print("✅ QA APPROVED")
                return qa_result
            
            # Check for recurring issues
            if self._has_recurring_issues(qa_result):
                print("⚠️  Recurring issues detected, escalating...")
                self._escalate_to_human(qa_result)
                return qa_result
            
            # Run fixer
            print(f"❌ QA found {len(qa_result.issues_found)} issues, running fixer...")
            await self._run_qa_fixer(qa_result)
        
        # Max iterations reached
        print(f"⚠️  Max iterations ({self.max_iterations}) reached")
        self._escalate_to_human(qa_result)
        return qa_result
    
    async def _run_qa_reviewer(self, iteration: int) -> QAResult:
        """Run QA reviewer agent."""
        # Load spec
        spec = self._load_spec()
        
        # Run tests
        test_results = self._run_tests()
        
        # Build prompt
        prompt = self._build_qa_prompt(spec, test_results, iteration)
        
        # Call model
        response = await self.model_client.complete(
            prompt=prompt,
            tools=[self._get_qa_tools()],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        qa_data = json.loads(response.content)
        
        # Validate schema
        if not self._validate_qa_response(qa_data):
            raise ValueError("Invalid QA response format")
        
        # Convert to QAResult
        issues = [
            QAIssue(**issue_data)
            for issue_data in qa_data.get("issues_found", [])
        ]
        
        return QAResult(
            status=qa_data["status"],
            iteration=iteration,
            issues_found=issues,
            timestamp=datetime.now(),
            test_results=test_results
        )
    
    async def _run_qa_fixer(self, qa_result: QAResult):
        """Run QA fixer agent to address issues."""
        # Build fixer prompt
        prompt = self._build_fixer_prompt(qa_result)
        
        # Call model with tools
        response = await self.model_client.complete(
            prompt=prompt,
            tools=[
                self._get_file_tools(),
                self._get_shell_tools()
            ]
        )
        
        # Fixer makes changes via tool calls
        # Auto-commit after fixes
        from core.worktree import WorktreeManager
        wt_manager = WorktreeManager(self.spec_dir.parent.parent)
        wt_manager.commit_changes(
            self.spec_dir.name,
            f"auto: Fix QA issues (iteration {qa_result.iteration})"
        )
    
    def _run_tests(self) -> dict:
        """Run project tests and return results."""
        # Detect test framework
        test_cmd = self._detect_test_command()
        
        if not test_cmd:
            return {"status": "no_tests", "message": "No test framework detected"}
        
        # Run tests
        result = self.shell_runner.execute(test_cmd, timeout=600)
        
        # Parse output (framework-specific)
        return {
            "status": "passed" if result.success else "failed",
            "command": test_cmd,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code
        }
    
    def _detect_test_command(self) -> str | None:
        """Detect test command based on project structure."""
        project_dir = self.spec_dir.parent.parent
        
        if (project_dir / "pytest.ini").exists() or (project_dir / "pyproject.toml").exists():
            return "pytest"
        elif (project_dir / "package.json").exists():
            return "npm test"
        elif (project_dir / "Cargo.toml").exists():
            return "cargo test"
        elif (project_dir / "go.mod").exists():
            return "go test ./..."
        
        return None
    
    def _has_recurring_issues(self, current_result: QAResult) -> bool:
        """Check if any issues are recurring (3+ times)."""
        if not self.history_file.exists():
            return False
        
        history = json.loads(self.history_file.read_text())
        
        for current_issue in current_result.issues_found:
            # Normalize title for comparison
            current_title = self._normalize_issue_title(current_issue.title)
            
            # Count occurrences in history
            occurrences = 0
            for past_iteration in history:
                for past_issue in past_iteration.get("issues_found", []):
                    past_title = self._normalize_issue_title(past_issue["title"])
                    
                    # Check similarity (Levenshtein distance > 80%)
                    if self._similarity(current_title, past_title) > 0.8:
                        occurrences += 1
            
            if occurrences >= self.RECURRING_THRESHOLD:
                return True
        
        return False
    
    def _normalize_issue_title(self, title: str) -> str:
        """Normalize issue title for comparison."""
        import re
        # Lowercase, remove punctuation
        return re.sub(r'[^\w\s]', '', title.lower())
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings (0-1)."""
        # Simple implementation: Levenshtein distance
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _record_iteration(self, qa_result: QAResult):
        """Record QA iteration to history."""
        if self.history_file.exists():
            history = json.loads(self.history_file.read_text())
        else:
            history = []
        
        history.append({
            "iteration": qa_result.iteration,
            "status": qa_result.status,
            "issues_count": len(qa_result.issues_found),
            "issues_found": [
                {
                    "id": issue.id,
                    "title": issue.title,
                    "severity": issue.severity,
                    "file": issue.file,
                    "line": issue.line
                }
                for issue in qa_result.issues_found
            ],
            "timestamp": qa_result.timestamp.isoformat()
        })
        
        self.history_file.write_text(json.dumps(history, indent=2))
    
    def _escalate_to_human(self, qa_result: QAResult):
        """Create escalation file for human review."""
        escalation_file = self.spec_dir / "ESCALATION.md"
        
        content = f"""# QA Escalation - Human Review Required

## Reason
{"Recurring issues detected" if self._has_recurring_issues(qa_result) else f"Max iterations ({self.max_iterations}) reached"}

## Current Issues ({len(qa_result.issues_found)})

"""
        
        for issue in qa_result.issues_found:
            content += f"""### {issue.title} ({issue.severity})

**File:** {issue.file or "N/A"}  
**Line:** {issue.line or "N/A"}

{issue.description}

"""
            if issue.suggested_fix:
                content += f"**Suggested Fix:**\n{issue.suggested_fix}\n\n"
        
        content += f"""
## Next Steps

1. Review the issues above
2. Apply fixes manually or update the code
3. Re-run QA: `multiagent qa {self.spec_dir.name}`

## Iteration History

Total iterations: {qa_result.iteration}
"""
        
        escalation_file.write_text(content)
        print(f"\n📝 Escalation file created: {escalation_file}")
    
    def _build_qa_prompt(self, spec: dict, test_results: dict, iteration: int) -> str:
        """Build QA reviewer prompt."""
        return f"""You are a QA Reviewer. Review the implementation against the spec.

## Spec

**Task:** {spec['task']}

**Acceptance Criteria:**
{chr(10).join(f"- {criterion}" for criterion in spec['acceptance_criteria'])}

## Test Results

{json.dumps(test_results, indent=2)}

## Your Task

1. Review the code changes (use read_file tool)
2. Check if acceptance criteria are met
3. Check for bugs, security issues, style problems
4. Run additional tests if needed (use execute_bash tool)

## Response Format (STRICT JSON)

You MUST respond with valid JSON in this exact format:

{{
  "status": "approved" | "rejected",
  "issues_found": [
    {{
      "id": "qa-1",
      "title": "Brief issue title",
      "severity": "critical" | "high" | "medium" | "low",
      "description": "Detailed description",
      "file": "path/to/file.py",
      "line": 42,
      "suggested_fix": "How to fix this issue"
    }}
  ],
  "summary": "Overall assessment"
}}

**IMPORTANT:**
- If ALL acceptance criteria are met and no issues found: status = "approved", issues_found = []
- If ANY issues found: status = "rejected", list all issues
- Be thorough but fair
- This is iteration {iteration}/{self.MAX_ITERATIONS}
"""
    
    def _build_fixer_prompt(self, qa_result: QAResult) -> str:
        """Build QA fixer prompt."""
        issues_text = "\n\n".join(
            f"### Issue {i+1}: {issue.title} ({issue.severity})\n"
            f"**File:** {issue.file}\n"
            f"**Line:** {issue.line}\n"
            f"**Description:** {issue.description}\n"
            f"**Suggested Fix:** {issue.suggested_fix or 'N/A'}"
            for i, issue in enumerate(qa_result.issues_found)
        )
        
        return f"""You are a QA Fixer. Fix the issues found by the QA reviewer.

## Issues to Fix ({len(qa_result.issues_found)})

{issues_text}

## Your Task

1. Read the relevant files
2. Apply fixes for each issue
3. Make minimal changes (only fix the issues)
4. Do NOT re-run QA (the system will do that)

Use the provided tools:
- read_file(path) - Read file contents
- write_file(path, content) - Write file
- execute_bash(command) - Run commands (tests, linters, etc.)

Work through the issues systematically. After fixing, the QA reviewer will check again.
"""
    
    def _validate_qa_response(self, qa_data: dict) -> bool:
        """Validate QA response schema."""
        required_fields = ["status", "issues_found"]
        
        if not all(field in qa_data for field in required_fields):
            return False
        
        if qa_data["status"] not in ["approved", "rejected"]:
            return False
        
        if not isinstance(qa_data["issues_found"], list):
            return False
        
        # Validate each issue
        for issue in qa_data["issues_found"]:
            required_issue_fields = ["id", "title", "severity", "description"]
            if not all(field in issue for field in required_issue_fields):
                return False
        
        return True
    
    def _load_spec(self) -> dict:
        """Load spec.yaml."""
        import yaml
        spec_file = self.spec_dir / "spec.yaml"
        return yaml.safe_load(spec_file.read_text())
    
    def _get_qa_tools(self) -> list:
        """Get tools for QA reviewer."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read file contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_bash",
                    "description": "Execute shell command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to run"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
    
    def _get_file_tools(self) -> list:
        """Get file operation tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read file contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write file contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                }
            }
        ]
    
    def _get_shell_tools(self) -> list:
        """Get shell execution tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_bash",
                    "description": "Execute shell command safely",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
```

### QA Report Format

**File:** `.multiagent/specs/{spec-name}/qa_report.json`

```json
{
  "spec_name": "add-authentication",
  "final_status": "approved",
  "total_iterations": 3,
  "total_issues_found": 7,
  "unique_issues": 5,
  
  "iterations": [
    {
      "iteration": 1,
      "status": "rejected",
      "issues_count": 5,
      "issues": [
        {
          "id": "qa-1",
          "title": "Missing error handling in login",
          "severity": "high",
          "file": "src/auth.py",
          "line": 42,
          "description": "Function doesn't handle network errors",
          "suggested_fix": "Add try-except block for requests.exceptions"
        }
      ],
      "timestamp": "2026-01-20T12:00:00Z",
      "duration_seconds": 120
    },
    {
      "iteration": 2,
      "status": "rejected",
      "issues_count": 2,
      "timestamp": "2026-01-20T12:15:00Z"
    },
    {
      "iteration": 3,
      "status": "approved",
      "issues_count": 0,
      "timestamp": "2026-01-20T12:30:00Z"
    }
  ],
  
  "test_results": {
    "status": "passed",
    "command": "pytest",
    "passed": 15,
    "failed": 0,
    "coverage": 85.5
  }
}
```

---

## 8. Provider-Agnostic Model Layer

### Overview

Support any OpenAI-compatible API endpoint through adapter pattern. No vendor lock-in.

### Model Client Interface

**File:** `core/model_client.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class ModelMessage:
    """Single message in conversation."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None

@dataclass
class ModelResponse:
    """Response from model."""
    content: str
    tool_calls: list[dict] | None = None
    finish_reason: str  # "stop", "tool_calls", "length"
    usage: dict | None = None

class ModelClient(ABC):
    """Abstract base class for model providers."""
    
    @abstractmethod
    async def complete(
        self,
        messages: list[ModelMessage],
        tools: list[dict] | None = None,
        response_format: dict | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> ModelResponse:
        """
        Generate completion.
        
        Args:
            messages: Conversation history
            tools: Available tools (OpenAI function calling format)
            response_format: Response format (e.g., {"type": "json_object"})
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        
        Returns:
            ModelResponse with content and/or tool calls
        """
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if provider supports tool calling."""
        pass
    
    @abstractmethod
    def supports_json_mode(self) -> bool:
        """Check if provider supports JSON mode."""
        pass
```

### OpenAI-Compatible Provider

**File:** `core/providers/openai_compatible.py`

```python
import httpx
from core.model_client import ModelClient, ModelMessage, ModelResponse

class OpenAICompatibleProvider(ModelClient):
    """Provider for OpenAI-compatible APIs (OpenAI, CLIProxy, OpenRouter, etc.)."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = 300
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def complete(
        self,
        messages: list[ModelMessage],
        tools: list[dict] | None = None,
        response_format: dict | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> ModelResponse:
        """Generate completion via OpenAI-compatible API."""
        # Convert messages to API format
        api_messages = [
            {
                "role": msg.role,
                "content": msg.content,
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {})
            }
            for msg in messages
        ]
        
        # Build request
        request_data = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        if tools:
            request_data["tools"] = tools
        
        if response_format:
            request_data["response_format"] = response_format
        
        # Make request
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            json=request_data,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Parse response
        choice = data["choices"][0]
        message = choice["message"]
        
        return ModelResponse(
            content=message.get("content", ""),
            tool_calls=message.get("tool_calls"),
            finish_reason=choice["finish_reason"],
            usage=data.get("usage")
        )
    
    def supports_tools(self) -> bool:
        """OpenAI-compatible APIs typically support tools."""
        return True
    
    def supports_json_mode(self) -> bool:
        """OpenAI-compatible APIs typically support JSON mode."""
        return True
```

### Fallback & Retry Logic

**File:** `core/model_client_with_fallback.py`

```python
from core.model_client import ModelClient, ModelMessage, ModelResponse
import asyncio
import time

class ModelClientWithFallback(ModelClient):
    """Model client with automatic fallback and retry."""
    
    def __init__(
        self,
        primary_client: ModelClient,
        fallback_clients: list[ModelClient],
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        self.primary_client = primary_client
        self.fallback_clients = fallback_clients
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.current_client_index = 0
    
    async def complete(
        self,
        messages: list[ModelMessage],
        tools: list[dict] | None = None,
        response_format: dict | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> ModelResponse:
        """Complete with automatic fallback."""
        clients = [self.primary_client] + self.fallback_clients
        last_error = None
        
        for client_index, client in enumerate(clients):
            for attempt in range(self.max_retries):
                try:
                    response = await client.complete(
                        messages=messages,
                        tools=tools,
                        response_format=response_format,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    if client_index > 0:
                        print(f"✅ Fallback successful: using client {client_index}")
                    
                    return response
                
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    
                    # Check if retryable
                    is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower()
                    is_server_error = "500" in error_str or "503" in error_str
                    
                    if is_rate_limit or is_server_error:
                        if attempt < self.max_retries - 1:
                            # Exponential backoff
                            delay = self.retry_delay * (2 ** attempt)
                            print(f"⚠️  Retrying in {delay}s... (attempt {attempt + 1}/{self.max_retries})")
                            await asyncio.sleep(delay)
                            continue
                    
                    # Not retryable or max retries reached, try next client
                    if client_index < len(clients) - 1:
                        print(f"⚠️  Client {client_index} failed, trying fallback...")
                        break
        
        # All clients exhausted
        raise Exception(f"All model clients failed. Last error: {last_error}")
    
    def supports_tools(self) -> bool:
        return self.primary_client.supports_tools()
    
    def supports_json_mode(self) -> bool:
        return self.primary_client.supports_json_mode()
```

### Configuration

**File:** `.multiagent/config.yaml`

```yaml
# Model provider configuration
providers:
  cliproxy:
    type: openai_compatible
    base_url: http://127.0.0.1:8317/v1
    api_key: test-key-123
    models:
      primary: gpt-5.2-codex
      fallback:
        - gpt-5.1-codex
        - gemini-2.5-pro
  
  openai:
    type: openai_compatible
    base_url: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}
    models:
      primary: gpt-4-turbo
      fallback:
        - gpt-4
        - gpt-3.5-turbo
  
  openrouter:
    type: openai_compatible
    base_url: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
    models:
      primary: anthropic/claude-3-opus
      fallback:
        - anthropic/claude-3-sonnet
        - openai/gpt-4-turbo

# Default provider
default_provider: cliproxy

# Phase-specific model overrides
phase_models:
  planning: gpt-5.2-codex
  implementation: gemini-2.5-flash
  qa: gpt-5.2-codex

# Retry configuration
retry:
  max_retries: 3
  initial_delay: 2.0
  max_delay: 60.0
  exponential_base: 2.0
```

---

