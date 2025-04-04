from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
from .models import KnowledgeEntry, MachineSpec, MaterialSpec, ProcessSpec

class VectorStoreClient:
    """Client for interacting with the vector store."""
    
    def __init__(self):
        """Initialize the vector store client."""
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings()
    
    async def add_knowledge_entry(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Add a new knowledge entry to the vector store."""
        # Generate embedding for the content
        embedding = await self.embeddings.ainvoke(entry.content)
        
        # Prepare data for insertion
        data = {
            "id": entry.id,
            "type": entry.type,
            "content": entry.content,
            "metadata": entry.metadata,
            "embedding": embedding,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat()
        }
        
        # Insert into Supabase
        result = self.supabase.table("knowledge_base").insert(data).execute()
        
        return KnowledgeEntry(**result.data[0])
    
    async def search_similar(self, query: str, limit: int = 5) -> List[KnowledgeEntry]:
        """Search for similar knowledge entries using vector similarity."""
        # Generate embedding for the query
        query_embedding = await self.embeddings.ainvoke(query)
        
        # Perform vector similarity search in Supabase
        result = self.supabase.rpc(
            "match_knowledge",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.7,
                "match_count": limit
            }
        ).execute()
        
        return [KnowledgeEntry(**item) for item in result.data]
    
    async def add_machine(self, machine: MachineSpec) -> MachineSpec:
        """Add a new machine specification to the vector store."""
        # Convert to knowledge entry
        entry = KnowledgeEntry(
            id=machine.id,
            type="machine",
            content=machine.specifications,
            metadata={
                "name": machine.name,
                "type": machine.type,
                "capabilities": machine.capabilities,
                "constraints": machine.constraints
            }
        )
        
        # Add to vector store
        result = await self.add_knowledge_entry(entry)
        
        # Convert back to MachineSpec
        return MachineSpec(
            id=result.id,
            name=result.metadata["name"],
            type=result.metadata["type"],
            capabilities=result.metadata["capabilities"],
            constraints=result.metadata["constraints"],
            specifications=result.content,
            embedding=result.embedding
        )
    
    async def add_material(self, material: MaterialSpec) -> MaterialSpec:
        """Add a new material specification to the vector store."""
        # Convert to knowledge entry
        entry = KnowledgeEntry(
            id=material.id,
            type="material",
            content=material.specifications,
            metadata={
                "name": material.name,
                "type": material.type,
                "properties": material.properties,
                "constraints": material.constraints
            }
        )
        
        # Add to vector store
        result = await self.add_knowledge_entry(entry)
        
        # Convert back to MaterialSpec
        return MaterialSpec(
            id=result.id,
            name=result.metadata["name"],
            type=result.metadata["type"],
            properties=result.metadata["properties"],
            constraints=result.metadata["constraints"],
            specifications=result.content,
            embedding=result.embedding
        )
    
    async def add_process(self, process: ProcessSpec) -> ProcessSpec:
        """Add a new process specification to the vector store."""
        # Convert to knowledge entry
        entry = KnowledgeEntry(
            id=process.id,
            type="process",
            content=process.specifications,
            metadata={
                "name": process.name,
                "type": process.type,
                "requirements": process.requirements,
                "constraints": process.constraints
            }
        )
        
        # Add to vector store
        result = await self.add_knowledge_entry(entry)
        
        # Convert back to ProcessSpec
        return ProcessSpec(
            id=result.id,
            name=result.metadata["name"],
            type=result.metadata["type"],
            requirements=result.metadata["requirements"],
            constraints=result.metadata["constraints"],
            specifications=result.content,
            embedding=result.embedding
        ) 