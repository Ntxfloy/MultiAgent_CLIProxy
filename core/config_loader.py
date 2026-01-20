"""Configuration loader for MultiAgent_CLIProxy."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Load and manage configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to config file (default: .multiagent/config.json)
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / ".multiagent" / "config.json"
        
        self.config_path = config_path
        self._config: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration not found: {self.config_path}\n"
                "Run 'multiagent init' to create configuration."
            )
        
        with open(self.config_path) as f:
            self._config = json.load(f)
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'models.architect')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        if self._config is None:
            self.load()
        
        # Support dot notation
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_base_url(self) -> str:
        """Get API base URL."""
        return self.get("base_url", "http://127.0.0.1:8317/v1")
    
    def get_api_key(self) -> str:
        """Get API key."""
        return self.get("api_key", "test-key-123")
    
    def get_model(self, role: str) -> str:
        """
        Get model for role.
        
        Args:
            role: Agent role (architect, reviewer, manager, coder, tester)
        
        Returns:
            Model name
        """
        return self.get(f"models.{role}", "gpt-5.2-codex")
    
    def get_fallback_chain(self, role: str) -> list:
        """
        Get fallback chain for role.
        
        Args:
            role: Agent role
        
        Returns:
            List of model names in fallback order
        """
        return self.get(f"fallback_chains.{role}", [])
    
    def get_max_iterations(self) -> int:
        """Get max QA loop iterations."""
        return self.get("max_iterations", 50)
    
    def get_worktree_base(self) -> str:
        """Get worktree base directory."""
        return self.get("worktree_base", ".multiagent/worktrees")
    
    def save(self, config: Dict[str, Any]):
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        self._config = config
    
    def update(self, key: str, value: Any):
        """
        Update configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: New value
        """
        if self._config is None:
            self.load()
        
        # Support dot notation
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        self.save(self._config)


# Global config instance
_config_loader: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """Get global config loader instance."""
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader()
    
    return _config_loader
