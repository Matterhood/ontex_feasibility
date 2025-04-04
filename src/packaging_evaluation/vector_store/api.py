from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from pathlib import Path
import shutil
from datetime import datetime

from .document_processor import DocumentProcessor, DocumentMetadata
from .client import VectorStoreClient

app = FastAPI(title="Packaging Knowledge Base API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
document_processor = DocumentProcessor()
vector_store = VectorStoreClient()

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    tags: List[str] = [],
    agent_type: str = "technical",
    description: Optional[str] = None
):
    """Upload a document and process it for the vector store."""
    try:
        # Save file temporarily
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file metadata
        file_size = file_path.stat().st_size
        file_type = file_path.suffix.lower()
        
        # Create document metadata
        metadata = DocumentMetadata(
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            tags=tags,
            agent_type=agent_type,
            description=description
        )
        
        # Process document
        entries = document_processor.process_document(str(file_path), metadata)
        
        # Add entries to vector store
        for entry in entries:
            await vector_store.add_knowledge_entry(entry)
        
        # Clean up
        file_path.unlink()
        
        return {
            "message": "Document processed successfully",
            "entries_created": len(entries),
            "metadata": metadata.dict()
        }
    
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_documents(
    query: str,
    agent_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 5
):
    """Search for documents in the vector store."""
    try:
        # Search in vector store
        results = await vector_store.search_similar(query, limit)
        
        # Filter results if agent_type or tags are specified
        if agent_type or tags:
            filtered_results = []
            for result in results:
                if agent_type and result.metadata.get("agent_type") != agent_type:
                    continue
                if tags and not all(tag in result.metadata.get("tags", []) for tag in tags):
                    continue
                filtered_results.append(result)
            results = filtered_results
        
        return {
            "results": [
                {
                    "id": result.id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "similarity": result.metadata.get("similarity", 0)
                }
                for result in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(
    agent_type: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    """List all documents in the vector store."""
    try:
        # Get all documents
        results = await vector_store.search_similar("", limit=1000)
        
        # Filter results if agent_type or tags are specified
        if agent_type or tags:
            filtered_results = []
            for result in results:
                if agent_type and result.metadata.get("agent_type") != agent_type:
                    continue
                if tags and not all(tag in result.metadata.get("tags", []) for tag in tags):
                    continue
                filtered_results.append(result)
            results = filtered_results
        
        # Group by filename
        documents = {}
        for result in results:
            filename = result.metadata.get("filename")
            if filename not in documents:
                documents[filename] = {
                    "filename": filename,
                    "file_type": result.metadata.get("file_type"),
                    "file_size": result.metadata.get("file_size"),
                    "page_count": result.metadata.get("page_count"),
                    "tags": result.metadata.get("tags", []),
                    "agent_type": result.metadata.get("agent_type"),
                    "description": result.metadata.get("description"),
                    "chunks": []
                }
            documents[filename]["chunks"].append({
                "id": result.id,
                "content": result.content,
                "chunk_index": result.metadata.get("chunk_index"),
                "total_chunks": result.metadata.get("total_chunks")
            })
        
        return {"documents": list(documents.values())}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 