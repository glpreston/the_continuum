# continuum/orchestrator/router/model_selector_v2.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from sqlalchemy import text


@dataclass
class RoutingDecision:
    actor: str
    intent: str
    model: str
    node: str
    required_memory_gb: float


class ModelSelectorV2:
    """
    DB-driven model + node selector.

    - Reads models, nodes, and model_nodes from the DB
    - Uses actor defaults / fallbacks (from controller)
    - Applies health + memory filters
    - Ranks nodes using a hybrid strategy:
        * actor-specific node preferences
        * health_score
        * available_memory_gb
        * latency_ms (if present)
    """

    def __init__(
        self,
        db,
        actor_defaults: Dict[str, str],
        actor_fallbacks: Dict[str, str],
        min_health_threshold: float = 0.0,
        logger=None,
    ):
        self.db = db
        self.actor_defaults = actor_defaults or {}
        self.actor_fallbacks = actor_fallbacks or {}
        self.min_health_threshold = min_health_threshold

        # logger should be something like logger.info or a simple callable
        self.logger = logger

        # Hybrid: actor → preferred nodes (can later be DB-driven)
        self.actor_node_preferences = self._load_actor_node_preferences()

    # -------------------------------------------------------------------------
    # Logging helper
    # -------------------------------------------------------------------------

    def _log(self, msg: str):
        if self.logger:
            try:
                self.logger(msg)
            except TypeError:
                # In case logger is a bound method expecting (msg)
                self.logger(msg)

    # -------------------------------------------------------------------------
    # Actor → node preferences (hybrid personality layer)
    # -------------------------------------------------------------------------

    def _load_actor_node_preferences(self) -> Dict[str, List[str]]:
        """
        Hybrid mode:
        - For now, hardcode actor→node preferences.
        - Later, this can be loaded from a table like `actor_node_preferences`.
        """
        return {
            "Greeter": ["Gamer", "Netty", "myplex"],
            "Storyweaver": ["Gamer", "Netty", "myplex"],
            "Analyst": ["Netty", "myplex", "Gamer"],
            "Synthesizer": ["Gamer", "myplex", "Netty"],
            "Architect": ["myplex", "Netty", "Gamer"],
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def select_models(
        self,
        intent_name: str,
        actor_name: str,
        require_vision: bool = False,
    ) -> Optional[RoutingDecision]:
        """
        Main entry point.

        Returns a RoutingDecision with:
          - actor
          - intent
          - model
          - node
          - required_memory_gb
        """
        return self._resolve_model_for_actor(
            actor_name=actor_name,
            intent_name=intent_name,
            require_vision=require_vision,
        )

    # -------------------------------------------------------------------------
    # Core resolution logic
    # -------------------------------------------------------------------------

    def _resolve_model_for_actor(
        self,
        actor_name: str,
        intent_name: str,
        require_vision: bool = False,
    ) -> Optional[RoutingDecision]:
        """
        Resolve a model + node for a given actor and intent.
        """

        # 1. Load live model instances from DB
        live = self._load_live_models(require_vision=require_vision)
        if not live:
            self._log("[ModelSelectorV2] No live models found in DB")
            return None

        # 2. Determine the target model name (class or concrete)
        target_model = self.actor_defaults.get(actor_name)
        fallback_model = self.actor_fallbacks.get(actor_name)

        if not target_model and fallback_model:
            target_model = fallback_model

        if not target_model:
            # As a last resort, pick any healthy model
            self._log(
                f"[ModelSelectorV2] No default/fallback model for actor '{actor_name}', "
                "falling back to any healthy model."
            )
            candidates = [m for m in live if m["health_score"] >= self.min_health_threshold]
        else:
            # Filter by target model name
            candidates = [
                m
                for m in live
                if m["model_name"] == target_model
                and m["health_score"] >= self.min_health_threshold
            ]

            # If no candidates for default, try fallback
            if not candidates and fallback_model:
                self._log(
                    f"[ModelSelectorV2] No live instances for default model '{target_model}' "
                    f"for actor '{actor_name}', trying fallback '{fallback_model}'."
                )
                candidates = [
                    m
                    for m in live
                    if m["model_name"] == fallback_model
                    and m["health_score"] >= self.min_health_threshold
                ]

            # If still nothing, fall back to any healthy model
            if not candidates:
                self._log(
                    f"[ModelSelectorV2] No live instances for default/fallback models "
                    f"for actor '{actor_name}', falling back to any healthy model."
                )
                candidates = [m for m in live if m["health_score"] >= self.min_health_threshold]

        if not candidates:
            self._log(
                f"[ModelSelectorV2] No candidates available for actor '{actor_name}' "
                f"and intent '{intent_name}' after filtering."
            )
            return None

        # 3. Rank candidates using hybrid node preferences
        ranked = self._rank_nodes_for_actor(actor_name, candidates)
        chosen = ranked[0]

        decision = RoutingDecision(
            actor=actor_name,
            intent=intent_name,
            model=chosen["model_name"],
            node=chosen["node_name"],
            required_memory_gb=chosen.get("required_memory_gb", 0.0),
        )

        self._log(
            f"[ModelSelectorV2] Selected model '{decision.model}' on node '{decision.node}' "
            f"for actor '{actor_name}' and intent '{intent_name}'"
        )

        return decision

    # -------------------------------------------------------------------------
    # Node ranking (hybrid: actor prefs + performance)
    # -------------------------------------------------------------------------

    def _rank_nodes_for_actor(
        self,
        actor_name: str,
        candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Hybrid ranking:
        1. Actor-specific node preferences (if any)
        2. Health score (desc)
        3. Available memory (desc)
        4. Latency (asc, if present)
        5. Node name (asc)
        """

        prefs = self.actor_node_preferences.get(actor_name, [])

        def node_pref_index(node_name: str) -> int:
            if node_name in prefs:
                return prefs.index(node_name)
            # If not in prefs, push it to the end
            return len(prefs) + 1

        def sort_key(entry: Dict[str, Any]):
            node = entry["node_name"]
            health = entry.get("health_score", 1.0) or 1.0
            mem = entry.get("available_memory_gb", 0.0) or 0.0
            latency = entry.get("latency_ms", 9999.0) or 9999.0

            return (
                node_pref_index(node),   # actor preference
                -health,                 # higher health first
                -mem,                    # more memory first
                latency,                 # lower latency first
                node,                    # stable tie-breaker
            )

        ranked = sorted(candidates, key=sort_key)
        self._log(
            f"[ModelSelectorV2] Ranked {len(candidates)} candidates for actor '{actor_name}': "
            + ", ".join(f"{c['node_name']}:{c['model_name']}" for c in ranked)
        )
        return ranked

    # -------------------------------------------------------------------------
    # DB access: live models
    # -------------------------------------------------------------------------

    def _load_live_models(self, require_vision: bool = False) -> List[Dict[str, Any]]:
        """
        Load live model instances from DB.

        Expected schema (adjust if needed):

        - models(id, name, is_vision, required_memory_gb, ...)
        - nodes(id, name, host, ...)
        - model_nodes(model_id, node_id)
        - node_health(node_name, health_score, available_memory_gb, latency_ms, ...)

        Returns a list of dicts:
          {
            "model_name": str,
            "node_name": str,
            "health_score": float,
            "available_memory_gb": float,
            "latency_ms": float,
            "required_memory_gb": float,
          }
        """

        sql = """
        SELECT
            m.name AS model_name,
            n.name AS node_name,
            COALESCE(h.health_score, 1.0) AS health_score,
            COALESCE(h.available_memory_gb, 0.0) AS available_memory_gb,
            COALESCE(h.latency_ms, 9999.0) AS latency_ms,
            COALESCE(m.required_memory_gb, 0.0) AS required_memory_gb,
            COALESCE(m.is_vision, 0) AS is_vision
        FROM model_nodes mn
        JOIN models m ON m.id = mn.model_id
        JOIN nodes n ON n.id = mn.node_id
        LEFT JOIN node_health h ON h.node_id = n.id
        """

        rows = self.db.execute(text(sql)).mappings().all()

        live: List[Dict[str, Any]] = []
        for r in rows:
            if require_vision and not bool(r["is_vision"]):
                continue

            live.append(
                {
                    "model_name": r["model_name"],
                    "node_name": r["node_name"],
                    "health_score": float(r["health_score"]),
                    "available_memory_gb": float(r["available_memory_gb"]),
                    "latency_ms": float(r["latency_ms"]),
                    "required_memory_gb": float(r["required_memory_gb"]),
                }
            )

        self._log(f"[ModelSelectorV2] Loaded {len(live)} live model instances")
        return live