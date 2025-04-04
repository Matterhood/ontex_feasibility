from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MachineSpec(BaseModel):
    """Specifications for a manufacturing machine."""
    id: str = Field(description="Unique identifier for the machine")
    name: str = Field(description="Name of the machine")
    type: str = Field(description="Type of machine (e.g., printer, cutter, folder)")
    capabilities: List[str] = Field(description="List of capabilities")
    constraints: List[str] = Field(description="List of constraints")
    specifications: str = Field(description="Detailed technical specifications")
    embedding: Optional[List[float]] = Field(description="Vector embedding of the specifications")

class MaterialSpec(BaseModel):
    """Specifications for a material."""
    id: str = Field(description="Unique identifier for the material")
    name: str = Field(description="Name of the material")
    type: str = Field(description="Type of material (e.g., paper, plastic, metal)")
    properties: List[str] = Field(description="List of material properties")
    constraints: List[str] = Field(description="List of constraints")
    specifications: str = Field(description="Detailed technical specifications")
    embedding: Optional[List[float]] = Field(description="Vector embedding of the specifications")

class ProcessSpec(BaseModel):
    """Specifications for a manufacturing process."""
    id: str = Field(description="Unique identifier for the process")
    name: str = Field(description="Name of the process")
    type: str = Field(description="Type of process (e.g., printing, cutting, folding)")
    requirements: List[str] = Field(description="List of requirements")
    constraints: List[str] = Field(description="List of constraints")
    specifications: str = Field(description="Detailed technical specifications")
    embedding: Optional[List[float]] = Field(description="Vector embedding of the specifications")

class KnowledgeEntry(BaseModel):
    """A knowledge entry in the vector store."""
    id: str = Field(description="Unique identifier for the entry")
    type: str = Field(description="Type of knowledge (machine/material/process)")
    content: str = Field(description="The actual content")
    metadata: dict = Field(description="Additional metadata")
    embedding: Optional[List[float]] = Field(description="Vector embedding of the content")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 