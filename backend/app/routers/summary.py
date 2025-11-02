"""
Summary router - handles topic summarization
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import SummaryRequest, SummaryResponse
from app.services.llm_service import llm_service
from app.services.pinecone_service import pinecone_service

router = APIRouter()


@router.post("/", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """
    Generate a summary for a topic
    
    Args:
        request: Summary request with topic information
        
    Returns:
        Summary response with summary text and key points
    """
    try:
        # Retrieve relevant chunks from Pinecone
        context_chunks = pinecone_service.search_by_topic(
            topic_name=request.topic_name,
            class_level=request.class_level,
            top_k=10
        )
        
        if not context_chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for topic: {request.topic_name}"
            )
        
        # Generate summary using LLM
        summary_data = llm_service.generate_summary(
            topic_name=request.topic_name,
            class_level=request.class_level,
            context_chunks=context_chunks
        )
        
        return SummaryResponse(
            topic_id=request.topic_id,
            topic_name=request.topic_name,
            summary=summary_data["summary"],
            key_points=summary_data["key_points"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

