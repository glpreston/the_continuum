# continuum/orchestrator/router/router.py

from typing import Optional, Dict, Any

from continuum.core.logger import logger, log_debug, log_error, log_info

from continuum.orchestrator.router.intent_classifier_contract import (
    IntentClassifierContract,
    IntentResult,
)

from continuum.orchestrator.router.model_selector_v2 import ModelSelectorV2
from continuum.orchestrator.router.node_selector_v2 import NodeSelectorV2


class Router:
    """
    High-level routing spine:

        user_text → IntentClassifier → ModelSelectorV2 → NodeSelectorV2

    This class does not execute the model; it only decides:
    - which intent is active
    - which model to use
    - which node to send it to
    """

    def __init__(
        self,
        intent_classifier: IntentClassifierContract,
        db_conn=None,
        logger_instance=None,
    ):
        # DB + logger wiring
        self.db = db_conn
        self.logger = logger_instance or logger

        # Core components
        self.intent_classifier = intent_classifier
        self.model_selector = ModelSelectorV2(self.db, logger=self._log)
        self.node_selector = NodeSelectorV2(self.db, logger=self._log)

    # -------------------------
    # Internal logging adapter
    # -------------------------
    def _log(self, level: str, message: str):
        if not self.logger:
            return

        level = level.lower()
        if level == "info":
            self.logger.info(message)
        elif level in ("warn", "warning"):
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.debug(message)

    # -------------------------
    # Dynamic node selection
    # -------------------------
    def _pick_best_node(self, node_selection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace the selected_node with a dynamically chosen one,
        but preserve all other fields returned by NodeSelectorV2.
        """

        nodes = node_selection.get("available_nodes") or node_selection.get("candidate_nodes") or []
        if not nodes:
            return node_selection  # nothing to choose from

        import random
        chosen = random.choice(nodes)

        # Preserve all original fields, only replace selected_node
        updated = dict(node_selection)
        updated["selected_node"] = chosen

        return updated

        # -------------------------
        # Public routing API
        # -------------------------
    def route(
        self,
        user_text: str,
        actor_name: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        extra_context = extra_context or {}

        # 1. Classify intent
        intent_result: IntentResult = self.intent_classifier.classify(user_text)
        self._log("info", f"[Router] Intent classified: {intent_result}")

        # 2. Select model (Phase‑5: DB-driven, node-aware)
        routing_decision = self.model_selector.select_models(
            intent_name=intent_result.intent,
            actor_name=actor_name,
        )

        if not routing_decision:
            raise RuntimeError(
                f"[Router] ModelSelectorV2 could not resolve a model for actor '{actor_name}'"
            )

        top_model = routing_decision.model
        required_memory_gb = routing_decision.required_memory_gb

        # 3. Select node for the chosen model
        node_selection = self.node_selector.select_node(
            top_model,
            required_memory_gb,
        )

        if not node_selection.get("selected_node"):
            raise RuntimeError(
                f"[Router] No available nodes for model '{top_model}' "
                f"(required_memory_gb={required_memory_gb})"
            )

        # 4. Optional dynamic node selection
        node_selection = self._pick_best_node(node_selection)

        result = {
            "intent": intent_result.intent,
            "intent_confidence": intent_result.confidence,
            "matched_alias": intent_result.matched_alias,
            "raw_text": intent_result.raw_text or user_text,
            "actor_name": actor_name,
            "model_selection": {
                "selected_model": top_model,
                "selected_model_required_memory_gb": required_memory_gb,
            },
            "node_selection": node_selection,
            "extra_context": extra_context,
        }

        self._log("info", f"[Router] Final routing decision: {result}")
        return result