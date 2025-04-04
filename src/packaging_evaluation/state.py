from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

class Component(BaseModel):
    """A component of the packaging concept."""
    name: str = Field(description="Name of the component")
    material: str = Field(description="Material the component is made of, be as descriptive as possible")
    function: str = Field(description="Primary function of the component, the use of the material, component")
    requirements: List[str] = Field(description="Requirements for the component to fulfill its purpose")

class ComponentAssessment(BaseModel):
    """Assessment details for a single component."""
    component_name: str = Field(description="Name of the component being assessed")
    feasible: bool = Field(description="Whether the component is technically feasible")
    notes: str = Field(description="Detailed technical assessment notes")
    challenges: List[str] = Field(description="Technical challenges identified")
    technical_score: float = Field(description="Technical feasibility score (0.0-1.0)")

class TechnicalAssessment(BaseModel):
    """Technical feasibility assessment."""
    overall_feasible: bool = Field(description="Whether the concept is technically feasible overall")
    component_assessments: List[ComponentAssessment] = Field(
        description="List of assessments for each component")
    technical_summary: str = Field(description="Summary of technical feasibility")

class OperationalAssessment(BaseModel):
    """Operational impact assessment."""
    supply_chain_impact: str = Field(description="Impact on supply chain (Low/Medium/High)")
    production_changes_needed: List[str] = Field(description="Changes needed to production processes")
    cost_impact: str = Field(description="Estimated cost impact")
    overall_feasible: bool = Field(description="Whether the concept is operationally feasible")
    operational_summary: str = Field(description="Summary of operational impact")

class ReflectionNotes(BaseModel):
    """Reflection on assessments."""
    blind_spots: List[str] = Field(description="Blind spots identified in the assessments")
    questions: List[str] = Field(description="Questions raised during reflection")
    requires_iteration: bool = Field(description="Whether further iteration is required")
    reflection_summary: str = Field(description="Summary of reflection insights")
    assessment_approved: bool = Field(description="Whether the technical and operational assessments are approved")
    iteration_count: int = Field(description="Number of assessment iterations completed")

class ImprovementRecommendation(BaseModel):
    """A specific recommendation for improving feasibility."""
    area: str = Field(description="The area of the packaging concept to improve")
    recommendation: str = Field(description="The specific improvement recommendation")

class FinalEvaluation(BaseModel):
    """Final evaluation and recommendations."""
    feasibility_score: int = Field(description="Overall feasibility score (1-10, with 10 being most feasible)")
    feasibility_summary: str = Field(description="Summary of overall feasibility")
    expert_rationale: str = Field(description="Detailed expert rationale explaining the reasons behind the feasibility score")
    key_strengths: List[str] = Field(description="Key strengths of the concept")
    key_challenges: List[str] = Field(description="Key challenges or barriers")
    improvement_recommendations: List[ImprovementRecommendation] = Field(description="Specific recommendations for improvement")
    go_decision: bool = Field(description="Whether to proceed with the concept")
    action_items: List[str] = Field(description="Recommended next steps")
    executive_summary: str = Field(description="Brief executive summary")

class ImageAnalysis(BaseModel):
    """Analysis of packaging concept images."""
    observations: List[str] = Field(description="Key observations from the concept image")
    identified_components: List[str] = Field(description="Components identified in the image")
    materials_detected: List[str] = Field(description="Materials that appear to be used in the concept")
    design_features: List[str] = Field(description="Notable design features observed")
    analysis_summary: str = Field(description="Summary of image analysis findings")

class UserFeedback(BaseModel):
    """User feedback on component and material assumptions."""
    is_correct: bool = Field(description="Whether the component and material assumptions are correct")
    feedback_notes: List[str] = Field(description="Specific feedback notes from the user")
    suggested_changes: List[str] = Field(description="Suggested changes to components or materials")

class PackagingEvaluationState(BaseModel):
    """State for the packaging evaluation process."""
    # Required input
    packaging_concept: str = Field(description="The packaging concept to evaluate")
    concept_images: List[str] = Field(default_factory=list, description="URLs or base64 encoded images of the packaging concept")
    
    # Internal state (automatically managed)
    components: List[Component] = Field(default_factory=list)
    image_analysis: Optional[ImageAnalysis] = None
    technical_assessment: Optional[TechnicalAssessment] = None
    operational_assessment: Optional[OperationalAssessment] = None
    reflection_notes: Optional[ReflectionNotes] = None
    final_evaluation: Optional[FinalEvaluation] = None
    evaluation_score: Optional[float] = None
    final_recommendation: str = ""
    current_node: str = "image_analyzer" if concept_images else "concept_breaker"
    process_complete: bool = False
    messages: List[Dict[str, str]] = Field(default_factory=list)
    reflection_counter: int = Field(default=0, description="Number of times reflection has been performed")
    
    # Add new fields for HITL
    user_feedback: Optional[UserFeedback] = None
    feedback_iteration: int = Field(default=0, description="Number of times feedback has been requested")
    awaiting_human_input: bool = Field(default=False, description="Whether the system is waiting for human input")
    
    def add_message(self, agent: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({"agent": agent, "content": content})