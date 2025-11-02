"""
FastAPI main application entry point for NCERT Science Learning Platform
Provides endpoints for topic selection, summarization, chat Q&A, quiz generation, and evaluation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.routers import topics, summary, chat, quiz, evaluation
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="NCERT Science Learning Platform",
    description="Backend API for NCERT Science learning with chat, summaries, quizzes, and evaluation",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])


@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"message": "NCERT Science Learning Platform API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )