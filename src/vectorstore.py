import streamlit as st
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from qdrant_client.models import VectorParams, Distance, PointStruct

qdrant_client = QdrantClient(":memory:")
embedding_model = TextEmbedding("snowflake/snowflake-arctic-embed-s")

def create_collection_and_insert(documents):
    collection = st.session_state.collection_name
    texts = [doc.page_content for doc in documents]
    metadata = [doc.metadata for doc in documents]
    embeddings = embedding_model.embed(texts)
    points = [
        PointStruct(
            id=idx,
            vector=embedding,
            payload={"text": text, "metadata": metadata},
        )
        for idx, (embedding, text, metadata) in enumerate(zip(embeddings, texts, metadata))
    ]
    qdrant_client.create_collection(
        collection,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )
    qdrant_client.upsert(collection, points)


def search_collection(query, top_k=4):
    query_embedding = next(embedding_model.query_embed(query))
    search_results = qdrant_client.search(
        collection_name=st.session_state.collection_name,
        query_vector=query_embedding,
        limit=top_k,
    )
    return [{"text": item.payload.get("text"), "metadata": item.payload.get("metadata")}  for item in search_results]

