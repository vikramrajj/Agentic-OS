from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    host: str = Field(default="127.0.0.1", description="Host to bind FastAPI server")
    port: int = Field(default=8000, description="Port to bind FastAPI server")
    debug: bool = Field(default=False, description="Debug mode")

    # LLM & Embedding Settings
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    ollama_model: str = Field(default="llama3.2", description="Default Ollama model")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")

    # Optional Cloud LLM Keys (if user wishes to use Gemini / OpenAI)
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")

    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    knowledge_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "knowledge")
    storage_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data")

    # RAG Settings
    top_k_retrieval: int = Field(default=4, description="Number of documents to retrieve")
    min_similarity_score: float = Field(default=0.25, description="Minimum similarity threshold")

    # Tool Execution Safety
    allow_system_inspection: bool = Field(default=True, description="Allow read-only Linux diagnostics")
    tool_timeout_seconds: int = Field(default=10, description="Timeout for read-only CLI tool runs")


settings = Settings()
