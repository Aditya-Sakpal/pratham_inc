# Project Structure

```
pratham_inc/
├── backend/                           # FastAPI Backend Application
│   ├── app/                           # Application package
│   │   ├── __init__.py               # Package initializer
│   │   ├── config.py                 # Configuration and settings management
│   │   ├── models/                    # Data models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py            # Pydantic models for request/response
│   │   ├── routers/                   # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── topics.py             # Topic listing and retrieval endpoints
│   │   │   ├── summary.py            # Summary generation endpoints
│   │   │   ├── chat.py               # Chat Q&A endpoints
│   │   │   ├── quiz.py               # Quiz generation endpoints
│   │   │   └── evaluation.py         # Evaluation and OCR endpoints
│   │   └── services/                 # Business logic services
│   │       ├── pinecone_service.py   # Pinecone vector database service
│   │       ├── llm_service.py        # OpenAI LLM service (summaries, chat, quiz, evaluation)
│   │       └── ocr_service.py        # OCR service for image text extraction
│   ├── main.py                        # FastAPI application entry point
│   └── requirements.txt              # Python dependencies
│
├── frontend/                          # React + Vite Frontend Application
│   ├── src/
│   │   ├── App.jsx                    # Main application component (single-page interface)
│   │   ├── App.css                    # Application styles
│   │   ├── main.jsx                   # React entry point
│   │   └── index.css                  # Global styles
│   ├── index.html                     # HTML template
│   ├── package.json                   # Node.js dependencies
│   ├── vite.config.js                 # Vite configuration
│   └── Dockerfile                     # Frontend Dockerfile
│
├── books/                             # PDF textbooks directory
│   ├── class8.pdf                     # Class 8 Science textbook
│   ├── class9.pdf                     # Class 9 Science textbook
│   └── class10.pdf                    # Class 10 Science textbook
│
├── ingestion/                         # PDF Ingestion Pipeline
│   └── ingestion.py                  # Script to ingest PDFs into Pinecone
│
├── scrapper/                          # Web Scraper
│   └── ncert_scraper.py              # Selenium scraper for downloading PDFs
│
├── uploads/                           # Upload directory (created at runtime)
│
├── .env                               # Environment variables (not in repo)
├── .env.example                       # Example environment variables
├── .venv/                             # Python virtual environment
│
├── Dockerfile                         # Backend Dockerfile
├── docker-compose.yml                 # Docker Compose configuration
├── requirements.txt                   # Root-level requirements (for ingestion/scraper)
│
├── README.md                          # Main documentation
├── ENDPOINTS.md                       # API endpoints documentation
└── PROJECT_STRUCTURE.md               # This file
```

## File Descriptions

### Backend Files

- **backend/main.py**: FastAPI application entry point, middleware setup, route registration
- **backend/app/config.py**: Environment variable loading, application settings
- **backend/app/models/schemas.py**: Pydantic models for API request/response validation
- **backend/app/routers/topics.py**: Handles topic listing and retrieval
- **backend/app/routers/summary.py**: Generates topic summaries using LLM
- **backend/app/routers/chat.py**: Handles conversational Q&A with context from Pinecone
- **backend/app/routers/quiz.py**: Generates quizzes and stores them
- **backend/app/routers/evaluation.py**: Handles image upload, OCR, and answer evaluation
- **backend/app/services/pinecone_service.py**: Manages Pinecone vector database operations
- **backend/app/services/llm_service.py**: Handles all OpenAI LLM interactions (summaries, chat, quiz, evaluation)
- **backend/app/services/ocr_service.py**: Extracts text from images using OCR

### Frontend Files

- **frontend/src/App.jsx**: Main React component with single-page interface for all features
- **frontend/src/App.css**: Styling for the application
- **frontend/src/main.jsx**: React application entry point
- **frontend/vite.config.js**: Vite build configuration with API proxy

### Other Files

- **ingestion/ingestion.py**: Pipeline to process PDFs, chunk text, generate embeddings, and upsert to Pinecone
- **scrapper/ncert_scraper.py**: Selenium-based scraper to download NCERT PDFs
- **Dockerfile**: Backend containerization
- **docker-compose.yml**: Multi-container orchestration
- **README.md**: Comprehensive setup and usage documentation
- **ENDPOINTS.md**: API endpoint documentation

## Key Design Decisions

1. **Single-Page Interface**: All features (topic selection, summary, chat, quiz, evaluation) in one React component for simplicity
2. **Service Layer**: Business logic separated into services for maintainability
3. **In-Memory Storage**: Quizzes and evaluations stored in memory (use database for production)
4. **Modular Routers**: Each feature has its own router module
5. **Pydantic Models**: Request/response validation and type safety
6. **CORS Configuration**: Allowed origins configured for frontend-backend communication

