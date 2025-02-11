from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from qdrant_client import models
from litellm import embedding
from src.modules.context import app_context

class VectorStoreBase(ABC):
    """Abstract base class defining vector store interface."""
    
    @abstractmethod
    def create_embeddings(self, text: str) -> List[float]:
        """Create embeddings for given text.
        
        Args:
            text: Text to create embeddings for
            
        Returns:
            List[float]: Vector embeddings
        """
        pass
    
    @abstractmethod
    def create_collection(self, collection_name: str) -> None:
        """Create a new collection.
        
        Args:
            collection_name: Name of collection to create
        """
        pass
    
    @abstractmethod
    def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]], is_memory: bool = False) -> None:
        """Insert documents into a collection.
        
        Args:
            collection_name: Target collection name
            documents: List of documents to insert
            is_memory: Whether to use memory store
        """
        pass
    
    @abstractmethod
    def search(self, collection_name: str, query: str, top_k: int = 4, is_memory: bool = False) -> List[Dict[str, Any]]:
        """Search for documents in a collection.
        
        Args:
            collection_name: Collection to search in
            query: Search query
            top_k: Number of results to return
            is_memory: Whether to use memory store
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        pass
    
    @abstractmethod
    def list_collections(self) -> List[str]:
        """Get all collection names.
        
        Returns:
            List[str]: Collection names
        """
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Any:
        """Get information about a collection.
        
        Args:
            collection_name: Collection to get info for
            
        Returns:
            Any: Collection information
        """
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection.
        
        Args:
            collection_name: Collection to delete
        """
        pass
    
    @abstractmethod
    def get_all_documents(self, collection_name: str, is_memory: bool = False) -> List[str]:
        """Get all documents from a collection.
        
        Args:
            collection_name: Collection to get documents from
            is_memory: Whether to use memory store
            
        Returns:
            List[str]: All documents
        """
        pass

class QdrantVectorStore(VectorStoreBase):
    """Qdrant vector store implementation."""
    
    def __init__(self, context):
        self.config = context.config
        self.qdrant_client = context.qdrant_client
        self.qdrant_memory_client = context.qdrant_memory_client
        self.sparse_embedding_model = context.sparse_embedding_model
        
        # Validate config on initialization
        self.config.validate_embeddings_config()
        self.dimensions = self.config.embedding_dimensions
        self.dense_embedding_model = self.config.dense_embedding_model

    def create_embeddings(self, text: str) -> List[float]:
        """Create dense embeddings for given text."""
        response = embedding(
            model=self.dense_embedding_model,
            input=[text],
        )
        return response.data[0]["embedding"]

    def _create_collection_internal(self, client: Any, collection: str) -> None:
        """Internal method to create collection."""
        client.create_collection(
            collection,
            vectors_config={
                "text-dense": models.VectorParams(
                    size=self.dimensions,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "text-sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                )
            }
        )

    def create_collection(self, collection_name: str) -> None:
        """Create a new collection."""
        self._create_collection_internal(self.qdrant_client, collection_name)

    def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]], is_memory: bool = False) -> None:
        """Insert documents into a collection."""
        client = self.qdrant_memory_client if is_memory else self.qdrant_client
        
        if collection_name not in self.list_collections():
            self._create_collection_internal(client, collection_name)
        
        for idx, doc in enumerate(documents, 1):
            text = doc.page_content
            dense_embedding = self.create_embeddings(text)
            sparse_embedding = list(self.sparse_embedding_model.query_embed(text))[0]
            
            client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=idx,
                        payload={
                            "metadata": doc.metadata,
                            "text": text
                        },
                        vector={
                            "text-sparse": models.SparseVector(
                                values=sparse_embedding.values,
                                indices=sparse_embedding.indices,
                            ),
                            "text-dense": dense_embedding,
                        }
                    )
                ],
            )

    def search(self, collection_name: str, query: str, top_k: int = 4, is_memory: bool = False) -> List[Dict[str, Any]]:
        """Search for documents in a collection."""
        client = self.qdrant_memory_client if is_memory else self.qdrant_client

        dense_embedding = self.create_embeddings(query)
        sparse_embedding = list(self.sparse_embedding_model.query_embed(query))[0]
        
        search_results = client.query_points(
            collection_name=collection_name,
            prefetch=[
                models.Prefetch(query=sparse_embedding.as_object(), using="text-sparse", limit=top_k),
                models.Prefetch(query=dense_embedding, using="text-dense", limit=top_k),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF), 
            limit=top_k,
        )

        return [{"text": item.payload.get("text"), "metadata": item.payload.get("metadata")} for item in search_results.points]

    def list_collections(self) -> List[str]:
        """Get all collection names."""
        collections_tuple = self.qdrant_client.get_collections()
        return [collection.name for collection in collections_tuple.collections]

    def get_collection_info(self, collection_name: str) -> Any:
        """Get information about a collection."""
        return self.qdrant_client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        self.qdrant_client.delete_collection(collection_name=collection_name)

    def get_all_documents(self, collection_name: str, is_memory: bool = False) -> List[str]:
        """Get all documents from a collection."""
        client = self.qdrant_memory_client if is_memory else self.qdrant_client

        result = client.count(collection_name=collection_name)
        records = client.scroll(
            collection_name=collection_name,
            limit=result.count,
            with_payload=True,
        )
        joined_text = " ".join(record.payload['text'] for record in records[0])
        cleaned_text = joined_text.replace("\t", " ").replace("\n", " ").replace("\r", " ")
        return [cleaned_text[i:i+5000] for i in range(0, len(cleaned_text), 5000)]

    def all_collections(self) -> List[str]:
        """Get list of all available collections.
        
        Returns:
            List[str]: List of collection names
        """
        return self.list_collections()

# Create global instance
vector_store = QdrantVectorStore(app_context)
