"""
Evaluation router - handles quiz answer evaluation
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.models.schemas import EvaluationRequest, EvaluationResponse, ImageUploadResponse
from app.services.llm_service import llm_service
from app.services.ocr_service import ocr_service
import uuid
import json

# Import quiz storage from quiz router (runtime import to avoid circular dependency)
from app.routers import quiz
quiz_storage = quiz.quiz_storage

router = APIRouter()

# In-memory storage for evaluations
evaluation_storage = {}


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload and process image for OCR
    
    Args:
        file: Image file to process
        
    Returns:
        OCR results with extracted text
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file data
        image_data = await file.read()
        
        # Check file size
        if len(image_data) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Extract text using OCR
        ocr_result = ocr_service.extract_text(image_data)
        
        file_id = str(uuid.uuid4())
        
        return ImageUploadResponse(
            file_id=file_id,
            extracted_text=ocr_result.get("extracted_text", ""),
            confidence=ocr_result.get("confidence")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answers_multipart(
    quiz_id: str = Form(...),
    answers: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Evaluate quiz answers with FormData (supports optional image upload)
    
    This endpoint accepts FormData with:
    - quiz_id: Quiz identifier (required)
    - answers: JSON string of answers (required)
    - file: Optional image file for OCR
    
    Args:
        quiz_id: Quiz identifier (from FormData)
        answers: JSON string of answers (from FormData)
        file: Optional image file (from FormData)
        
    Returns:
        Evaluation results with feedback
    """
    try:
        # Parse answers JSON
        try:
            answers_dict = json.loads(answers) if isinstance(answers, str) else answers
        except json.JSONDecodeError:
            answers_dict = {}
        
        # Check if quiz exists
        if quiz_id not in quiz_storage:
            raise HTTPException(status_code=404, detail=f"Quiz {quiz_id} not found")
        
        quiz_data = quiz_storage[quiz_id]
        quiz_questions = quiz_data["questions"]
        
        # If file is provided, extract text from image and merge with answers
        if file and file.filename:
            image_data = await file.read()
            ocr_result = ocr_service.extract_text(image_data)
            extracted_text = ocr_result.get("extracted_text", "")
            
            # # Merge OCR-extracted answers with provided answers
            # if extracted_text:
            #     lines = [l.strip() for l in extracted_text.split('\n') if l.strip()]
            #     for i, question in enumerate(quiz_questions):
            #         question_id = question.get("question_id", f"q{i+1}")
            #         if i < len(lines) and lines[i]:
            #             # OCR answers can supplement manual answers if they're empty
            #             if question_id not in answers_dict or not answers_dict.get(question_id):
            #                 answers_dict[question_id] = lines[i]
        
        # Evaluate using LLM
        evaluation = llm_service.evaluate_answers(
            quiz_questions=quiz_questions,
            student_answers=answers_dict,
            topic_name=quiz_data["topic_name"],
            extracted_text=extracted_text
        )
        
        # Format question results
        question_results = []
        for i, result in enumerate(evaluation.get("question_results", [])):
            question_results.append({
                "question_id": result.get("question_id", f"q{i+1}"),
                "is_correct": result.get("is_correct", False),
                "feedback": result.get("feedback", ""),
                "needs_review": result.get("needs_review", False)
            })
        
        # Store evaluation
        evaluation_id = str(uuid.uuid4())
        evaluation_storage[evaluation_id] = evaluation
        
        return EvaluationResponse(
            quiz_id=quiz_id,
            total_questions=evaluation.get("total_questions", len(question_results)),
            correct_count=evaluation.get("correct_count", 0),
            score_percentage=evaluation.get("score_percentage", 0.0),
            question_results=question_results,
            topics_to_review=evaluation.get("topics_to_review", []),
            feedback=evaluation.get("overall_feedback", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answers: {str(e)}")


@router.post("/evaluate-json", response_model=EvaluationResponse)
async def evaluate_answers_json(request: EvaluationRequest):
    """
    Evaluate quiz answers (JSON endpoint for backward compatibility)
    
    Args:
        request: Evaluation request with quiz ID and answers
        
    Returns:
        Evaluation results with feedback
    """
    try:
        # Retrieve quiz
        if request.quiz_id not in quiz_storage:
            raise HTTPException(status_code=404, detail=f"Quiz {request.quiz_id} not found")
        
        quiz_data = quiz_storage[request.quiz_id]
        quiz_questions = quiz_data["questions"]
        
        # Evaluate using LLM
        evaluation = llm_service.evaluate_answers(
            quiz_questions=quiz_questions,
            student_answers=request.answers,
            topic_name=quiz_data["topic_name"]
        )
        
        # Format question results
        question_results = []
        for i, result in enumerate(evaluation.get("question_results", [])):
            question_results.append({
                "question_id": result.get("question_id", f"q{i+1}"),
                "is_correct": result.get("is_correct", False),
                "feedback": result.get("feedback", ""),
                "needs_review": result.get("needs_review", False)
            })
        
        # Store evaluation
        evaluation_id = str(uuid.uuid4())
        evaluation_storage[evaluation_id] = evaluation
        
        return EvaluationResponse(
            quiz_id=request.quiz_id,
            total_questions=evaluation.get("total_questions", len(question_results)),
            correct_count=evaluation.get("correct_count", 0),
            score_percentage=evaluation.get("score_percentage", 0.0),
            question_results=question_results,
            topics_to_review=evaluation.get("topics_to_review", []),
            feedback=evaluation.get("overall_feedback", "")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answers: {str(e)}")


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(evaluation_id: str):
    """
    Retrieve stored evaluation
    
    Args:
        evaluation_id: Evaluation identifier
        
    Returns:
        Evaluation results
    """
    if evaluation_id not in evaluation_storage:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    
    evaluation = evaluation_storage[evaluation_id]
    
    return EvaluationResponse(**evaluation)
