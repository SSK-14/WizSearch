import yaml
from typing import Any, Dict, Optional, List

class ConfigManager:
    """Configuration management without singleton pattern."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self._config: Dict[str, Any] = {}
        self._config_path = config_path
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from config.yaml file."""
        try:
            with open(self._config_path, "r") as file:
                self._config = yaml.safe_load(file)
        except FileNotFoundError:
            raise ValueError(f"Configuration file not found at {self._config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {str(e)}")

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    @property
    def model_list(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        return self._config.get("model_list", [])

    def get_model_names(self) -> List[str]:
        """Get list of model names."""
        return [model["model_name"] for model in self.model_list]

    def is_vision_model(self, model_name: str) -> bool:
        """Check if a model supports vision capabilities."""
        for model in self.model_list:
            if model["model_name"] == model_name:
                model_info = model.get("model_info", {})
                return model_info.get("supports_vision", False)
        return False

    def select_model(self, model_name: str) -> Optional[str]:
        """Get LiteLLM model configuration for a given model name."""
        for model in self.model_list:
            if model["model_name"] == model_name:
                return model["litellm_params"]["model"]
        return None

    @property
    def embeddings_config(self) -> Dict[str, Any]:
        """Get embeddings model configuration."""
        return self._config.get("embeddings_model", {})

    @property
    def embedding_dimensions(self) -> Optional[int]:
        """Get embedding dimensions from config."""
        return self.embeddings_config.get("litellm_params", {}).get("dimensions")

    @property
    def dense_embedding_model(self) -> Optional[str]:
        """Get dense embedding model name from config."""
        return self.embeddings_config.get("litellm_params", {}).get("model")

    def validate_embeddings_config(self) -> None:
        """Validate that required embeddings configuration is present."""
        if not self.embedding_dimensions or not self.dense_embedding_model:
            raise ValueError("Dimensions or dense embedding model not found in config.yaml")

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key with optional default."""
        return self._config.get(key, default)

    def get_nested_config_value(self, *keys: str, default: Any = None) -> Any:
        """Get a nested configuration value by sequence of keys with optional default."""
        current = self._config
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return current
