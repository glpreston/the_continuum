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

        # 2. Select model candidates
        model_selection = self.model_selector.select_models(
            intent_name=intent_result.intent,
            actor_name=actor_name,
        )

        if not model_selection["candidates"]:
            raise RuntimeError(
                f"[Router] No model candidates for intent '{intent_result.intent}'"
            )

        # 3. Select node for top model
        top_model = model_selection["candidates"][0]["model"]
        node_selection = self.node_selector.select_node(top_model)

        result = {
            "intent": intent_result.intent,
            "intent_confidence": intent_result.confidence,
            "matched_alias": intent_result.matched_alias,
            "raw_text": intent_result.raw_text or user_text,
            "actor_name": actor_name,
            "model_selection": model_selection,
            "node_selection": node_selection,
            "extra_context": extra_context,
        }

        self._log("info", f"[Router] Final routing decision: {result}")
        return result