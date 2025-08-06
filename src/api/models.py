from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    success: bool
    response: str
    sources: List[Dict[str, Any]] = []
    session_id: str

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    chunks_created: int = 0

class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    last_activity: Optional[str] = None