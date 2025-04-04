"""Enhanced agent implementations for the packaging evaluation system."""
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.packaging_evaluation.state import (
    PackagingEvaluationState,
    Component,
    TechnicalAssessment,
    OperationalAssessment,
    ReflectionNotes,
    FinalEvaluation,
    ImageAnalysis,
    UserFeedback
)

# Initialize the GPT-4o model (which can handle both text and images)
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

class ComponentList(BaseModel):
    """A list of packaging components."""
    components: List[Component] = Field(description="List of packaging components")

async def image_analysis(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Analyzes packaging concept images using GPT-4o's multimodal capabilities.
    Extracts visual information from concept images.
    """
    # Skip if no images are provided
    if not state.concept_images:
        state.current_node = "concept_breaker"
        return state
    
    prompt = ChatPromptTemplate.from_template("""
    # Packaging Concept Image Analysis
    
    You are a specialized packaging engineer with expertise in materials, manufacturing processes, and structural design.
    You have been provided with images of a packaging concept.
    
    ## Your Task
    Analyze the packaging concept images and extract valuable information about:
    1. Visual components and their arrangement
    2. Materials that appear to be used
    3. Structural design elements
    4. Notable features and characteristics
    
    ## Packaging Concept Text Description
    {packaging_concept}
    
    ## Image Analysis Guidelines
    - Identify all visible components in the packaging
    - Assess the materials based on visual appearance
    - Note any interesting design features
    - Consider manufacturing implications of what you see
    - Look for innovative aspects or potential challenges
    
    Provide a comprehensive analysis of what you observe in the images.
    """)
    
    # Create a structured output model for image analysis
    structured_llm = llm.with_structured_output(ImageAnalysis)
    
    # Format the messages with text and images
    text_message = prompt.format_messages(packaging_concept=state.packaging_concept)[0].content
    
    # Create a list of content parts (text + images)
    content_parts = [
        {"type": "text", "text": text_message}
    ]
    
    # Add each image to the content parts
    for image_url in state.concept_images:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })
    
    # Create the message with the multi-modal content
    message = {
        "role": "user",
        "content": content_parts
    }
    
    # Run the model with structured output
    analysis = await structured_llm.ainvoke([message])
    
    # Update state with image analysis
    state.image_analysis = analysis
    
    # Add a message about the analysis
    state.add_message("image_analyzer", 
                     f"Image analysis complete. Identified {len(analysis.identified_components)} components. " + 
                     f"{analysis.analysis_summary}")
    
    # Move to next node
    state.current_node = "concept_breaker"
    
    return state

async def concept_breaker(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Breaks down the packaging concept into its components and analyzes each component.
    """
    prompt = ChatPromptTemplate.from_template("""
    # Packaging Concept Breakdown
    
    You are a specialized packaging engineer with expertise in materials, manufacturing processes, and structural design.
    
    ## Your Task
    Break down the packaging concept into its components and analyze each component.
    
    ## Packaging Concept
    {packaging_concept}
    
    ## Image Analysis (if available)
    {image_analysis}
    
    ## Guidelines
    - Identify all components of the packaging
    - For each component, specify:
      * Name
      * Material
      * Function
      * Requirements
    - Consider both visible and hidden components
    - Think about manufacturing and assembly requirements
    
    Provide a comprehensive breakdown of the packaging concept.
    """)
    
    # Create a structured output model for component list
    structured_llm = llm.with_structured_output(ComponentList)
    
    # Format the messages
    text_message = prompt.format_messages(
        packaging_concept=state.packaging_concept,
        image_analysis=state.image_analysis.analysis_summary if state.image_analysis else "No image analysis available"
    )[0].content
    
    # Create the message
    message = {
        "role": "user",
        "content": text_message
    }
    
    # Run the model with structured output
    components = await structured_llm.ainvoke([message])
    
    # Update state with components
    state.components = components.components
    
    # Add a message about the breakdown
    state.add_message("concept_breaker", 
                     f"Concept breakdown complete. Identified {len(components.components)} components.")
    
    # Move to next node
    state.current_node = "human_feedback"
    
    return state

async def human_feedback(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Request and process human feedback on component and material assumptions.
    This node pauses the evaluation for human input.
    """
    # Only request feedback if we haven't received it yet
    if state.user_feedback is None:
        # Format the current component understanding for user review
        components_summary = "\n".join([
            f"- Component: {c.name}\n  Material: {c.material}\n  Function: {c.function}\n  Requirements: {', '.join(c.requirements)}"
            for c in state.components
        ])
        
        # Create a structured prompt for user feedback
        feedback_prompt = f"""
Please review the component breakdown:

{components_summary}

Please provide feedback on:
1. Are the component identifications correct? (yes/no)
2. Are the material assumptions accurate? (yes/no)
3. Any suggested changes or improvements? (list specific changes)

Please provide your feedback in the following format:
is_correct: [yes/no]
feedback_notes: [your notes]
suggested_changes: [list of specific changes]
"""
        
        # Add message requesting feedback
        state.add_message("human_feedback", feedback_prompt)
        
        # Set state to await human input
        state.awaiting_human_input = True
        state.current_node = "human_feedback"  # Stay in this node while waiting
    else:
        # If we already have feedback, move to process_feedback
        state.current_node = "process_feedback"
    
    return state

async def process_feedback(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Process the received user feedback and determine next steps.
    """
    if not state.user_feedback:
        raise ValueError("No user feedback available to process")
    
    # Add message about received feedback
    state.add_message("feedback_processor",
                     f"Processing feedback. {'Changes requested' if not state.user_feedback.is_correct else 'Components confirmed correct'}")
    
    if state.user_feedback.is_correct:
        # If feedback confirms assumptions, proceed to technical feasibility
        state.current_node = "technical_feasibility"
    else:
        # If changes are needed, go back to concept breaker with feedback
        state.add_message("feedback_processor",
                         f"Adjusting components based on feedback: {', '.join(state.user_feedback.suggested_changes)}")
        state.current_node = "concept_breaker"
    
    # Clear the feedback to prevent loops
    state.user_feedback = None
    
    return state

async def technical_feasibility(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Assess the technical feasibility of the packaging concept.
    """
    prompt = ChatPromptTemplate.from_template("""
    # Technical Feasibility Assessment
    
    You are a specialized packaging engineer with expertise in materials, manufacturing processes, and structural design.
    
    ## Your Task
    Assess the technical feasibility of the packaging concept based on its components.
    
    ## Components
    {components}
    
    ## Guidelines
    - Evaluate each component's technical feasibility
    - Consider material properties and manufacturing processes
    - Identify potential technical challenges
    - Assess overall technical viability
    
    Provide a comprehensive technical feasibility assessment.
    """)
    
    # Create a structured output model for technical assessment
    structured_llm = llm.with_structured_output(TechnicalAssessment)
    
    # Format the components for the prompt
    components_text = "\n".join([
        f"- {c.name} (Material: {c.material}, Function: {c.function})"
        for c in state.components
    ])
    
    # Format the messages
    text_message = prompt.format_messages(components=components_text)[0].content
    
    # Create the message
    message = {
        "role": "user",
        "content": text_message
    }
    
    # Run the model with structured output
    assessment = await structured_llm.ainvoke([message])
    
    # Update state with technical assessment
    state.technical_assessment = assessment
    
    # Add a message about the assessment
    state.add_message("technical_feasibility", 
                     f"Technical feasibility assessment complete. Overall feasibility: {assessment.overall_feasible}")
    
    # Move to next node
    state.current_node = "operations"
    
    return state

async def operations(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Assess the operational impact of the packaging concept.
    """
    prompt = ChatPromptTemplate.from_template("""
    # Operational Impact Assessment
    
    You are a specialized packaging engineer with expertise in manufacturing operations and supply chain.
    
    ## Your Task
    Assess the operational impact of implementing the packaging concept.
    
    ## Components
    {components}
    
    ## Technical Assessment
    {technical_assessment}
    
    ## Guidelines
    - Evaluate supply chain impact
    - Assess production process changes needed
    - Estimate cost implications
    - Consider operational feasibility
    
    Provide a comprehensive operational impact assessment.
    """)
    
    # Create a structured output model for operational assessment
    structured_llm = llm.with_structured_output(OperationalAssessment)
    
    # Format the components and technical assessment for the prompt
    components_text = "\n".join([
        f"- {c.name} (Material: {c.material}, Function: {c.function})"
        for c in state.components
    ])
    
    technical_text = state.technical_assessment.technical_summary if state.technical_assessment else "No technical assessment available"
    
    # Format the messages
    text_message = prompt.format_messages(
        components=components_text,
        technical_assessment=technical_text
    )[0].content
    
    # Create the message
    message = {
        "role": "user",
        "content": text_message
    }
    
    # Run the model with structured output
    assessment = await structured_llm.ainvoke([message])
    
    # Update state with operational assessment
    state.operational_assessment = assessment
    
    # Add a message about the assessment
    state.add_message("operations", 
                     f"Operational impact assessment complete. Overall feasibility: {assessment.overall_feasible}")
    
    # Move to next node
    state.current_node = "reflection"
    
    return state

async def reflection(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Reflect on the assessments and determine if further iteration is needed.
    """
    # Increment reflection counter
    state.reflection_counter += 1
    
    # If we've reached the maximum number of reflections, move to final score
    if state.reflection_counter >= 3:
        state.add_message("reflection", 
                         "Maximum number of reflections reached (3). Moving to final evaluation.")
        state.current_node = "final_score"
        return state
    
    prompt = ChatPromptTemplate.from_template("""
    # Assessment Reflection
    
    You are a specialized packaging engineer reviewing the technical and operational assessments.
    
    ## Your Task
    Reflect on the assessments and identify any blind spots or areas needing further iteration.
    
    ## Technical Assessment
    {technical_assessment}
    
    ## Operational Assessment
    {operational_assessment}
    
    ## Guidelines
    - Identify potential blind spots in the assessments
    - Consider if further iteration is needed
    - Formulate questions that need to be answered
    - Make a recommendation on whether to proceed
    
    Provide a comprehensive reflection on the assessments.
    """)
    
    # Create a structured output model for reflection notes
    structured_llm = llm.with_structured_output(ReflectionNotes)
    
    # Format the assessments for the prompt
    technical_text = state.technical_assessment.technical_summary if state.technical_assessment else "No technical assessment available"
    operational_text = state.operational_assessment.operational_summary if state.operational_assessment else "No operational assessment available"
    
    # Format the messages
    text_message = prompt.format_messages(
        technical_assessment=technical_text,
        operational_assessment=operational_text
    )[0].content
    
    # Create the message
    message = {
        "role": "user",
        "content": text_message
    }
    
    # Run the model with structured output
    reflection = await structured_llm.ainvoke([message])
    
    # Update state with reflection notes
    state.reflection_notes = reflection
    
    # Add a message about the reflection
    state.add_message("reflection", 
                     f"Reflection {state.reflection_counter}/3 complete. Requires iteration: {reflection.requires_iteration}")
    
    # Determine next node based on reflection
    if reflection.requires_iteration and state.reflection_counter < 3:
        if reflection.questions:
            state.current_node = "technical_feasibility"
        else:
            state.current_node = "operations"
    else:
        state.current_node = "final_score"
    
    return state

async def final_score(state: PackagingEvaluationState) -> PackagingEvaluationState:
    """
    Generate the final evaluation score and recommendations.
    """
    prompt = ChatPromptTemplate.from_template("""
    # Final Evaluation
    
    You are a specialized packaging engineer providing the final evaluation of the concept.
    
    ## Your Task
    Generate a final evaluation score and recommendations based on all assessments.
    
    ## Technical Assessment
    {technical_assessment}
    
    ## Operational Assessment
    {operational_assessment}
    
    ## Reflection Notes
    {reflection_notes}
    
    ## Guidelines
    - Provide an overall feasibility score (1-10)
    - Summarize key strengths and challenges
    - Make specific improvement recommendations
    - Provide a clear go/no-go decision
    - List action items for next steps
    
    Provide a comprehensive final evaluation.
    """)
    
    # Create a structured output model for final evaluation
    structured_llm = llm.with_structured_output(FinalEvaluation)
    
    # Format the assessments and reflection for the prompt
    technical_text = state.technical_assessment.technical_summary if state.technical_assessment else "No technical assessment available"
    operational_text = state.operational_assessment.operational_summary if state.operational_assessment else "No operational assessment available"
    reflection_text = state.reflection_notes.reflection_summary if state.reflection_notes else "No reflection notes available"
    
    # Format the messages
    text_message = prompt.format_messages(
        technical_assessment=technical_text,
        operational_assessment=operational_text,
        reflection_notes=reflection_text
    )[0].content
    
    # Create the message
    message = {
        "role": "user",
        "content": text_message
    }
    
    # Run the model with structured output
    evaluation = await structured_llm.ainvoke([message])
    
    # Update state with final evaluation
    state.final_evaluation = evaluation
    state.evaluation_score = evaluation.feasibility_score
    state.final_recommendation = evaluation.executive_summary
    state.process_complete = True
    
    # Add a message about the final evaluation
    state.add_message("final_score", 
                     f"Final evaluation complete. Score: {evaluation.feasibility_score}/10. "
                     f"Go decision: {evaluation.go_decision}")
    
    return state


