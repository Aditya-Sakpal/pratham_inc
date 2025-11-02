"""
Pydantic models for request/response schemas
Defines data structures for API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TopicResponse(BaseModel):
    """Topic information response"""
    topic_id: str
    topic_name: str
    class_level: str
    chapter: Optional[str] = None
    description: Optional[str] = None


class SummaryRequest(BaseModel):
    """Request for generating a topic summary"""
    topic_id: str
    topic_name: str
    class_level: str


class SummaryResponse(BaseModel):
    """Response containing topic summary"""
    topic_id: str
    topic_name: str
    summary: str
    key_points: List[str]


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat Q&A"""
    topic_id: str
    topic_name: str
    messages: List[ChatMessage]
    class_level: Optional[str] = None
    context_chunks: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    """Response from chat Q&A"""
    response: str
    sources: Optional[List[Dict[str, Any]]] = None


class QuizRequest(BaseModel):
    """Request for quiz generation"""
    topic_id: str
    topic_name: str
    class_level: str
    num_mcqs: int = Field(default=5, ge=1, le=20)
    num_fill_blank: int = Field(default=3, ge=1, le=10)
    num_short_answer: int = Field(default=2, ge=1, le=10)


class QuizQuestion(BaseModel):
    """Single quiz question"""
    question_id: str
    question_type: str = Field(..., description="mcq, fill_blank, or short_answer")
    question: str
    options: Optional[List[str]] = None  # For MCQ
    correct_answer: str
    explanation: Optional[str] = None


class QuizResponse(BaseModel):
    """Response containing generated quiz"""
    quiz_id: str
    topic_id: str
    topic_name: str
    questions: List[QuizQuestion]
    total_questions: int


class EvaluationRequest(BaseModel):
    """Request for evaluating quiz answers"""
    quiz_id: str
    answers: Dict[str, str] = Field(..., description="Map of question_id to student answer")


class EvaluationResponse(BaseModel):
    """Response containing evaluation results"""
    quiz_id: str
    total_questions: int
    correct_count: int
    score_percentage: float
    question_results: List[Dict[str, Any]]
    topics_to_review: List[str]
    feedback: str


class ImageUploadResponse(BaseModel):
    """Response after image upload and OCR"""
    file_id: str
    extracted_text: str
    confidence: Optional[float] = None

