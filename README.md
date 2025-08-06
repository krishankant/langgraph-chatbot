# langgraph-chatbot
🤖 LangGraph Intelligent Chatbot

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package%20manager-ff69b4.svg)](https://github.com/astral-sh/uv)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.3-green.svg)](https://python.langchain.com/docs/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47.1-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/langchain-ai/langgraph/main/docs/static/img/langgraph_cloud_architecture.png" alt="LangGraph Architecture" width="600"/>
</p>

> **A comprehensive AI chatbot solution built with LangGraph, featuring internet search capabilities, document processing, and intelligent conversation management. Built with modern Python tooling using uv package manager.**

## 🌟 Features

- 🔄 **LangGraph Workflow**: Advanced conversation flow with state management
- 🌐 **Internet Search**: Real-time web search using Tavily API
- 📄 **Document Processing**: Support for PDF, DOCX, TXT, CSV, and XLSX files
- 🧠 **Vector Database**: Intelligent document retrieval with ChromaDB
- 💾 **Memory Management**: Persistent conversation history
- 🚀 **FastAPI Backend**: RESTful API with automatic documentation
- 🎨 **Streamlit Frontend**: User-friendly web interface
- 🔧 **Error Handling**: Robust error management and fallback mechanisms
- ⚡ **Modern Tooling**: Built with uv for fast dependency management

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **uv package manager** ([Installation Guide](https://github.com/astral-sh/uv#installation))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Tavily API Key** ([Get one here](https://app.tavily.com/))

### 1. Install uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/krishankant/langgraph-chatbot.git
cd langgraph-chatbot

# Install dependencies using uv
uv sync

# Copy environment template (create your own .env)
cp .env .env.local
# Edit .env.local with your API keys
```

### 3. Configure Environment

Edit your `.env` or `.env.local` file:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional Configuration
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=1000
VECTOR_DB_PATH=./data/vector_db
UPLOAD_PATH=./data/uploads
```

### 4. Run the Application

```bash
# Create necessary directories
mkdir -p data/{uploads,vector_db}

# Start the API server
uv run uvicorn src.api.main:app --reload --port 8000

# In a new terminal, start the Streamlit frontend
uv run streamlit run frontend/streamlit_app.py --server.port 8501
```

🎉 **Access your chatbot at**: http://localhost:8501
📚 **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
langgraph-chatbot/
├── src/
│   ├── __init__.py
│   ├── agents/              # AI agents (chat, search, document)
│   │   ├── __init__.py
│   │   ├── chat_agent.py    # Main LangGraph workflow
│   │   ├── search_agent.py  # Internet search functionality
│   │   └── document_agent.py # Document processing and querying
│   ├── utils/               # Utility modules
│   │   ├── __init__.py
│   │   ├── document_processor.py # File processing logic
│   │   ├── vector_store.py      # ChromaDB management
│   │   └── memory_manager.py    # Conversation memory
│   ├── api/                 # FastAPI backend
│   │   ├── __init__.py
│   │   ├── main.py         # API endpoints
│   │   └── models.py       # Pydantic models
│   └── config/
│       ├── __init__.py
│       └── settings.py     # Configuration management
├── frontend/               # Streamlit web interface
│   ├── __init__.py
│   ├── streamlit_app.py   # Main web application
│   └── components/        # UI components
│       └── __init__.py
├── data/
│   ├── uploads/           # Uploaded files storage
│   └── vector_db/         # ChromaDB database
├── mock_uploads/          # Sample files for testing
├── tests/                 # Unit tests
│   └── __init__.py
├── main.py               # Entry point
├── pyproject.toml        # uv project configuration
├── uv.lock              # Locked dependencies
├── requirements.txt     # Fallback requirements
├── .python-version      # Python version specification (3.11)
├── .env                 # Environment variables
└── .gitignore          # Git ignore rules
```

## ⚙️ Installation & Configuration

### Detailed Installation with uv

1. **System Requirements**
   
   ```bash
   # Verify Python version
   python --version  # Should be 3.11+
   
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Project Setup**
   
   ```bash
   # Clone the repository
   git clone https://github.com/krishankant/langgraph-chatbot.git
   cd langgraph-chatbot
   
   # Create virtual environment and install dependencies
   uv sync
   
   # Activate the virtual environment (optional, uv run handles this)
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```
3. **Verify Installation**
   
   ```bash
   # Check installed packages
   uv pip list
   
   # Run basic health check
   uv run python -c "import langgraph; print('LangGraph installed successfully')"
   ```

### Configuration Options

| Setting        | Description                   | Default              | Environment Variable |
| -------------- | ----------------------------- | -------------------- | -------------------- |
| OpenAI API Key | Required for AI functionality | -                    | `OPENAI_API_KEY`   |
| Tavily API Key | Required for internet search  | -                    | `TAVILY_API_KEY`   |
| LLM Model      | OpenAI model to use           | `gpt-3.5-turbo`    | `LLM_MODEL`        |
| Temperature    | Response creativity (0.0-1.0) | `0.7`              | `TEMPERATURE`      |
| Max Tokens     | Maximum response length       | `1000`             | `MAX_TOKENS`       |
| Vector DB Path | ChromaDB storage location     | `./data/vector_db` | `VECTOR_DB_PATH`   |
| Upload Path    | File upload directory         | `./data/uploads`   | `UPLOAD_PATH`      |

### Environment Variables

Your `.env` file should contain:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# Optional Configuration
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
TEMPERATURE=0.7
MAX_TOKENS=1000

# Paths
VECTOR_DB_PATH=./data/vector_db
UPLOAD_PATH=./data/uploads

# Search Configuration
MAX_SEARCH_RESULTS=5
SEARCH_TIMEOUT=10

# Memory Configuration
MEMORY_WINDOW=10
MAX_MEMORY_TOKENS=4000
```

## 📖 Usage Examples

### Command Line Usage

```bash
# Run the main application
uv run python main.py

# Start individual components
uv run uvicorn src.api.main:app --reload
uv run streamlit run frontend/streamlit_app.py

# Run with environment variables
uv run --env-file .env.local python main.py
```

### Web Interface Usage

1. **Basic Chat**
   
   - Navigate to http://localhost:8501
   - Type your question in the chat input
   - Get AI-powered responses
2. **Internet Search**
   
   ```
   User: "What are the latest developments in AI?"
   Bot: "Based on recent search results, here are the latest AI developments..."
   ```
3. **Document Upload**
   
   - Use the file uploader in the sidebar
   - Upload PDF, DOCX, TXT, CSV, or XLSX files
   - Ask questions about the uploaded content

### API Usage Examples

#### Using uv to test API endpoints

```bash
# Test health endpoint
uv run python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
"

# Test chat endpoint
uv run python -c "
import requests
response = requests.post(
    'http://localhost:8000/chat',
    json={'query': 'Hello!', 'session_id': 'test'}
)
print(response.json())
"
```

#### Chat Endpoint

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "query": "What is machine learning?",
        "session_id": "user123"
    }
)
print(response.json())
```

## 🔌 API Documentation

### Endpoints Overview

| Method     | Endpoint                   | Description                  |
| ---------- | -------------------------- | ---------------------------- |
| `GET`    | `/health`                | Health check endpoint        |
| `POST`   | `/chat`                  | Send chat message            |
| `POST`   | `/upload`                | Upload and process document  |
| `GET`    | `/sessions`              | List active chat sessions    |
| `DELETE` | `/sessions/{session_id}` | Clear specific session       |
| `GET`    | `/documents/info`        | Get document collection info |

### Sample Request/Response

#### Chat Request

```json
{
  "query": "What is the capital of France?",
  "session_id": "user123"
}
```

#### Chat Response

```json
{
  "success": true,
  "response": "The capital of France is Paris, a vibrant city known for...",
  "sources": [
    {
      "title": "Paris - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Paris",
      "snippet": "Paris is the capital and most populous city of France..."
    }
  ],
  "session_id": "user123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Interactive Documentation

Once the API is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Run Tests with uv

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_agents.py -v

# Run tests with output
uv run pytest -s tests/
```

### Test Categories

```bash
# Test specific modules
uv run pytest tests/test_agents.py      # Agent functionality
uv run pytest tests/test_api.py         # API endpoints
uv run pytest tests/test_utils.py       # Utility functions

# Integration tests
uv run pytest tests/ -k "integration"
```

### Manual API Testing

```bash
# Health check
uv run python -c "
import requests
print(requests.get('http://localhost:8000/health').json())
"

# Test document processing
uv run python -c "
import requests
with open('mock_uploads/sample.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
    print(response.json())
"
```

## 🚨 Troubleshooting

### Common Issues

#### uv Installation Issues

```bash
# If uv command not found
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.bashrc  # or ~/.zshrc

# Alternative installation
pip install uv
```

#### Dependency Issues

```bash
# Clear uv cache and reinstall
uv cache clean
rm -rf .venv
uv sync

# Force reinstall specific package
uv add --force langchain
```

#### Python Version Issues

```bash
# Check current Python version
python --version

# Use specific Python version with uv
uv python install 3.11
uv sync --python 3.11
```

#### API Connection Issues

```bash
# Check if ports are available
lsof -i :8000  # API port
lsof -i :8501  # Streamlit port

# Kill processes if needed
kill -9 $(lsof -t -i:8000)
```

#### Environment Variable Issues

```bash
# Debug environment loading
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OpenAI Key:', os.getenv('OPENAI_API_KEY', 'Not found'))
print('Tavily Key:', os.getenv('TAVILY_API_KEY', 'Not found'))
"
```

### Performance Optimization

1. **Use uv's parallel installation**
   
   ```bash
   uv sync --no-cache  # Skip cache for faster CI builds
   ```
2. **Environment-specific installations**
   
   ```bash
   uv sync --dev      # Include development dependencies
   uv sync --no-dev   # Production only
   ```

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-fork/langgraph-chatbot.git
cd langgraph-chatbot

# Setup development environment
uv sync --dev

# Install pre-commit hooks (if using)
uv run pre-commit install
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add requests

# Add development dependency
uv add --dev pytest

# Add specific version
uv add "langchain>=0.1.0"

# Update dependencies
uv sync --upgrade
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/

# Run all checks
uv run pytest && uv run ruff check && uv run mypy src/
```

### Pull Request Process

1. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
2. **Install Dependencies**: `uv sync --dev`
3. **Make Changes**: Implement your feature
4. **Add Tests**: `uv run pytest tests/test_new_feature.py`
5. **Update Dependencies**: `uv sync` (updates uv.lock)
6. **Submit PR**: Create pull request with detailed description

## 🛠 Development Commands

### Useful uv Commands

```bash
# Project information
uv info

# List installed packages
uv pip list

# Update all dependencies
uv sync --upgrade

# Add package temporarily
uv run --with requests python script.py

# Run scripts with environment
uv run --env-file .env.local python main.py

# Build distribution
uv build

# Publish to PyPI (if applicable)
uv publish
```

### Package Management

```bash
# Add new dependencies to pyproject.toml
uv add fastapi uvicorn

# Remove dependency
uv remove package-name

# Update specific package
uv add package-name --upgrade

# Install from requirements.txt
uv add -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation

- **uv Documentation**: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
- **LangGraph Docs**: [https://python.langchain.com/docs/langgraph](https://python.langchain.com/docs/langgraph)
- **FastAPI Docs**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Streamlit Docs**: [https://docs.streamlit.io/](https://docs.streamlit.io/)

### Getting Help

1. **Check Documentation**: Review this README and inline documentation
2. **Search Issues**: Look for similar problems in [GitHub Issues](https://github.com/krishankant/langgraph-chatbot/issues)
3. **Create Issue**: If you can't find a solution, create a detailed issue
4. **Community Support**: Join discussions in the repository

### Quick Debug Commands

```bash
# System information
uv --version
python --version
uv pip list | grep -E "(langchain|langgraph|fastapi)"

# Environment check
uv run python -c "
import sys
print(f'Python: {sys.version}')
import langgraph
print(f'LangGraph: {langgraph.__version__}')
"

# Health check
uv run python -c "
try:
    from src.config.settings import settings
    print('✅ Configuration loaded successfully')
    print(f'✅ OpenAI key: {\"*\" * 20 if settings.openai_api_key else \"❌ Missing\"}')
    print(f'✅ Tavily key: {\"*\" * 20 if settings.tavily_api_key else \"❌ Missing\"}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

---

<p align="center">
  <strong>Built with ❤️ using LangGraph, FastAPI, Streamlit, and uv</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-documentation">API</a> •
  <a href="#-testing">Testing</a> •
  <a href="#-contributing">Contributing</a>
</p>
