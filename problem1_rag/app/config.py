import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    chroma_db_dir: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 500))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 50))

settings = Settings()
