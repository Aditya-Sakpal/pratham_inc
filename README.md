# NCERT Science Learning Platform

A full-stack proof-of-concept application for students of classes 8-10 following the NCERT English Science syllabus. The platform provides an interactive learning experience with topic summaries, conversational Q&A, quiz generation, and automated evaluation.

## Features

1. **Topic Selection**: Browse and select topics from NCERT Science syllabus (Classes 8-10)
2. **Summary Generation**: Get concise summaries of selected topics for quick revision
3. **Interactive Chat**: Ask questions about topics and receive contextual answers
4. **Quiz Generation**: Generate assessment quizzes with MCQs, fill-in-the-blanks, and short-answer questions
5. **Image Upload**: Upload photos of handwritten/typed quiz answers
6. **Automated Evaluation**: Receive evaluation with correct answers, feedback, and topics for review

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: React + Vite
- **Vector Database**: Pinecone (with text-embedding-3-small, 512 dimensions)
- **LLM**: OpenAI API (GPT-4o-mini or GPT-4)
- **OCR**: Tesseract OCR

## Project Structure

```
pratham_inc/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── config.py           # Configuration and settings
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── routers/            # API route handlers
│   │   │   ├── topics.py       # Topic listing endpoints
│   │   │   ├── summary.py      # Summary generation
│   │   │   ├── chat.py         # Chat Q&A endpoints
│   │   │   ├── quiz.py         # Quiz generation
│   │   │   └── evaluation.py   # Evaluation endpoints
│   │   └── services/           # Business logic
│   │       ├── pinecone_service.py  # Vector database service
│   │       ├── llm_service.py       # OpenAI LLM service
│   │       └── ocr_service.py        # OCR service
│   ├── main.py                 # FastAPI application entry point
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── App.css             # Application styles
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Global styles
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   └── Dockerfile              # Frontend Dockerfile
├── books/                      # PDF textbooks (downloaded)
├── ingestion/                  # PDF ingestion pipeline
│   └── ingestion.py           # Pinecone ingestion script
├── scrapper/                   # Web scraper
│   └── ncert_scraper.py       # Selenium scraper
├── .env                        # Environment variables (not in repo)
├── .env.example               # Example environment variables
├── Dockerfile                  # Backend Dockerfile
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional)
- Tesseract OCR (for image processing)
- OpenAI API key
- Pinecone API key

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=512

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=prathaminc
PINECONE_NAMESPACE=ncert-science
PINECONE_REGION=us-east-1

# OCR Configuration
OCR_PROVIDER=tesseract

# CORS (for local development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2. Backend Setup

```bash
# Navigate to project root
cd pratham_inc

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install Tesseract OCR
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract

# Run backend
cd ..
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
```

## API Endpoints

### Topics

- `GET /api/topics/` - List all topics (optional `class_level` query param)
- `GET /api/topics/classes` - List available class levels
- `GET /api/topics/{topic_id}` - Get specific topic

### Summary

- `POST /api/summary/` - Generate summary for a topic
  - Request: `{ topic_id, topic_name, class_level }`
  - Response: `{ topic_id, topic_name, summary, key_points }`

### Chat

- `POST /api/chat/` - Send chat message
  - Request: `{ topic_id, topic_name, messages[] }`
  - Response: `{ response, sources[] }`

### Quiz

- `POST /api/quiz/` - Generate quiz
  - Request: `{ topic_id, topic_name, class_level, num_mcqs, num_fill_blank, num_short_answer }`
  - Response: `{ quiz_id, topic_id, topic_name, questions[], total_questions }`
- `GET /api/quiz/{quiz_id}` - Get stored quiz

### Evaluation

- `POST /api/evaluation/upload-image` - Upload image for OCR
  - Request: `FormData with file`
  - Response: `{ file_id, extracted_text, confidence }`
- `POST /api/evaluation/evaluate` - Evaluate quiz answers
  - Request: `{ quiz_id, answers: { question_id: answer } }`
  - Response: `{ quiz_id, total_questions, correct_count, score_percentage, question_results[], topics_to_review[], feedback }`
- `GET /api/evaluation/{evaluation_id}` - Get stored evaluation

## Usage

### 1. Start the Application

1. Start backend: `python -m uvicorn backend.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:5173`

### 2. Using the Application

1. **Select Class**: Choose Class VIII, IX, or X from the dropdown
2. **Select Topic**: Click on a topic from the list
3. **Generate Summary**: Click "Generate Summary" to get a topic overview
4. **Ask Questions**: Type questions in the chat input and send
5. **Generate Quiz**: Click "Generate Quiz" to create assessment questions
6. **Answer Quiz**: Fill in answers manually or upload image of handwritten answers
7. **Submit Quiz**: Click "Submit Quiz" to get evaluation results
8. **Review Results**: View score, feedback, and topics to review

## Environment Variables Reference

| Variable                        | Description                                | Default                    |
| ------------------------------- | ------------------------------------------ | -------------------------- |
| `OPENAI_API_KEY`              | OpenAI API key (required)                  | -                          |
| `PINECONE_API_KEY`            | Pinecone API key (required)                | -                          |
| `PINECONE_INDEX_NAME`         | Pinecone index name                        | `prathaminc`             |
| `PINECONE_NAMESPACE`          | Pinecone namespace                         | `ncert-science`          |
| `PINECONE_REGION`             | Pinecone region                            | `us-east-1`              |
| `OPENAI_MODEL`                | OpenAI model for LLM                       | `gpt-4o-mini`            |
| `OPENAI_EMBEDDING_MODEL`      | Embedding model                            | `text-embedding-3-small` |
| `OPENAI_EMBEDDING_DIMENSIONS` | Embedding dimensions                       | `512`                    |
| `OCR_PROVIDER`                | OCR provider (tesseract/easyocr/paddleocr) | `tesseract`              |
| `CORS_ORIGINS`                | Allowed CORS origins                       | `http://localhost:5173`  |

## Prompt Templates

The application uses the following prompt templates (see `backend/app/services/llm_service.py`):

### Summary Generation

```
You are an expert NCERT Science teacher for {class_level} students.

Generate a comprehensive yet concise summary of the topic "{topic_name}" based on the following context from NCERT Science textbooks.

[Context from Pinecone chunks]

Requirements:
1. Create a clear, structured summary suitable for {class_level} students (200-300 words)
2. Identify 3-5 key points that students should remember
3. Use simple language appropriate for the class level
```

### Chat Q&A

```
You are a helpful NCERT Science tutor. Answer questions about "{topic_name}" based on the following context from NCERT Science textbooks.

[Context from Pinecone chunks]

Guidelines:
- Answer based on the provided context
- Use simple, clear language appropriate for the student's class level
- Provide accurate information from NCERT curriculum
```

### Quiz Generation

```
You are an expert NCERT Science teacher creating an assessment quiz for {class_level} students on the topic "{topic_name}".

[Context from Pinecone chunks]

Generate a quiz with:
1. {num_mcqs} Multiple Choice Questions (MCQs) with 4 options each
2. {num_fill_blank} Fill-in-the-Blank questions
3. {num_short_answer} Short Answer questions (1-2 lines expected)

Ensure questions are based on the provided context and appropriate for {class_level} level.
```

### Answer Evaluation

```
Evaluate the following quiz answers for the topic "{topic_name}".

[Quiz questions and student answers]

For each question:
1. Determine if the answer is correct, partially correct, or incorrect
2. Provide specific feedback on what's wrong or right
3. Suggest topics that need review if answer is incorrect

Be fair but thorough in evaluation. For short answers, accept variations that convey the same meaning.
```

## Development Notes

- The application uses in-memory storage for quizzes and evaluations. For production, use a database (PostgreSQL, MongoDB, etc.)
- OCR processing can be slow for large images. Consider async processing or cloud OCR APIs for production
- Pinecone index must have 512 dimensions matching `text-embedding-3-small` model
- Ensure PDFs are ingested into Pinecone before using the application
- CORS is configured for local development. Update `CORS_ORIGINS` for production

## Troubleshooting

### Backend Issues

- **Import errors**: Ensure virtual environment is activated and dependencies are installed
- **Pinecone connection**: Verify API key and index name in `.env`
- **OCR errors**: Install Tesseract OCR and ensure it's in PATH
- **Port already in use**: Change port in `uvicorn` command or kill existing process

### Frontend Issues

- **API connection errors**: Check `VITE_API_URL` in frontend `.env` or `vite.config.js`
- **CORS errors**: Ensure backend `CORS_ORIGINS` includes frontend URL
- **Build errors**: Clear `node_modules` and reinstall dependencies

### OCR Issues

- **No text extracted**: Ensure image is clear, well-lit, and contains text
- **Poor accuracy**: Try different OCR provider (easyocr, paddleocr) or improve image quality

## License

This is a proof-of-concept application. Adapt for production use as needed.

## Contributing

This is a demo project. For production deployment, consider:

- Database integration for persistent storage
- User authentication and authorization
- Rate limiting and API security
- Error logging and monitoring
- Performance optimization
- Enhanced OCR accuracy
- Mobile responsiveness improvements
