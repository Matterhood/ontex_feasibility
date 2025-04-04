"""Configuration for the packaging evaluation system."""

# Agent configuration
AGENT_CONFIG = {
    "image_analyzer": {
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "concept_breaker": {
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "technical_feasibility": {
        "model": "gpt-4o",
        "temperature": 0.2,
        "use_rag": True
    },
    "operations": {
        "model": "gpt-4o",
        "temperature": 0.2,
        "use_rag": True
    },
    "reflection": {
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "final_score": {
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "human_feedback": {
        "model": "gpt-4o",
        "temperature": 0.1
    },
    "process_feedback": {
        "model": "gpt-4o",
        "temperature": 0.1
    }
}

# Graph configuration
GRAPH_CONFIG = {
    "max_iterations": 10,
    "timeout": 300  # seconds
}
