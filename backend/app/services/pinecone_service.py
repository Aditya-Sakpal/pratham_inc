"""
Pinecone vector database service
Handles embedding retrieval from Pinecone index
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from app.config import settings


class PineconeService:
    """Service for interacting with Pinecone vector database"""
    
    def __init__(self):
        """Initialize Pinecone client and embeddings"""
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        # Initialize embeddings - use environment variable if available
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_EMBEDDING_MODEL,
            dimensions=settings.OPENAI_EMBEDDING_DIMENSIONS
        )
    
    def get_relevant_chunks(
        self, 
        query: str, 
        topic_name: Optional[str] = None,
        class_level: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from Pinecone based on query
        
        Args:
            query: Search query
            topic_name: Optional topic name filter
            class_level: Optional class level filter
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        # Enhance query with topic name if provided for better semantic search
        enhanced_query = query
        if topic_name:
            enhanced_query = f"{topic_name} {query}"
        
        # Generate embedding for enhanced query
        query_embedding = self.embeddings.embed_query(enhanced_query)
        
        # Build filter if class specified
        filter_dict = {}
        if class_level:
            filter_dict["class"] = class_level
        
        # Increase top_k if filtering by class to get more results
        query_top_k = top_k * 2 if filter_dict else top_k
        
        # Query Pinecone
        if filter_dict:
            results = self.index.query(
                vector=query_embedding,
                top_k=query_top_k,
                include_metadata=True,
                namespace=settings.PINECONE_NAMESPACE,
                filter=filter_dict
            )
        else:
            results = self.index.query(
                vector=query_embedding,
                top_k=query_top_k,
                include_metadata=True,
                namespace=settings.PINECONE_NAMESPACE
            )
        
        # Format results and filter by minimum score
        chunks = []
        for match in results.matches:
            # Only include chunks with reasonable similarity score
            if match.score >= 0.25:  # Minimum similarity threshold
                chunks.append({
                    "text": match.metadata.get("chunk_text", ""),
                    "page_number": match.metadata.get("page_number"),
                    "class": match.metadata.get("class"),
                    "source": match.metadata.get("source_file"),
                    "score": match.score,
                    "chunk_id": match.id
                })
        
        # Return top_k chunks after filtering
        return chunks[:top_k] if chunks else []
    
    def search_by_topic(
        self, 
        topic_name: str, 
        class_level: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for chunks related to a specific topic
        
        Args:
            topic_name: Name of the topic
            class_level: Class level (Class VIII, IX, or X)
            top_k: Number of results
            
        Returns:
            List of relevant chunks
        """
        # Create a query combining topic name and class
        query = f"{topic_name} {class_level}"
        return self.get_relevant_chunks(query, topic_name, class_level, top_k)


# Global instance - lazy initialization to avoid crashes on import
_pinecone_service = None

class _LazyPineconeService:
    """Lazy wrapper that initializes PineconeService on first access"""
    def __getattr__(self, name):
        global _pinecone_service
        if _pinecone_service is None:
            _pinecone_service = PineconeService()
        return getattr(_pinecone_service, name)
    
    def __call__(self, *args, **kwargs):
        """Allow calling the wrapper itself"""
        global _pinecone_service
        if _pinecone_service is None:
            _pinecone_service = PineconeService()
        return _pinecone_service

pinecone_service = _LazyPineconeService()

