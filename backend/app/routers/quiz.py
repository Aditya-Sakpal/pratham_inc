"""
Quiz router - handles quiz generation
"""
import uuid
from fastapi import APIRouter, HTTPException
from app.models.schemas import QuizRequest, QuizResponse, QuizQuestion
from app.services.llm_service import llm_service
from app.services.pinecone_service import pinecone_service

router = APIRouter()

# In-memory storage for quizzes (use database in production)
quiz_storage = {}


@router.post("/", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz for a topic
    
    Args:
        request: Quiz request with topic and question counts
        
    Returns:
        Quiz response with questions
    """
    try:
        # Retrieve relevant chunks from Pinecone
        context_chunks = pinecone_service.search_by_topic(
            topic_name=request.topic_name,
            class_level=request.class_level,
            top_k=15
        )
        
        if not context_chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for topic: {request.topic_name}"
            )
        
        # Generate quiz using LLM
        quiz_data = llm_service.generate_quiz(
            topic_name=request.topic_name,
            class_level=request.class_level,
            context_chunks=context_chunks,
            num_mcqs=request.num_mcqs,
            num_fill_blank=request.num_fill_blank,
            num_short_answer=request.num_short_answer
        )
        
        # Generate quiz ID
        quiz_id = str(uuid.uuid4())
        
        # Format questions
        questions = []
        for i, q_data in enumerate(quiz_data.get("questions", []), 1):
            question = QuizQuestion(
                question_id=q_data.get("question_id", f"q{i}"),
                question_type=q_data.get("question_type", "mcq"),
                question=q_data.get("question", ""),
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer", ""),
                explanation=q_data.get("explanation")
            )
            questions.append(question)
        
        # Store quiz for later evaluation
        quiz_storage[quiz_id] = {
            "questions": [q.dict() for q in questions],
            "topic_id": request.topic_id,
            "topic_name": request.topic_name
        }
        
        return QuizResponse(
            quiz_id=quiz_id,
            topic_id=request.topic_id,
            topic_name=request.topic_name,
            questions=questions,
            total_questions=len(questions)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    """
    Retrieve a stored quiz
    
    Args:
        quiz_id: Quiz identifier
        
    Returns:
        Quiz response
    """
    if quiz_id not in quiz_storage:
        raise HTTPException(status_code=404, detail=f"Quiz {quiz_id} not found")
    
    quiz_data = quiz_storage[quiz_id]
    questions = [
        QuizQuestion(**q) for q in quiz_data["questions"]
    ]
    
    return QuizResponse(
        quiz_id=quiz_id,
        topic_id=quiz_data["topic_id"],
        topic_name=quiz_data["topic_name"],
        questions=questions,
        total_questions=len(questions)
    )

