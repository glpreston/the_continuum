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
    ):
        """
        Modernized LLM execution path.

        Uses:
          - controller.last_routing_decision["model_selection"]
          - controller.last_routing_decision["node_selection"]

        Legacy model_selector/node_selector are no longer used.
        """

        routing = controller.last_routing_decision
        if not routing:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] No routing decision available. "
                f"Router must run before actor execution."
            )

        # ---------------------------------------------------------
        # 1. Extract model + node from routing
        # ---------------------------------------------------------
        model_info = routing.get("model_selection", {})
        node_info = routing.get("node_selection", {})

        # Top model chosen by ModelSelectorV2
        model_name = model_info["candidates"][0]["model"]

        # Selected node chosen by NodeSelectorV2
        node = node_info.get("selected_node")
        if not node:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] Routing decision missing selected_node."
            )

        # Build endpoint (robust to host already containing scheme/port)
        host = node.get("host")
        port = node.get("port")
        if not host:
            raise RuntimeError(
                f"[BaseLLMActor:{self.name}] Routing decision missing host."
            )

        if host.startswith("http://") or host.startswith("https://"):
            base = host.rstrip("/")
            if port:
                # Avoid duplicating port if already included in host
                if ":" not in base.split("//", 1)[1]:
                    base = f"{base}:{port}"
        else:
            base = f"http://{host}"
            if port:
                base = f"{base}:{port}"

        endpoint = f"{base}/api/generate"

        # ---------------------------------------------------------
        # 2. Load persona prompt
        # ---------------------------------------------------------
        persona_prompt = self.load_persona_prompt()

        # ---------------------------------------------------------
        # 3. Build final prompt
        # ---------------------------------------------------------
        prompt = (
            f"{self.system_prompt}\n\n"
            f"{persona_prompt}\n\n"
            f"User: {message}"
        )

        # ---------------------------------------------------------
        # 4. Override LLMClient endpoint
        # ---------------------------------------------------------
        original_endpoint = controller.llm_client.endpoint
        controller.llm_client.endpoint = endpoint

        log_debug(
            f"[ACTOR EXECUTION] {self.name} using model={model_name} endpoint={endpoint}",
            phase="actors"
        )

        # ---------------------------------------------------------
        # 5. Execute LLM call
        # ---------------------------------------------------------
        try:
            response = controller.llm_client.generate(
                prompt=prompt,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                endpoint=endpoint,   # ⭐ ADD THIS
            )
        finally:
            # Restore original endpoint
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
        """
        Provide a safe, non-chain-of-thought explanation for UI/debug.
        """
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
    ):
        """
        Phase‑5 unified propose() method.

        Delegates to _run_llm(), using:
          - router-selected model
          - router-selected node
          - actor's own system_prompt, temperature, max_tokens
        """

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