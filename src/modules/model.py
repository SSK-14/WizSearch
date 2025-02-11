import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncGenerator
import streamlit as st
import litellm
from src.modules.context import app_context

class ModelBase(ABC):
    """Abstract base class defining model interface."""
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List[str]: Available model names
        """
        pass
    
    @abstractmethod
    def supports_vision(self, model_name: str) -> bool:
        """Check if model supports vision capabilities.
        
        Args:
            model_name: Name of model to check
            
        Returns:
            bool: True if model supports vision
        """
        pass
    
    @abstractmethod
    def select_model(self, model_name: str) -> str:
        """Select a model by name.
        
        Args:
            model_name: Name of model to select
            
        Returns:
            str: Selected model identifier
        """
        pass
    
    @abstractmethod
    async def generate(self, prompt: List[Dict[str, str]], name: str = "generate") -> str:
        """Generate completion from prompt.
        
        Args:
            prompt: List of message dictionaries
            name: Name for generation tracking
            
        Returns:
            str: Generated completion
        """
        pass
    
    @abstractmethod
    def stream(self, prompt: List[Dict[str, str]], name: str = "stream") -> AsyncGenerator[str, None]:
        """Stream completion from prompt.
        
        Args:
            prompt: List of message dictionaries
            name: Name for generation tracking
            
        Returns:
            AsyncGenerator[str, None]: Generated completion chunks
        """
        pass

class LiteLLMModel(ModelBase):
    """LiteLLM-based model implementation."""
    
    def __init__(self, context):
        self.config = context.config
        
        # Configure litellm
        litellm.modify_params = True
        litellm.drop_params = True
        
        # Setup callbacks if langfuse is configured
        if os.environ.get("LANGFUSE_SECRET_KEY") and os.environ.get("LANGFUSE_PUBLIC_KEY"):
            litellm.success_callback = ["langfuse"]
            litellm.failure_callback = ["langfuse"]

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self.config.get_model_names()

    def supports_vision(self, model_name: str) -> bool:
        """Check if model supports vision capabilities."""
        return self.config.is_vision_model(model_name)

    def select_model(self, model_name: str) -> str:
        """Select a model by name."""
        return self.config.select_model(model_name)

    def _get_generation_params(self, prompt: List[Dict[str, str]], name: str, stream: bool = False) -> Dict[str, Any]:
        """Get parameters for model generation.
        
        Args:
            prompt: List of message dictionaries
            name: Name for generation tracking
            stream: Whether to stream output
            
        Returns:
            Dict[str, Any]: Generation parameters
        """
        params = {
            "model": self.select_model(st.session_state.model_name),
            "messages": prompt,
            "metadata": {
                "generation_name": name,
                "trace_id": st.session_state.trace.id,
            },
            "max_tokens": st.session_state.max_tokens,
            "temperature": st.session_state.temperature,
        }
        if stream:
            params["stream"] = True
        return params

    async def generate(self, prompt: List[Dict[str, str]], name: str = "generate") -> str:
        """Generate completion from prompt."""
        params = self._get_generation_params(prompt, name)
        result = litellm.completion(**params)['choices'][0]['message']['content']
        return result

    def stream(self, prompt: List[Dict[str, str]], name: str = "stream") -> AsyncGenerator[str, None]:
        """Stream completion from prompt."""
        params = self._get_generation_params(prompt, name, stream=True)
        st.session_state.messages.append({"role": "assistant", "content": ""})
        
        for chunk in litellm.completion(**params):
            content = str(chunk['choices'][0]['delta']['content'])
            st.session_state.messages[-1]["content"] += content
            yield content

# Create global instance
model = LiteLLMModel(app_context)
