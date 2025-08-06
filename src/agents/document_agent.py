import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from src.utils.vector_store import VectorStoreManager
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DocumentAgent:
    def __init__(self):
        self.vector_store_manager = VectorStoreManager()
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            temperature=settings.temperature
        )
        self.document_prompt = PromptTemplate(
            input_variables=["query", "context", "chat_history"],
            template=""" You are a helpful assistant that answers questions based on uploaded documents and conversation history.
            Chat History: {chat_history}
            Context from Documents: {context}
            User Question: {query}
            Please provide a comprehensive answer based on the document context. If the information is not available in the documents, clearly state that. Always cite which document or section your information comes from when possible.
            Answer: """
        )

    def query_documents(self, query: str, chat_history: str = "") -> Dict[str, Any]:
        """Query documents using vector similarity search."""
        try:
            logger.info(f"Querying documents for: {query}")
            # Perform similarity search
            relevant_docs = self.vector_store_manager.similarity_search_with_score(
                query, k=5
            )
            if not relevant_docs:
                return {
                    "success": True,
                    "response": "I don't have any relevant documents to answer your question. Please upload some documents first.",
                    "sources": [],
                    "documents_found": False
                }

            # Filter documents by relevance score (threshold: 0.8)
            filtered_docs = [
                (doc, score) for doc, score in relevant_docs if score < 0.8
                # Lower score means higher similarity in some implementations
            ]
            if not filtered_docs:
                return {
                    "success": True,
                    "response": "I couldn't find sufficiently relevant information in the uploaded documents to answer your question.",
                    "sources": [],
                    "documents_found": True
                }

            # Prepare context from documents
            context = self._prepare_context(filtered_docs)
            # Generate response
            prompt = self.document_prompt.format(
                query=query,
                context=context,
                chat_history=chat_history
            )
            response = self.llm.invoke(prompt)
            # Prepare source information
            sources = self._prepare_sources(filtered_docs)
            logger.info(f"Generated document-based response for: {query}")
            return {
                "success": True,
                "response": response.content.strip(),
                "sources": sources,
                "documents_found": True
            }
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            return {
                "success": False,
                "response": f"Error accessing documents: {str(e)}",
                "sources": [],
                "documents_found": False
            }

    def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """Add documents to the vector store."""
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            document_ids = self.vector_store_manager.add_documents(documents)
            return {
                "success": True,
                "message": f"Successfully added {len(documents)} document chunks",
                "document_ids": document_ids
            }
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return {
                "success": False,
                "message": f"Error adding documents: {str(e)}",
                "document_ids": []
            }

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about stored documents."""
        try:
            info = self.vector_store_manager.get_collection_info()
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {
                "success": False,
                "info": {},
                "error": str(e)
            }

    def _prepare_context(self, docs_with_scores: List[tuple]) -> str:
        """Prepare context string from relevant documents."""
        context = ""
        for i, (doc, score) in enumerate(docs_with_scores, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk_id = doc.metadata.get("chunk_id", 0)
            context += f"Document {i} (Source: {source}, Chunk: {chunk_id}):\n"
            context += f"{doc.page_content}\n\n"
        return context

    def _prepare_sources(self, docs_with_scores: List[tuple]) -> List[Dict[str, Any]]:
        """Prepare source information for response."""
        sources = []
        for doc, score in docs_with_scores:
            source_info = {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "file_type": doc.metadata.get("file_type", "unknown"),
                "relevance_score": float(score),
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            sources.append(source_info)
        return sources

    def has_documents(self) -> bool:
        """Check if there are any documents in the vector store."""
        try:
            info = self.vector_store_manager.get_collection_info()
            return info.get("count", 0) > 0
        except Exception:
            return False