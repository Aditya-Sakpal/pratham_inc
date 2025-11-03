"""
FastAPI main application entry point for NCERT Science Learning Platform
Provides endpoints for topic selection, summarization, chat Q&A, quiz generation, and evaluation
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from app.routers import topics, summary, chat, quiz, evaluation

# Initialize FastAPI app
# CRITICAL: Disable redirect_slashes to prevent redirect loops in Lambda Function URLs
app = FastAPI(
    title="NCERT Science Learning Platform",
    description="Backend API for NCERT Science learning with chat, summaries, quizzes, and evaluation",
    version="1.0.0",
    redirect_slashes=False
)

# CORS is handled by AWS Lambda Function URL configuration
# No need to configure CORS in FastAPI when using Lambda Function URLs

# Include routers
# Add explicit routes to handle both with/without trailing slash (no redirects)
from app.routers.topics import list_topics, list_classes, get_topic
from app.routers.summary import generate_summary
from app.routers.quiz import generate_quiz, get_quiz

# Explicit routes for topics - handle both /api/topics and /api/topics/
app.add_api_route("/api/topics", list_topics, methods=["GET"], tags=["topics"])
app.add_api_route("/api/topics/", list_topics, methods=["GET"], tags=["topics"])
app.add_api_route("/api/topics/classes", list_classes, methods=["GET"], tags=["topics"])
app.add_api_route("/api/topics/{topic_id}", get_topic, methods=["GET"], tags=["topics"])

# Explicit routes for summary - handle both /api/summary and /api/summary/
app.add_api_route("/api/summary", generate_summary, methods=["POST"], tags=["summary"])
app.add_api_route("/api/summary/", generate_summary, methods=["POST"], tags=["summary"])

# Explicit routes for quiz - handle both /api/quiz and /api/quiz/
app.add_api_route("/api/quiz", generate_quiz, methods=["POST"], tags=["quiz"])
app.add_api_route("/api/quiz/", generate_quiz, methods=["POST"], tags=["quiz"])
app.add_api_route("/api/quiz/{quiz_id}", get_quiz, methods=["GET"], tags=["quiz"])

# Chat and evaluation use prefix (no trailing slash issues)
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
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
    import traceback
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
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