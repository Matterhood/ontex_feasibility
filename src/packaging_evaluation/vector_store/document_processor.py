from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import fitz  # PyMuPDF
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
from .models import KnowledgeEntry

class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    filename: str
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    agent_type: str  # e.g., "technical", "operational", "reflection"
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentProcessor:
    """Process documents and prepare them for vector storage."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the document processor."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _generate_file_hash(self, file_path: str) -> str:
        """Generate a unique hash for a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _extract_text_from_pdf(self, file_path: str) -> List[str]:
        """Extract text from a PDF file."""
        doc = fitz.open(file_path)
        text_chunks = []
        
        for page in doc:
            text = page.get_text()
            # Split text into chunks
            words = text.split()
            current_chunk = []
            current_size = 0
            
            for word in words:
                current_chunk.append(word)
                current_size += len(word) + 1  # +1 for space
                
                if current_size >= self.chunk_size:
                    text_chunks.append(" ".join(current_chunk))
                    # Keep some words for overlap
                    overlap_words = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_words
                    current_size = sum(len(word) + 1 for word in overlap_words)
            
            if current_chunk:
                text_chunks.append(" ".join(current_chunk))
        
        doc.close()
        return text_chunks
    
    def _extract_text_from_txt(self, file_path: str) -> List[str]:
        """Extract text from a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Split text into chunks
        words = text.split()
        text_chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= self.chunk_size:
                text_chunks.append(" ".join(current_chunk))
                # Keep some words for overlap
                overlap_words = current_chunk[-self.chunk_overlap:]
                current_chunk = overlap_words
                current_size = sum(len(word) + 1 for word in overlap_words)
        
        if current_chunk:
            text_chunks.append(" ".join(current_chunk))
        
        return text_chunks
    
    def process_document(self, file_path: str, metadata: DocumentMetadata) -> List[KnowledgeEntry]:
        """Process a document and create knowledge entries."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate file hash
        file_hash = self._generate_file_hash(str(file_path))
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text_chunks = self._extract_text_from_pdf(str(file_path))
        elif file_path.suffix.lower() == '.txt':
            text_chunks = self._extract_text_from_txt(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Create knowledge entries for each chunk
        entries = []
        for i, chunk in enumerate(text_chunks):
            entry = KnowledgeEntry(
                id=f"{file_hash}_{i}",
                type="document",
                content=chunk,
                metadata={
                    "filename": metadata.filename,
                    "file_type": metadata.file_type,
                    "file_size": metadata.file_size,
                    "page_count": metadata.page_count,
                    "tags": metadata.tags,
                    "agent_type": metadata.agent_type,
                    "description": metadata.description,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks)
                }
            )
            entries.append(entry)
        
        return entries 