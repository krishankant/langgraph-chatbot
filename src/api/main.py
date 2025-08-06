import os
import logging
import uuid
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles
from src.agents.chat_agent import ChatAgent
from src.agents.document_agent import DocumentAgent
from src.utils.document_processor import DocumentProcessor
from src.utils.memory_manager import memory_store
from src.api.models import ChatRequest, ChatResponse, FileUploadResponse, SessionInfo
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LangGraph Chatbot API",
    description="Intelligent chatbot with search and document processing capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global components
document_processor = DocumentProcessor()
document_agent = DocumentAgent()

# Ensure upload directory exists
os.makedirs(settings.upload_path, exist_ok=True)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint."""
    try:
        # Get or create chat agent for session
        chat_agent = ChatAgent(request.session_id)
        # Process the query
        result = chat_agent.chat(request.query)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process document files."""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.csv', '.xlsx'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )

        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(settings.upload_path, filename)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Process file
        documents = document_processor.process_file(file_path)

        # Add to vector store
        result = document_agent.add_documents(documents)
        
        if result["success"]:
            return FileUploadResponse(
                success=True,
                message=f"Successfully processed {file.filename}",
                filename=file.filename,
                chunks_created=len(documents)
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions", response_model=List[SessionInfo])
async def get_sessions():
    """Get list of active sessions."""
    try:
        active_sessions = memory_store.get_active_sessions()
        session_info = []
        for session_id in active_sessions:
            memory_manager = memory_store.get_session_memory(session_id)
            summary = memory_manager.get_session_summary()
            session_info.append(SessionInfo(
                session_id=summary["session_id"],
                message_count=summary["message_count"],
                last_activity=summary["last_activity"]
            ))
        return session_info
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear specific session memory."""
    try:
        memory_store.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/info")
async def get_documents_info():
    """Get information about stored documents."""
    try:
        info = document_agent.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Error getting document info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LangGraph Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)