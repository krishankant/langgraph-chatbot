import os
import logging
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from src.config.settings import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
        self.vector_store = None
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store."""
        try:
            os.makedirs(settings.vector_db_path, exist_ok=True)
            self.vector_store = Chroma(
                persist_directory=settings.vector_db_path,
                embedding_function=self.embeddings,
                collection_name="documents"
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store."""
        try:
            ids = self.vector_store.add_documents(documents)
            self.vector_store.persist()
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search in vector store."""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents for query")
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return []

    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Perform similarity search with relevance scores."""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} documents with scores")
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search with scores: {str(e)}")
            return []

    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.vector_store.delete_collection()
            logger.info("Vector store collection deleted")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        try:
            collection = self.vector_store._collection
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}