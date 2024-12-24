import os, yaml
from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding
from litellm import embedding

config_path = "config.yaml"
with open(config_path, "r") as file:
    CONFIG = yaml.safe_load(file)

DIMENSIONS = CONFIG.get("embeddings_model", {}).get("litellm_params", {}).get("dimensions")
DENSE_EMBEDDING_MODEL = CONFIG.get("embeddings_model", {}).get("litellm_params", {}).get("model")

if not DIMENSIONS or not DENSE_EMBEDDING_MODEL:
    raise ValueError("Dimensions or dense embedding model not found in config.yaml")
    
qdrant_url = os.environ.get("QDRANT_URL") or None
qdrant_api_key = os.environ.get("QDRANT_API_KEY") or None

if qdrant_url:
    if qdrant_api_key:
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
    else:
        if "http" in qdrant_url:
            qdrant_client = QdrantClient(url=qdrant_url)
        else:
            qdrant_client = QdrantClient(path=qdrant_url)
else:
    qdrant_client = QdrantClient(":memory:")

qdrant_client_memory = QdrantClient(":memory:")

def create_dense_embeddings(text):
    response = embedding(
        model=DENSE_EMBEDDING_MODEL,
        input=[text],
    )
    return response.data[0]["embedding"]

sparse_embedding_model = SparseTextEmbedding(
    model_name="Qdrant/bm25",
    providers=["CPUExecutionProvider"]
)

def create_collection(client, collection):
    client.create_collection(
        collection,
        vectors_config={
            "text-dense": models.VectorParams(
                size=DIMENSIONS,
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "text-sparse": models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            )
        }
    )

def create_collection_and_insert(collection_name, documents, is_memory=False):
    if is_memory:
        client = qdrant_client_memory
    else:
        client = qdrant_client
    create_collection(client, collection_name)
    point_id = 1
    for doc in documents:
        text = doc.page_content
        dense_embedding = create_dense_embeddings(text)
        sparse_embedding = list(sparse_embedding_model.query_embed(text))[0]
        client.upsert(
            collection_name=collection_name,
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

def search_collection(collection_name, query, top_k=4, is_memory=False):
    if is_memory:
        client = qdrant_client_memory
    else:
        client = qdrant_client

    dense_embedding = create_dense_embeddings(query)
    sparse_embedding = list(sparse_embedding_model.query_embed(query))[0]
    search_results = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(query=sparse_embedding.as_object(), using="text-sparse", limit=top_k),
            models.Prefetch(query=dense_embedding, using="text-dense", limit=top_k),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF), 
        limit=top_k,
    )

    return [{"text": item.payload.get("text"), "metadata": item.payload.get("metadata")}  for item in search_results.points]

def all_collections():
    collections_tuple = qdrant_client.get_collections()
    return [collection.name for collection in collections_tuple.collections]

def collection_info(collection_name):
    details = qdrant_client.get_collection(collection_name=collection_name)
    return details

def delete_collection(collection_name):
    qdrant_client.delete_collection(collection_name=collection_name)

def all_points(collection_name, is_memory=False):
    if is_memory:
        client = qdrant_client_memory
    else:
        client = qdrant_client

    result = client.count(collection_name=collection_name)
    records = client.scroll(
        collection_name=collection_name,
        limit=result.count,
        with_payload=True,
    )
    joined_text = " ".join(record.payload['text'] for record in records[0])
    cleaned_text = joined_text.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    texts = [cleaned_text[i:i+5000] for i in range(0, len(cleaned_text), 5000)]
    return texts
