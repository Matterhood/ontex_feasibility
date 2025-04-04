"""Graph definition for the packaging evaluation system."""
from langgraph.graph import StateGraph, END
from src.packaging_evaluation.state import PackagingEvaluationState
from src.packaging_evaluation.tools import (
    image_analysis,
    concept_breaker,
    human_feedback,
    process_feedback,
    technical_feasibility,
    operations,
    reflection,
    final_score
)

# Initialize the graph
graph = StateGraph(PackagingEvaluationState)

# Add all nodes
graph.add_node("image_analyzer", image_analysis)
graph.add_node("concept_breaker", concept_breaker)
graph.add_node("human_feedback", human_feedback)
graph.add_node("process_feedback", process_feedback)
graph.add_node("technical_feasibility", technical_feasibility)
graph.add_node("operations", operations)
graph.add_node("reflection", reflection)
graph.add_node("final_score", final_score)

# Define the conditional router
def router(state: PackagingEvaluationState):
    if state.process_complete:
        return END
    if state.awaiting_human_input:
        return state.current_node
    return state.current_node

# Connect nodes with conditional edges
graph.add_conditional_edges(
    "image_analyzer",
    router,
    {
        "concept_breaker": "concept_breaker",
    }
)

graph.add_conditional_edges(
    "concept_breaker",
    router,
    {
        "human_feedback": "human_feedback",
    }
)

graph.add_conditional_edges(
    "human_feedback",
    router,
    {
        "human_feedback": "human_feedback",  # Stay in this node while awaiting input
        "process_feedback": "process_feedback",  # Move to process_feedback when input received
    }
)

graph.add_conditional_edges(
    "process_feedback",
    router,
    {
        "concept_breaker": "concept_breaker",  # If changes needed
        "technical_feasibility": "technical_feasibility",  # If approved
    }
)

graph.add_conditional_edges(
    "technical_feasibility",
    router,
    {
        "operations": "operations",
    }
)

graph.add_conditional_edges(
    "operations",
    router,
    {
        "reflection": "reflection",
    }
)

graph.add_conditional_edges(
    "reflection",
    router,
    {
        "technical_feasibility": "technical_feasibility",
        "operations": "operations",
        "final_score": "final_score",
    }
)

graph.add_conditional_edges(
    "final_score",
    router,
    {
        END: END
    }
)

# Set the entry point
graph.set_entry_point("image_analyzer")