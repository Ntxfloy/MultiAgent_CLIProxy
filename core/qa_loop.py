"""QA loop with structured JSON validation."""

import json
from typing import Dict, Any, List, Optional, Callable


class QALoop:
    """Structured QA validation loop."""
    
    def __init__(self, max_iterations: int = 50):
        """
        Initialize QA loop.
        
        Args:
            max_iterations: Maximum fix iterations
        """
        self.max_iterations = max_iterations
        self.history: List[Dict[str, Any]] = []
    
    def run(
        self,
        reviewer_fn: Callable[[str], str],
        fixer_fn: Callable[[str, List[str]], str],
        initial_code: str
    ) -> Dict[str, Any]:
        """
        Run QA loop until approved or max iterations.
        
        Args:
            reviewer_fn: Function that reviews code and returns JSON
            fixer_fn: Function that fixes issues
            initial_code: Code to review
        
        Returns:
            Result dict with status, iterations, final_code
        """
        current_code = initial_code
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Get review
            review_output = reviewer_fn(current_code)
            review = self._parse_review(review_output)
            
            # Log iteration
            self.history.append({
                "iteration": iteration,
                "review": review,
                "code_length": len(current_code)
            })
            
            # Check if approved
            if review.get("approved", False):
                return {
                    "status": "approved",
                    "iterations": iteration,
                    "final_code": current_code,
                    "history": self.history
                }
            
            # Get issues
            issues = review.get("issues", [])
            if not issues:
                # No issues but not approved - treat as approved
                return {
                    "status": "approved",
                    "iterations": iteration,
                    "final_code": current_code,
                    "history": self.history
                }
            
            # Check for recurring issues
            recurring = self._detect_recurring_issues(issues)
            if recurring:
                return {
                    "status": "recurring_issues",
                    "iterations": iteration,
                    "final_code": current_code,
                    "recurring_issues": recurring,
                    "history": self.history
                }
            
            # Fix issues
            current_code = fixer_fn(current_code, issues)
        
        # Max iterations reached
        return {
            "status": "max_iterations",
            "iterations": iteration,
            "final_code": current_code,
            "history": self.history
        }
    
    def _parse_review(self, review_output: str) -> Dict[str, Any]:
        """
        Parse reviewer output as JSON.
        
        Args:
            review_output: Raw reviewer output
        
        Returns:
            Parsed review dict
        """
        try:
            # Try to extract JSON from output
            start = review_output.find("{")
            end = review_output.rfind("}") + 1
            
            if start >= 0 and end > start:
                json_str = review_output[start:end]
                return json.loads(json_str)
            
            # Fallback: treat as plain text
            return {
                "approved": "APPROVED" in review_output.upper(),
                "issues": [],
                "raw_output": review_output
            }
        except json.JSONDecodeError:
            # Fallback for invalid JSON
            return {
                "approved": "APPROVED" in review_output.upper(),
                "issues": [],
                "raw_output": review_output
            }
    
    def _detect_recurring_issues(self, current_issues: List[str]) -> Optional[List[str]]:
        """
        Detect recurring issues (exact match).
        
        Args:
            current_issues: Current iteration issues
        
        Returns:
            List of recurring issues or None
        """
        if len(self.history) < 3:
            return None
        
        # Check last 3 iterations
        recent_issues = [
            set(h["review"].get("issues", []))
            for h in self.history[-3:]
        ]
        
        # Find issues that appear in all recent iterations
        recurring = set(current_issues)
        for issue_set in recent_issues:
            recurring &= issue_set
        
        return list(recurring) if recurring else None
    
    def generate_fix_request(self, code: str, issues: List[str]) -> str:
        """
        Generate fix request prompt for coder.
        
        Args:
            code: Current code
            issues: List of issues to fix
        
        Returns:
            Fix request prompt
        """
        prompt = "The code has the following issues that need to be fixed:\n\n"
        
        for i, issue in enumerate(issues, 1):
            prompt += f"{i}. {issue}\n"
        
        prompt += "\nPlease fix these issues in the code.\n"
        prompt += f"\nCurrent code:\n```\n{code}\n```"
        
        return prompt
