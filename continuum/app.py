from continuum.memory.mysql_backend import MySQLMemoryBackend
from continuum.memory.mysql_memory import MySQLEpisodicMemory, MySQLSemanticMemory
from continuum.core.context import ContinuumContext
from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.orchestrator.senate import Senate
from continuum.orchestrator.jury import Jury
from continuum.actors.base_actor import BaseActor
from continuum.config.personas import ACTOR_PROFILES
import uuid

# 1. Create backend
backend = MySQLMemoryBackend(
    host="localhost",
    port=3306,
    user="hal",
    password="Hal@2025!",
    database="continuum",
)
backend.ensure_schema()

# 2. Create memory layers
episodic = MySQLEpisodicMemory(backend)
semantic = MySQLSemanticMemory(backend)

# 3. Build controller
actors = [BaseActor(id=k, profile=v) for k, v in ACTOR_PROFILES.items()]
controller = ContinuumController(senate=Senate(actors), jury=Jury())

# 4. Create context
context = ContinuumContext(conversation_id=str(uuid.uuid4()))

# 5. Example usage
user_input = "Hello Continuum"
context.add("user", user_input)

episodic.record(context)
semantic.set("last_greeting", user_input)

result = controller.handle_user_message(context, user_input)
print(result.final_response)