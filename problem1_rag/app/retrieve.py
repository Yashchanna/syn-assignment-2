import os
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

client = OpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# Load embedder lazily to avoid heavy loading on import
embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        embedder = SentenceTransformer(settings.embedding_model)
    return embedder

def get_chroma_collection():
    chroma_client = chromadb.PersistentClient(path=settings.chroma_db_dir)
    return chroma_client.get_or_create_collection(name="rag_corpus")

def retrieve_chunks(query: str, k: int = 5):
    collection = get_chroma_collection()
    emb = get_embedder()
    query_embedding = emb.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    
    if not results['documents'] or not results['documents'][0]:
        return []
    
    retrieved = []
    for doc, meta, doc_id in zip(results['documents'][0], results['metadatas'][0], results['ids'][0]):
        retrieved.append({
            "id": doc_id,
            "text": doc,
            "metadata": meta
        })
    return retrieved

def generate_answer(query: str, chunks: list):
    if not chunks:
        return {
            "answer": "I could not find any relevant context to answer your question.",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
    context_str = ""
    for i, chunk in enumerate(chunks):
        source = chunk['metadata'].get('source', 'Unknown')
        context_str += f"\n[Document {i+1} | Source: {source}]: {chunk['text']}"
        
    system_prompt = (
        "You are a helpful answering assistant. You will be provided with context from various documents. "
        "Answer the user's question ONLY using the provided context. "
        "You must cite the documents you used in your answer by referencing them like [Document 1]. "
        "If the context does not contain the answer, reply with 'I cannot answer this based on the provided context.' "
        "Do not hallucinate."
    )
    
    user_prompt = f"Context:{context_str}\n\nQuestion: {query}"
    
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )
    
    return {
        "answer": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }
