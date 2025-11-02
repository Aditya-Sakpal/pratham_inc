import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import uuid
from dotenv import load_dotenv

# Load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

# Add parent directory to path to access books folder
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pinecone import Pinecone as PineconeClient, ServerlessSpec


class PDFIngestionPipeline:
    """Pipeline to ingest PDF textbooks into Pinecone vector database"""
    
    def __init__(self, openai_api_key: str, pinecone_api_key: str, pinecone_index_name: str, books_folder: str):
        """
        Initialize the ingestion pipeline
        
        Args:
            openai_api_key: OpenAI API key for embeddings
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Name of the Pinecone index
            books_folder: Path to the folder containing PDF books
        """
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index_name = pinecone_index_name
        self.books_folder = books_folder
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-3-small",
            dimensions=512
        )
        
        # Initialize Pinecone
        self.pc = PineconeClient(api_key=pinecone_api_key)
        
        # Get or create index
        self.index = self._setup_pinecone_index()
        
    def _setup_pinecone_index(self):
        """Setup or connect to Pinecone index"""
        # Try to connect to the index first - if it exists, this will work
        try:
            index = self.pc.Index(self.pinecone_index_name)
            print(f"Connected to existing Pinecone index: {self.pinecone_index_name}")
            return index
        except Exception as e1:
            # Index might not exist, try to create it
            print(f"Index {self.pinecone_index_name} not found, attempting to create...")
            
            try:
                # Create index if it doesn't exist
                # text-embedding-3-large dimension is 3072
                # self.pc.create_index(
                #     name=self.pinecone_index_name,
                #     dimension=3072,  # OpenAI text-embedding-3-large dimension
                #     metric="cosine",
                #     spec=ServerlessSpec(
                #         cloud="aws",
                #         region="us-east-1"  # Adjust region as needed
                #     )
                # )
                # Wait for index to be ready
                import time
                print("Waiting for index to be ready...")
                time.sleep(10)  # Wait for index to initialize
            except Exception as e2:
                # Check if index already exists (409 error)
                error_str = str(e2)
                if "ALREADY_EXISTS" in error_str or "409" in error_str or "already exists" in error_str.lower():
                    print(f"Index {self.pinecone_index_name} already exists, connecting...")
                else:
                    print(f"Error creating index: {error_str}")
                    raise e2
        
        # Return the index connection (will work whether we created it or it already existed)
        return self.pc.Index(self.pinecone_index_name)
    
    def extract_class_from_filename(self, filename: str) -> str:
        """Extract class number from filename"""
        filename_lower = filename.lower()
        if "class8" in filename_lower or "classviii" in filename_lower:
            return "Class VIII"
        elif "class9" in filename_lower or "classix" in filename_lower:
            return "Class IX"
        elif "class10" in filename_lower or "classx" in filename_lower:
            return "Class X"
        else:
            return "Unknown"
    
    def load_pdf_with_pages(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Load PDF and extract text with page numbers"""
        print(f"Loading PDF: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Extract page numbers and text
        pages_data = []
        for i, doc in enumerate(documents):
            pages_data.append({
                "page_number": i + 1,  # PDF pages are 1-indexed
                "text": doc.page_content,
                "source": os.path.basename(pdf_path)
            })
        
        print(f"Loaded {len(pages_data)} pages from {os.path.basename(pdf_path)}")
        return pages_data
    
    def chunk_text_semantic(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        """Chunk text using semantic chunker"""
        # Create a document object for semantic chunker
        doc = Document(page_content=text, metadata={"page": page_number})
        
        # Initialize semantic chunker
        # You can adjust the threshold based on your needs (0.38 is default)
        text_splitter = SemanticChunker(
            OpenAIEmbeddings(
                openai_api_key=self.openai_api_key, 
                model="text-embedding-3-small",
                dimensions=512
            ),
            breakpoint_threshold_type="percentile"  # or "standard_deviation"
        )
        
        # Split the document
        chunks = text_splitter.split_documents([doc])
        
        chunk_data = []
        for chunk in chunks:
            chunk_data.append({
                "text": chunk.page_content,
                "metadata": chunk.metadata
            })
        
        return chunk_data
    
    def process_book(self, pdf_path: str, namespace: str = "default") -> int:
        """Process a single book and upload to Pinecone"""
        filename = os.path.basename(pdf_path)
        class_name = self.extract_class_from_filename(filename)
        
        print(f"\n{'='*60}")
        print(f"Processing: {filename} ({class_name})")
        print(f"{'='*60}")
        
        # Load PDF with page numbers
        pages_data = self.load_pdf_with_pages(pdf_path)
        
        # Process each page and chunk
        all_chunks = []
        total_chunks = 0
        
        for page_data in pages_data:
            page_number = page_data["page_number"]
            text = page_data["text"]
            
            # Skip empty pages
            if not text or not text.strip():
                continue
            
            print(f"  Processing page {page_number}...")
            
            # Chunk the page text semantically
            chunks = self.chunk_text_semantic(text, page_number)
            
            # Prepare chunks with metadata
            for chunk_idx, chunk_info in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                chunk_text = chunk_info["text"]
                
                metadata = {
                    "class": class_name,
                    "subject": "Science",
                    "page_number": page_number,
                    "chunk_text": chunk_text,
                    "chunk_id": chunk_id,
                    "datetime": datetime.now().isoformat(),
                    "source_file": filename,
                    "chunk_index": chunk_idx,
                    "language": "English"
                }
                
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": metadata
                })
                
                total_chunks += 1
        
        print(f"\n  Generated {total_chunks} chunks from {filename}")
        
        # Generate embeddings and upsert in batches
        self._upsert_chunks_to_pinecone(all_chunks, namespace, batch_size=100)
        
        return total_chunks
    
    def _upsert_chunks_to_pinecone(self, chunks: List[Dict[str, Any]], namespace: str, batch_size: int = 100):
        """Upsert chunks to Pinecone in batches"""
        print(f"\nGenerating embeddings and upserting to Pinecone namespace: {namespace}")
        print(f"Total chunks to upsert: {len(chunks)}")
        
        # Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        print("Generating embeddings...")
        embeddings_list = self.embeddings.embed_documents(texts)
        
        # Prepare vectors for Pinecone
        vectors_to_upsert = []
        for i, chunk in enumerate(chunks):
            vector = {
                "id": chunk["id"],
                "values": embeddings_list[i],
                "metadata": chunk["metadata"]
            }
            vectors_to_upsert.append(vector)
        
        # Upsert in batches
        total_batches = (len(vectors_to_upsert) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(vectors_to_upsert))
            batch = vectors_to_upsert[start_idx:end_idx]
            
            print(f"  Upserting batch {batch_num + 1}/{total_batches} ({len(batch)} vectors)...")
            try:
                self.index.upsert(vectors=batch, namespace=namespace)
                print(f"  ✓ Batch {batch_num + 1} upserted successfully")
            except Exception as e:
                print(f"  ✗ Error upserting batch {batch_num + 1}: {str(e)}")
                raise
        
        print(f"\n✓ Successfully upserted {len(vectors_to_upsert)} chunks to Pinecone")
    
    def ingest_all_books(self, namespace: str = "default"):
        """Ingest all PDF books in the books folder"""
        print(f"\n{'='*60}")
        print("Starting PDF Ingestion Pipeline")
        print(f"{'='*60}")
        
        # Find all PDF files
        pdf_files = [
            os.path.join(self.books_folder, f)
            for f in os.listdir(self.books_folder)
            if f.lower().endswith('.pdf')
        ]
        
        if not pdf_files:
            print(f"No PDF files found in {self.books_folder}")
            return
        
        print(f"\nFound {len(pdf_files)} PDF file(s):")
        for pdf_file in pdf_files:
            print(f"  - {os.path.basename(pdf_file)}")
        
        total_chunks = 0
        
        # Process each book
        for pdf_file in sorted(pdf_files):
            try:
                chunks_count = self.process_book(pdf_file, namespace)
                total_chunks += chunks_count
            except Exception as e:
                print(f"\n✗ Error processing {os.path.basename(pdf_file)}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n{'='*60}")
        print(f"Ingestion Complete!")
        print(f"Total chunks ingested: {total_chunks}")
        print(f"Namespace: {namespace}")
        print(f"{'='*60}\n")


def main():
    """Main function to run the ingestion pipeline"""
    import os
    
    # Environment variables are already loaded at module level
    # Get API keys from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "ncert-textbooks")
    namespace = os.getenv("PINECONE_NAMESPACE", "ncert-science")
    
    # Validate API keys
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    
    # Get books folder path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    books_folder = os.path.join(project_root, "books")
    
    if not os.path.exists(books_folder):
        raise ValueError(f"Books folder not found: {books_folder}")
    
    print(f"Books folder: {books_folder}")
    print(f"Pinecone index: {pinecone_index_name}")
    print(f"Pinecone namespace: {namespace}")
    
    # Initialize and run pipeline
    pipeline = PDFIngestionPipeline(
        openai_api_key=openai_api_key,
        pinecone_api_key=pinecone_api_key,
        pinecone_index_name=pinecone_index_name,
        books_folder=books_folder
    )
    
    # Ingest all books
    pipeline.ingest_all_books(namespace=namespace)


if __name__ == "__main__":
    main()

