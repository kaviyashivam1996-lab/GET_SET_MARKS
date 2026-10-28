# ingestion package — PDF extraction and chunking pipeline
# Phase 1: extraction + chunking only (no embeddings, no DB writes)
from .models import PageContent, Chunk

try:
    from .pipeline import run_pipeline
    __all__ = ["PageContent", "Chunk", "run_pipeline"]
except (ImportError, Exception):
    __all__ = ["PageContent", "Chunk"]
