from typing import Optional, Dict, Any
from qdrant_client import QdrantClient
import os
from src.modules.config_manager import ConfigManager
from fastembed import SparseTextEmbedding

class AppContext:
    """Application context for managing core dependencies and services."""
    
    def __init__(self):
        self._config: Optional[ConfigManager] = None
        self._qdrant_client: Optional[QdrantClient] = None
        self._qdrant_memory_client: Optional[QdrantClient] = None
        self._sparse_embedding_model: Optional[SparseTextEmbedding] = None
        self._callbacks: Dict[str, Any] = {}

    @property
    def config(self) -> ConfigManager:
        """Get or initialize ConfigManager instance."""
        if self._config is None:
            self._config = ConfigManager()
        return self._config

    @property
    def qdrant_client(self) -> QdrantClient:
        """Get or initialize main QdrantClient instance."""
        if self._qdrant_client is None:
            qdrant_url = os.environ.get("QDRANT_URL")
            qdrant_api_key = os.environ.get("QDRANT_API_KEY")

            if qdrant_url:
                if qdrant_api_key:
                    self._qdrant_client = QdrantClient(
                        url=qdrant_url,
                        api_key=qdrant_api_key
                    )
                else:
                    if "http" in qdrant_url:
                        self._qdrant_client = QdrantClient(url=qdrant_url)
                    else:
                        self._qdrant_client = QdrantClient(path=qdrant_url)
            else:
                self._qdrant_client = QdrantClient(":memory:")
        
        return self._qdrant_client

    @property
    def qdrant_memory_client(self) -> QdrantClient:
        """Get or initialize memory QdrantClient instance."""
        if self._qdrant_memory_client is None:
            self._qdrant_memory_client = QdrantClient(":memory:")
        return self._qdrant_memory_client

    @property
    def sparse_embedding_model(self) -> SparseTextEmbedding:
        """Get or initialize SparseTextEmbedding instance."""
        if self._sparse_embedding_model is None:
            self._sparse_embedding_model = SparseTextEmbedding(
                model_name="Qdrant/bm25",
                providers=["CPUExecutionProvider"]
            )
        return self._sparse_embedding_model

    def register_callback(self, name: str, callback: Any) -> None:
        """Register a callback function."""
        self._callbacks[name] = callback

    def get_callback(self, name: str) -> Optional[Any]:
        """Get a registered callback function."""
        return self._callbacks.get(name)

# Global application context
app_context = AppContext()
