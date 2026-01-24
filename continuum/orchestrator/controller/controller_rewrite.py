# continuum/orchestrator/controller/controller_rewrite.py

from continuum.core.logger import log_error, log_debug


def meta_rewrite_llm(controller, core_text: str, emotional_state: dict) -> str:
    """
    Meta‑Persona rewrite layer.
    Applies a light, grounded rewrite that preserves meaning and technical detail.
    """

    try:
        # Use the first registered model (same one actors use)
        model_info = next(iter(controller.registry.models.values()))
        model = model_info.node

        # Balanced rewrite prompt — preserves meaning and technical content
        prompt = (
            "Rewrite the following text in a clear, grounded, human tone.\n"
            "Do not add metaphors, imagery, or emotional commentary.\n"
            "Do not soften or replace technical or factual content.\n"
            "Preserve all instructions, details, and meaning exactly.\n"
            "Your job is only to:\n"
            "- smooth phrasing\n"
            "- remove redundancy\n"
            "- unify voice\n"
            "- keep it concise and readable\n"
            "\n"
            "Do not explain your changes.\n"
            "Do not add notes, comments, or analysis about the text or your edits.\n"
            "Write only the rewritten text itself.\n"
            "\n"
            "If the text is technical, keep it technical.\n"
            "If the text is emotional, keep it emotionally aware but not poetic.\n"
            "\n"
            f"Text:\n{core_text}\n\n"
            "Rewrite:"
        )

        # ---------------------------------------------------------
        # FIX: Accumulate streamed output instead of taking 1 chunk
        # ---------------------------------------------------------
        raw = model.generate(prompt=prompt, max_tokens=300)

        # If the model streams (generator, list of chunks, etc.)
        if hasattr(raw, "__iter__") and not isinstance(raw, str):
            text = ""
            for chunk in raw:
                # Ollama-style: {"response": "..."}
                if isinstance(chunk, dict) and "response" in chunk:
                    text += chunk["response"]
                # LM Studio / OpenAI-style: {"choices":[{"text": "..."}]}
                elif isinstance(chunk, dict) and "choices" in chunk:
                    text += chunk["choices"][0].get("text", "")
                else:
                    text += str(chunk)
            rewritten = text.strip()
        else:
            # Non-streaming clients return a full string
            rewritten = raw.strip()

        # ---------------------------------------------------------
        # Guardrail: prevent useless or generic assistant replies
        # ---------------------------------------------------------
        bad_responses = {
            "i can do that.",
            "sure, i can do that.",
            "i can help with that.",
            "how can i assist you?",
            "i can help.",
            "let me help you with that.",
            "i can assist with that.",
        }

        normalized = rewritten.lower().strip()

        if normalized in bad_responses or len(rewritten.split()) <= 3:
            log_error("[META-REWRITE] Low-value rewrite, falling back to original", phase="meta")
            return core_text

        log_debug("[META-REWRITE] LLM rewrite complete", phase="meta")
        return rewritten

    except Exception as e:
        log_error(f"[META-REWRITE] Error during rewrite: {e}", phase="meta")
        return core_text