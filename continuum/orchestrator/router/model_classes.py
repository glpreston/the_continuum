# continuum/orchestrator/router/model_classes.py

"""
Declarative model classes: actors ask for these by name,
and the router expands them into concrete models.
"""

MODEL_CLASSES = {

    # ---------------------------------------------------------
    # Small, fast, cheap models (Greeter, chitchat, intent)
    # ---------------------------------------------------------
    "general-small": [
        "qwen3:4b",
        "gemma3:4b",
        "llama3.1:latest",
        "llama3:latest",
    ],

    # ---------------------------------------------------------
    # Creative writing / narrative
    # ---------------------------------------------------------
    "creative-small": [
        "qwen3:4b",
        "gemma3:4b",
        "mistral-openorca:latest",
    ],

    # ---------------------------------------------------------
    # Coding / synthesis
    # ---------------------------------------------------------
    "code-small": [
        "codellama:latest",
        "qwen2.5-coder:latest",
    ],

    # ---------------------------------------------------------
    # Reasoning / analysis
    # ---------------------------------------------------------
    "reasoning-medium": [
        "deepseek-r1:latest",
        "deepseek-r1:8b",
        "glm-4.6:cloud",
    ],

    # ---------------------------------------------------------
    # General-purpose conversation (Architect default)
    # ---------------------------------------------------------
    "general-medium": [
        "llama4:16x17b",
        "gpt-oss:20b",
        "llama3.2:latest",
        "qwen3:4b",
    ],
}