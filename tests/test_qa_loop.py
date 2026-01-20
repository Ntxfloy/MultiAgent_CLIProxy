"""Tests for QA loop."""

import unittest
from core.qa_loop import QALoop


class TestQALoop(unittest.TestCase):
    """Test QALoop class."""
    
    def test_approved_first_iteration(self):
        """Test immediate approval."""
        def reviewer(code):
            return '{"approved": true, "issues": []}'
        
        def fixer(code, issues):
            return code
        
        loop = QALoop(max_iterations=10)
        result = loop.run(reviewer, fixer, "good code")
        
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["iterations"], 1)
        self.assertEqual(result["final_code"], "good code")
    
    def test_fix_and_approve(self):
        """Test fix iteration then approval."""
        iteration_count = [0]
        
        def reviewer(code):
            iteration_count[0] += 1
            if iteration_count[0] == 1:
                return '{"approved": false, "issues": ["missing semicolon"]}'
            return '{"approved": true, "issues": []}'
        
        def fixer(code, issues):
            return code + ";"
        
        loop = QALoop(max_iterations=10)
        result = loop.run(reviewer, fixer, "code")
        
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["iterations"], 2)
        self.assertEqual(result["final_code"], "code;")
    
    def test_max_iterations(self):
        """Test max iterations limit."""
        iteration_count = [0]
        
        def reviewer(code):
            iteration_count[0] += 1
            return f'{{"approved": false, "issues": ["issue {iteration_count[0]}"]}}' 
        
        def fixer(code, issues):
            return code + "x"
        
        loop = QALoop(max_iterations=3)
        result = loop.run(reviewer, fixer, "code")
        
        self.assertEqual(result["status"], "max_iterations")
        self.assertEqual(result["iterations"], 3)
    
    def test_recurring_issues(self):
        """Test recurring issue detection."""
        def reviewer(code):
            return '{"approved": false, "issues": ["same issue"]}'
        
        def fixer(code, issues):
            return code  # Don't actually fix
        
        loop = QALoop(max_iterations=10)
        result = loop.run(reviewer, fixer, "code")
        
        # Should detect recurring after 3+ iterations
        self.assertEqual(result["status"], "recurring_issues")
        self.assertIn("same issue", result["recurring_issues"])
    
    def test_parse_json_review(self):
        """Test JSON parsing from review output."""
        loop = QALoop()
        
        # Valid JSON
        review = loop._parse_review('{"approved": true, "issues": []}')
        self.assertTrue(review["approved"])
        
        # JSON with surrounding text
        review = loop._parse_review('Some text {"approved": false, "issues": ["bug"]} more text')
        self.assertFalse(review["approved"])
        self.assertEqual(review["issues"], ["bug"])
        
        # Plain text with APPROVED
        review = loop._parse_review('The code looks good. APPROVED')
        self.assertTrue(review["approved"])
    
    def test_generate_fix_request(self):
        """Test fix request generation."""
        loop = QALoop()
        
        request = loop.generate_fix_request(
            "def foo(): pass",
            ["missing docstring", "no type hints"]
        )
        
        self.assertIn("missing docstring", request)
        self.assertIn("no type hints", request)
        self.assertIn("def foo(): pass", request)


if __name__ == "__main__":
    unittest.main()
