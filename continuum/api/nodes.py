from fastapi import APIRouter, HTTPException
from continuum.db.sqlalchemy_connection import get_db_session
from continuum.db.models.nodes import Node
from continuum.config.model_search import refresh_node

router = APIRouter()

@router.post("/nodes/{node_id}/refresh")
def refresh_node_endpoint(node_id: int):
    db = get_db_session()
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    try:
        refresh_node(node_id=node.id, endpoint=node.host)
        return {"status": "success", "message": f"Node {node_id} refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()