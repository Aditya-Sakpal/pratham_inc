"""
Chat router - handles conversational Q&A about topics
"""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.services.pinecone_service import pinecone_service

router = APIRouter()


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Handle streaming chat Q&A about a topic (Server-Sent Events)
    
    Args:
        request: Chat request with messages and topic
        
    Returns:
        Streaming response with answer chunks
    """
    async def generate_stream():
        try:
            # Get the last user message
            user_messages = [msg for msg in request.messages if msg.role == "user"]
            if not user_messages:
                yield f"data: {json.dumps({'error': 'No user message found'})}\n\n"
                return
            
            last_user_message = user_messages[-1].content
            
            # Extract class_level from request or use default
            class_level = request.class_level if request.class_level else "Class VIII"
            
            # Retrieve relevant chunks from Pinecone based on query
            context_chunks = pinecone_service.get_relevant_chunks(
                query=last_user_message,
                topic_name=request.topic_name,
                class_level=class_level,
                top_k=5
            )
            
            if not context_chunks:
                # Try broader search by topic with class level
                context_chunks = pinecone_service.search_by_topic(
                    topic_name=request.topic_name,
                    class_level=class_level,
                    top_k=5
                )
            
            # Convert messages to dict format
            messages_dict = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Stream response from LLM
            full_response = ""
            for chunk in llm_service.chat_with_context(
                topic_name=request.topic_name,
                messages=messages_dict,
                context_chunks=context_chunks,
                stream=True
            ):
                full_response += chunk
                # Send each chunk as SSE
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Send sources after response is complete
            sources = [
                {
                    "page_number": chunk.get("page_number"),
                    "source": chunk.get("source"),
                    "class": chunk.get("class")
                }
                for chunk in context_chunks[:3]
            ]
            
            # Send final message with complete response and sources
            yield f"data: {json.dumps({'done': True, 'full_response': full_response, 'sources': sources})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    # Create streaming response with CORS headers
    # Note: CORS middleware should handle CORS, but we add headers explicitly for streaming
    response = StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
    # Add headers for SSE
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat Q&A about a topic
    
    Args:
        request: Chat request with messages and topic
        
    Returns:
        Chat response with answer and sources
    """
    try:
        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_user_message = user_messages[-1].content
        
        # Retrieve relevant chunks from Pinecone based on query
        context_chunks = pinecone_service.get_relevant_chunks(
            query=last_user_message,
            topic_name=request.topic_name,
            top_k=5
        )
        
        if not context_chunks:
            # Try broader search by topic
            context_chunks = pinecone_service.search_by_topic(
                topic_name=request.topic_name,
                class_level="Class VIII",  # Default, could be enhanced
                top_k=3
            )
        
        # Convert messages to dict format
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Generate response using LLM
        response_text = llm_service.chat_with_context(
            topic_name=request.topic_name,
            messages=messages_dict,
            context_chunks=context_chunks
        )
        
        # Prepare sources from context chunks
        sources = [
            {
                "page_number": chunk.get("page_number"),
                "source": chunk.get("source"),
                "class": chunk.get("class")
            }
            for chunk in context_chunks[:3]
        ]
        
        return ChatResponse(
            response=response_text,
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

