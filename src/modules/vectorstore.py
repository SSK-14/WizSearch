import streamlit as st
from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding, TextEmbedding

qdrant_client = QdrantClient(":memory:")
embedding_model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5", 
    providers=["CPUExecutionProvider"]
)
sparse_embedding_model = SparseTextEmbedding(
    model_name="Qdrant/bm42-all-minilm-l6-v2-attentions",
    providers=["CPUExecutionProvider"]
)

def create_collection(collection):
    qdrant_client.create_collection(
        collection,
        vectors_config={
            "text-dense": models.VectorParams(
                size=384,
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "text-sparse": models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            )
        }
    )


def create_collection_and_insert(documents):
    collection = st.session_state.collection_name
    create_collection(collection)

    point_id = 1
    for doc in documents:
        text = doc.page_content
        sparse_embedding = list(sparse_embedding_model.query_embed(text))[0]
        dense_embedding = list(embedding_model.query_embed(text))[0]
        qdrant_client.upsert(
            collection_name=collection,
            points=[
                models.PointStruct(
                    id=point_id,
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
        point_id += 1


def search_collection(query, top_k=4):
    sparse_embedding = list(sparse_embedding_model.query_embed(query))[0]
    dense_embedding = list(embedding_model.query_embed(query))[0]
    search_results = qdrant_client.query_points(
        collection_name=st.session_state.collection_name,
        prefetch=[
            models.Prefetch(query=sparse_embedding.as_object(), using="text-sparse", limit=top_k),
            models.Prefetch(query=dense_embedding.tolist(), using="text-dense", limit=top_k),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF), 
        limit=top_k,
    )
    return [{"text": item.payload.get("text"), "metadata": item.payload.get("metadata")}  for item in search_results.points]

