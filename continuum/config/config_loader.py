import logging
from continuum.db.mysql_connection import MySQLConfigDB


class ConfigLoader:
    """
    Loads all configuration data for Aira from the MySQL configuration database.
    Produces structured dictionaries ready for the ContinuumController.
    """

    def __init__(self, db: MySQLConfigDB):
        self.db = db
        self.logger = logging.getLogger("ConfigLoader")

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def load_all(self):
        """
        Load all configuration domains at once.
        Returns a dictionary with all config sections.
        """
        self.logger.info("Loading configuration from database...")

        return {
            "nodes": self.load_nodes(),
            "actors": self.load_actors(),
            "models": self.load_models(),
            "system_settings": self.load_system_settings(),
            "persona_presets": self.load_persona_presets(),
        }

    # ---------------------------------------------------------
    # Domain loaders
    # ---------------------------------------------------------

    def load_nodes(self):
        rows = self.db.load_nodes()
        nodes = {}

        for row in rows:
            nodes[row["id"]] = {
                "hostname": row["hostname"],
                "endpoint": row["endpoint"],
                "models": row["models_json"],
                "status": row["status"],
                "last_heartbeat": row["last_heartbeat"],
            }

        self.logger.info(f"Loaded {len(nodes)} nodes")
        return nodes

    def load_actors(self):
        rows = self.db.load_actors()
        actors = {}

        for row in rows:
            actors[row["name"]] = {
                "default_model": row["default_model"],
                "fallback_model": row["fallback_model"],
                "personality": row["personality_json"],
            }

        self.logger.info(f"Loaded {len(actors)} actors")
        return actors

    def load_models(self):
        rows = self.db.load_models()
        models = {}

        for row in rows:
            models[row["name"]] = {
                "provider": row["provider"],
                "context_window": row["context_window"],
                "temperature_default": row["temperature_default"],
            }

        self.logger.info(f"Loaded {len(models)} models")
        return models

    def load_system_settings(self):
        settings = self.db.load_system_settings()
        self.logger.info(f"Loaded {len(settings)} system settings")
        return settings

    def load_persona_presets(self):
        rows = self.db.load_persona_presets()
        presets = {}

        for row in rows:
            presets[row["name"]] = row["config_json"]

        self.logger.info(f"Loaded {len(presets)} persona presets")
        return presets
    