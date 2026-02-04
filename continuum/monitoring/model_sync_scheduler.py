from apscheduler.schedulers.background import BackgroundScheduler
from continuum.config.model_search import refresh_node
from continuum.db.sqlalchemy_connection import get_db_session
from continuum.db.models.nodes import Node


scheduler = BackgroundScheduler()

def scheduled_model_refresh():
    db = get_db_session()
    nodes = db.query(Node).filter(Node.enabled == True).all()

    for node in nodes:
        try:
            refresh_node(node_id=node.id, endpoint=node.host)
        except Exception as e:
            print(f"[ModelSync] Failed to refresh node {node.host}: {e}")

    db.close()

def start_scheduler():
    scheduler.add_job(scheduled_model_refresh, "interval", minutes=10)
    scheduler.start()