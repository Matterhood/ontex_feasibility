"""Utility functions for the packaging evaluation system."""
import json
from src.packaging_evaluation.state import PackagingEvaluationState

def format_evaluation_results(state: PackagingEvaluationState) -> str:
    """Format the evaluation results into a readable string."""
    result = "\n=== PACKAGING EVALUATION RESULTS ===\n"
    result += f"Concept: {state.packaging_concept}\n"
    result += f"Score: {state.final_score:.2f}/1.0\n"
    result += f"Recommendation: {state.final_recommendation}\n\n"
    
    result += "=== COMPONENTS ===\n"
    for component in state.components:
        result += f"- {component['name']} ({component['material']}): {component['function']}\n"
    
    result += "\n=== TECHNICAL ASSESSMENT ===\n"
    result += f"Overall: {'Feasible' if state.technical_assessment.get('overall_feasible', False) else 'Not Feasible'}\n"
    
    result += "\n=== OPERATIONAL ASSESSMENT ===\n"
    result += f"Supply Chain Impact: {state.operational_assessment.get('supply_chain_impact', 'Unknown')}\n"
    result += f"Cost Impact: {state.operational_assessment.get('cost_impact', 'Unknown')}\n"
    
    result += "\n=== REFLECTION NOTES ===\n"
    if state.reflection_notes.get('blind_spots'):
        result += "Blind Spots:\n"
        for spot in state.reflection_notes.get('blind_spots', []):
            result += f"- {spot}\n"
    
    result += "\n=== AGENT MESSAGES ===\n"
    for msg in state.messages:
        result += f"[{msg['agent']}] {msg['content']}\n"
    
    return result

def save_evaluation_to_json(state: PackagingEvaluationState, filename: str) -> None:
    """Save evaluation results to a JSON file."""
    data = {
        "concept": state.packaging_concept,
        "score": state.final_score,
        "recommendation": state.final_recommendation,
        "components": state.components,
        "technical_assessment": state.technical_assessment,
        "operational_assessment": state.operational_assessment,
        "reflection_notes": state.reflection_notes,
        "messages": state.messages
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
