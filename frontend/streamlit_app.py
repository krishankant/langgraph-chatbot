# frontend/streamlit_app.py
import streamlit as st
import requests
from typing import Dict, Any, List

# --- Page and API Configuration ---
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# The API base URL should point to where your FastAPI backend is running.
API_BASE_URL = "http://127.0.0.1:8000"

# --- API Communication Functions ---

def send_chat_message(query: str, session_id: str) -> Dict[str, Any]:
    """Sends a chat message to the backend API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"query": query, "session_id": session_id},
            timeout=45  # Increased timeout for potentially long-running generation
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with API: {e}")
        # Return a dictionary with a standard error format
        return {"success": False, "response": "Failed to connect to the backend service."}

def upload_file(file) -> Dict[str, Any]:
    """Uploads a file to the backend API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            timeout=120  # Generous timeout for large files and processing
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading file: {e}")
        return {"success": False, "message": "File upload failed due to a connection error."}

def get_document_info() -> Dict[str, Any]:
    """Gets document collection information from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/info")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        # Don't show an error for this, just return a non-success state
        return {"success": False}

# --- UI Helper Functions ---

def display_message(message: Dict[str, Any]):
    """Displays a single chat message, including content and sources."""
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Display sources if they exist in the message
        if "sources" in message and message["sources"]:
            with st.expander("📚 Show Sources", expanded=False):
                for i, source in enumerate(message["sources"], 1):
                    # Check if the source is from an internet search (has a URL)
                    if source.get("url"):
                        st.markdown(f"**{i}. {source.get('title', 'Web Source')}**")
                        st.markdown(f"🔗 [{source['url']}]({source['url']})")
                        st.markdown(f"📝 *{source.get('snippet', 'No preview available')}*")
                    # Otherwise, assume it's a document source
                    else:
                        st.markdown(f"**{i}. Document Source**")
                        st.markdown(f"📄 File: `{source.get('source', 'Unknown')}`")
                        st.markdown(f"📋 *Preview: {source.get('preview', 'No preview available')}*")
                    st.divider()

def initialize_session_state():
    """Initializes all necessary session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = "default_session"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

# --- Main Application UI ---

def main():
    """Renders the main Streamlit application page."""
    initialize_session_state()

    st.title("🤖 LangGraph Intelligent Chatbot")
    st.markdown("An AI assistant that can search the internet and analyze your documents!")

    # --- Sidebar for Controls and Uploads ---
    with st.sidebar:
        st.header("⚙️ Controls & Settings")

        # --- Session Management ---
        st.subheader("Session Management")
        session_id_input = st.text_input(
            "Current Session ID",
            value=st.session_state.session_id,
            help="Change the ID to start a new, separate conversation."
        )
        
        # If the user changes the session ID, reset the chat
        if session_id_input != st.session_state.session_id:
            st.session_state.session_id = session_id_input
            st.session_state.messages = []
            st.session_state.uploaded_files = [] # Reset files as they are tied to a vector store
            st.rerun()

        if st.button("🗑️ Clear Current Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()

        # --- Document Handling ---
        st.subheader("📁 Document Upload")
        uploaded_file = st.file_uploader(
            "Upload files for analysis",
            type=['pdf', 'docx', 'txt', 'csv', 'xlsx']
        )
        
        if uploaded_file:
            if st.button(f"📤 Process `{uploaded_file.name}`"):
                with st.spinner("Processing file... This may take a moment."):
                    result = upload_file(uploaded_file)
                    if result.get("success"):
                        st.success(f"✅ {result.get('message', 'File processed.')}")
                        st.info(f"Created {result.get('chunks_created', 0)} text chunks.")
                        # Add to our list of uploaded files for this session
                        if uploaded_file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(uploaded_file.name)
                    else:
                        st.error(f"❌ {result.get('message', 'An unknown error occurred.')}")

        # --- Document Status ---
        st.subheader("🗂️ Document Status")
        if st.button("📊 Refresh Document Info"):
            with st.spinner("Checking document collection..."):
                doc_info = get_document_info()
                if doc_info.get("success"):
                    info = doc_info.get("info", {})
                    st.write(f"**Total Chunks:** {info.get('count', 0)}")
                    st.write(f"**Collection Name:** `{info.get('name', 'N/A')}`")
                else:
                    st.warning("Could not retrieve document info from the backend.")

        if st.session_state.uploaded_files:
            with st.expander("View Uploaded Files", expanded=False):
                for file_name in st.session_state.uploaded_files:
                    st.write(f"• {file_name}")

    # --- Main Chat Interface ---
    st.subheader("💬 Chat")

    # Display all past messages from the session state
    for message in st.session_state.messages:
        display_message(message)

    # Handle new user input
    if user_prompt := st.chat_input("Ask me anything..."):
        # Add user's message to the session state and display it
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        display_message({"role": "user", "content": user_prompt})
        
        # Get and display the AI's response
        with st.spinner("Thinking..."):
            ai_response = send_chat_message(user_prompt, st.session_state.session_id)
            if ai_response.get("success"):
                assistant_message = {
                    "role": "assistant",
                    "content": ai_response["response"],
                    "sources": ai_response.get("sources", [])
                }
                # Add the AI's full response to the session state
                st.session_state.messages.append(assistant_message)
                # Rerender the new AI message from the session state
                display_message(assistant_message)
            else:
                st.error(ai_response.get("response", "An unknown error occurred."))


if __name__ == "__main__":
    main()