import os
import hashlib
import glob
from pathlib import Path
from bs4 import BeautifulSoup
import pypdf
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import sys
# Ensure app module can be found when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            ext = page.extract_text()
            if ext:
                text += ext + "\n"
    return text

def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        return soup.get_text(separator='\n')

def extract_text_from_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_text_from_file(file_path):
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.html', '.htm']:
        return extract_text_from_html(file_path)
    elif ext == '.md':
        return extract_text_from_md(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

def chunk_text(text, chunk_size, chunk_overlap):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - chunk_overlap
    return chunks

def get_chunk_hash(chunk_text):
    return hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()

def ingest_corpus(corpus_dir: str):
    print(f"Loading embedding model: {settings.embedding_model}...")
    embedder = SentenceTransformer(settings.embedding_model)
    
    print(f"Connecting to ChromaDB at {settings.chroma_db_dir}...")
    client = chromadb.PersistentClient(path=settings.chroma_db_dir)
    collection = client.get_or_create_collection(name="rag_corpus")
    
    files = []
    for ext in ['pdf', 'html', 'md', 'txt']:
        files.extend(glob.glob(f"{corpus_dir}/**/*.{ext}", recursive=True))
    
    print(f"Found {len(files)} files to ingest.")
    if not files:
        print("Please place files in the corpus directory to ingest.")
        return
        
    new_chunks = 0
    for file_path in files:
        try:
            text = get_text_from_file(file_path)
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                chunk_id = get_chunk_hash(chunk)
                
                # Check if exists (idempotent logic)
                res = collection.get(ids=[chunk_id])
                if res and res.get('ids') and len(res['ids']) > 0:
                    continue # already ingested
                
                # embed and store
                embedding = embedder.encode(chunk).tolist()
                metadata = {
                    "source": os.path.basename(file_path),
                    "type": Path(file_path).suffix.lower().replace(".", ""),
                    "chunk_index": i
                }
                
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    ids=[chunk_id]
                )
                new_chunks += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print(f"Ingestion complete. Added {new_chunks} new chunks.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus"), help="Directory containing documents")
    args = parser.parse_args()
    
    # Create dir if not exists
    os.makedirs(args.dir, exist_ok=True)
    ingest_corpus(args.dir)
