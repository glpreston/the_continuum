# continuum/actors/base_llm_actor.py
from continuum.core.logger import log_debug, log_error
import os


class BaseLLMActor:
    def __init__(
        self,
        name,
        prompt_file,
        persona,
        system_prompt,
        temperature,
        max_tokens,
        controller,
    ):
        self.name = name
        self.prompt_file = prompt_file
        self.persona = persona
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.controller = controller

    # ---------------------------------------------------------
    # Load persona prompt from /actors/prompts/
    # ---------------------------------------------------------
    def load_persona_prompt(self):
        base = os.path.join(os.path.dirname(__file__), "prompts")
        path = os.path.join(base, self.prompt_file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"[ERROR: could not load persona prompt {self.prompt_file}: {e}]"

    # ---------------------------------------------------------
    # Modernized LLM execution (Router-driven)
    # ---------------------------------------------------------
    def _run_llm(
        self,
        context,
        message,
        controller,
        temperature,
        max_tokens,
        system_prompt,
        memory,
        emotional_state,
        voiceprint,
        metadata,
        telemetry,
        routing=None,   # ⭐ NEW
    ):
        """
        Modernized LLM execution path.

        Uses per‑actor routing when provided.
        """

        # ⭐ Prefer per‑actor routing from Senate
        routing = routing or controller.last_routing_decision

        if not routing:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] No routing decision available."
            )

        # ---------------------------------------------------------
        # 1. Extract model + node from routing
        # ---------------------------------------------------------
        model_info = routing.get("model_selection", {})
        node_info = routing.get("node_selection", {})

        model_name = model_info.get("selected_model")
        if not model_name:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] Routing decision missing selected_model."
            )

        node = node_info.get("selected_node")
        if not node:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] Routing decision missing selected_node."
            )

        host = node.get("host")
        port = node.get("port")
        if not host:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] Routing decision missing host."
            )

        # Build endpoint
        if host.startswith("http://") or host.startswith("https://"):
            base = host.rstrip("/")
            if port and ":" not in base.split("//", 1)[1]:
                base = f"{base}:{port}"
        else:
            base = f"http://{host}"
            if port:
                base = f"{base}:{port}"

        endpoint = f"{base}/api/generate"

        # Load persona prompt
        persona_prompt = self.load_persona_prompt()

        # Build final prompt
        prompt = (
            f"{self.system_prompt}\n\n"
            f"{persona_prompt}\n\n"
            f"User: {message}"
        )

        # Override LLMClient endpoint
        original_endpoint = controller.llm_client.endpoint
        controller.llm_client.endpoint = endpoint

        try:
            response = controller.llm_client.generate(
                prompt=prompt,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        finally:
            controller.llm_client.endpoint = original_endpoint

        return response

        # ---------------------------------------------------------
        # respond() used by Fusion
        # ---------------------------------------------------------
        def respond(self, prompt: str, **kwargs) -> str:
            return prompt

    # ---------------------------------------------------------
    # Safe reasoning summary (for Senate UI/debug)
    # ---------------------------------------------------------
    def summarize_reasoning(self, proposal: dict) -> str:
        persona = self.persona
        if isinstance(persona, dict):
            style = persona.get("style") or persona.get("role") or "general"
            goal = persona.get("goal") or "provide helpful guidance"
        else:
            style = str(persona) if persona else "general"
            goal = "provide helpful guidance"

        return (
            f"This proposal reflects the actor's style of {style}, "
            f"aimed at {goal}. It focuses on key elements the actor "
            f"considers most relevant to the user's message."
        )

    # ---------------------------------------------------------
    # Phase‑5 propose() — unified entrypoint for all LLM actors
    # ---------------------------------------------------------
    def propose(
        self,
        context,
        message,
        controller,
        memory,
        emotional_state,
        emotional_memory,
        voiceprint,
        metadata,
        telemetry,
        routing=None,            # ⭐ NEW
    ):
        """
        routing:
        - Provided by Senate (per‑actor routing)
        - Falls back to controller.last_routing_decision if missing
        """

        # ⭐ Prefer per‑actor routing from Senate
        routing = routing or controller.last_routing_decision

        if not routing:
            return {
                "actor": self.name,
                "content": None,
                "confidence": 0.0,
                "metadata": {
                    "type": "error",
                    "error": "No routing decision available.",
                },
            }

        try:
            raw = self._run_llm(
                context=context,
                message=message,
                controller=controller,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                system_prompt=self.system_prompt,
                memory=memory,
                emotional_state=emotional_state,
                voiceprint=voiceprint,
                metadata=metadata,
                telemetry=telemetry,
                routing=routing,
                # ⭐ Pass routing into _run_llm
                # (we will update _run_llm next)
            )

            # Normalize into Senate-friendly proposal format
            if isinstance(raw, dict):
                content = raw.get("text")
                confidence = raw.get("confidence", 1.0)
            else:
                content = str(raw)
                confidence = 1.0

            if not content or not str(content).strip():
                content = "[ERROR] LLM returned empty response."
                confidence = 0.1

            if isinstance(content, str) and content.startswith("[ERROR]"):
                confidence = min(confidence, 0.1)

            return {
                "actor": self.name,
                "content": content,
                "confidence": confidence,
                "metadata": {
                    "raw_response": raw,
                    "persona": self.persona,
                },
            }

        except Exception as e:
            log_error(f"[BaseLLMActor:{self.name}] ERROR in propose(): {e}", phase="actors")
            return {
                "actor": self.name,
                "content": None,
                "confidence": 0.0,
                "metadata": {
                    "type": "error",
                    "error": str(e),
                },
            }

