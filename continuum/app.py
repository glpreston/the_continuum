# continuum/app.py

from fastapi import FastAPI

# Memory + Controller
from continuum.memory.mysql_backend import MySQLMemoryBackend
from continuum.memory.mysql_memory import MySQLEpisodicMemory, MySQLSemanticMemory
from continuum.core.context import ContinuumContext
from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.orchestrator.senate import Senate
from continuum.orchestrator.jury import Jury
from continuum.actors.base_actor import BaseActor
from continuum.config.personas import ACTOR_PROFILES

# API Routers
from continuum.api.nodes import router as nodes_router

# Scheduler
from continuum.monitoring.model_sync_scheduler import start_scheduler

import sys
print("Loaded modules:", list(sys.modules.keys()))


# ---------------------------------------------------------
# Initialize Memory Backend
# ---------------------------------------------------------

backend = MySQLMemoryBackend(
    host="192.168.50.114",
    port=3306,
    user="hal",
    password="Hal@2025!",
    database="aira_config",
)
backend.ensure_schema()

episodic = MySQLEpisodicMemory(backend)
semantic = MySQLSemanticMemory(backend)


# ---------------------------------------------------------
# Initialize Controller
# ---------------------------------------------------------

#actors = [BaseActor(id=k, profile=v) for k, v in ACTOR_PROFILES.items()]
#controller = ContinuumController(senate=Senate(actors), jury=Jury())

# 3. Build controller
actors = [BaseActor(name=k, persona=v) for k, v in ACTOR_PROFILES.items()]
#controller = ContinuumController()
controller = None

def get_controller():
    global controller
    if controller is None:
        controller = ContinuumController()
    return controller
# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI()

# Register API routes
app.include_router(nodes_router)


# ---------------------------------------------------------
# Background Scheduler
# ---------------------------------------------------------

start_scheduler()


# ---------------------------------------------------------
# Optional: expose controller for future API endpoints
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Continuum backend running"}