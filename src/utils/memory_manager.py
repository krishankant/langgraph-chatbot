import logging
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from src.config.settings import settings

logger = logging.getLogger(__name__)

class ConversationMemoryManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = ConversationBufferWindowMemory(
            k=settings.memory_window,
            return_messages=True,
            memory_key="chat_history"
        )
        self._message_history: List[Dict[str, Any]] = []

    def add_user_message(self, message: str):
        """Add user message to memory."""
        try:
            self.memory.chat_memory.add_user_message(message)
            self._message_history.append({
                "type": "human",
                "content": message,
                "timestamp": self._get_timestamp()
            })
            logger.debug(f"Added user message to memory for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error adding user message to memory: {str(e)}")

    def add_ai_message(self, message: str):
        """Add AI response to memory."""
        try:
            self.memory.chat_memory.add_ai_message(message)
            self._message_history.append({
                "type": "ai",
                "content": message,
                "timestamp": self._get_timestamp()
            })
            logger.debug(f"Added AI message to memory for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error adding AI message to memory: {str(e)}")

    def get_conversation_history(self) -> List[BaseMessage]:
        """Get conversation history as LangChain messages."""
        try:
            return self.memory.chat_memory.messages
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []

    def get_formatted_history(self) -> str:
        """Get formatted conversation history as string."""
        try:
            messages = self.get_conversation_history()
            formatted_history = ""
            for message in messages:
                if isinstance(message, HumanMessage):
                    formatted_history += f"Human: {message.content}\n"
                elif isinstance(message, AIMessage):
                    formatted_history += f"Assistant: {message.content}\n"
            return formatted_history
        except Exception as e:
            logger.error(f"Error formatting conversation history: {str(e)}")
            return ""

    def clear_memory(self):
        """Clear conversation memory."""
        try:
            self.memory.clear()
            self._message_history = []
            logger.info(f"Cleared memory for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")

    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for prompt formatting."""
        try:
            return self.memory.load_memory_variables({})
        except Exception as e:
            logger.error(f"Error getting memory variables: {str(e)}")
            return {"chat_history": []}

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        return {
            "session_id": self.session_id,
            "message_count": len(self._message_history),
            "last_activity": self._message_history[-1]["timestamp"] if self._message_history else None
        }

class MemoryStore:
    """Global memory store for managing multiple sessions."""
    def __init__(self):
        self._sessions: Dict[str, ConversationMemoryManager] = {}

    def get_session_memory(self, session_id: str) -> ConversationMemoryManager:
        """Get or create memory manager for session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationMemoryManager(session_id)
        return self._sessions[session_id]

    def clear_session(self, session_id: str):
        """Clear specific session memory."""
        if session_id in self._sessions:
            self._sessions[session_id].clear_memory()
            del self._sessions[session_id]

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self._sessions.keys())

# Global memory store instance
memory_store = MemoryStore()