"""
share_service.py

Dual-persistence sharing service:
1. SQLite (local cache for sub-millisecond lookups).
2. Neo4j AuraDB (persistent cloud store that survives Render container restarts).

Generates short 10-char alphanumeric share IDs (e.g. 's_a8f9c2d1')
and preserves complete message content with zero artificial truncation.
"""

import json
import secrets
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from database.models import SharedConversation
from graph.neo4j_client import Neo4jClient

_neo4j_client = None


def _get_neo4j() -> Neo4jClient:
    global _neo4j_client
    if _neo4j_client is None:
        _neo4j_client = Neo4jClient()
    return _neo4j_client


def save_shared_conversation(
    db: Session,
    title: str,
    topic: Optional[str],
    messages: List[Dict[str, Any]],
) -> str:
    share_id = f"s_{secrets.token_hex(4)}"
    messages_json = json.dumps(messages, ensure_ascii=False)
    safe_title = (title.strip() if title else "EduGraphAI Conversation")[:255]
    safe_topic = (topic.strip() if topic else None)
    if safe_topic:
        safe_topic = safe_topic[:255]

    # 1. SQLite save
    try:
        shared = SharedConversation(
            id=share_id,
            title=safe_title,
            topic=safe_topic,
            messages_json=messages_json,
            created_at=datetime.utcnow(),
        )
        db.add(shared)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[WARN] Failed to save shared conversation to SQLite: {e}")

    # 2. Neo4j save (for cloud persistence across Render restarts)
    try:
        client = _get_neo4j()
        with client.get_session() as session:
            session.run(
                """
                MERGE (s:SharedConversation {id: $share_id})
                SET s.title = $title,
                    s.topic = $topic,
                    s.messages_json = $messages_json,
                    s.created_at = datetime()
                RETURN s.id AS id
                """,
                share_id=share_id,
                title=safe_title,
                topic=safe_topic,
                messages_json=messages_json,
            )
    except Exception as e:
        print(f"[WARN] Failed to save shared conversation to Neo4j: {e}")

    return share_id


def get_shared_conversation(db: Session, share_id: str) -> Optional[Dict[str, Any]]:
    # 1. Try SQLite first
    try:
        shared = db.query(SharedConversation).filter(SharedConversation.id == share_id).first()
        if shared:
            return {
                "id": shared.id,
                "title": shared.title,
                "topic": shared.topic,
                "messages": json.loads(shared.messages_json),
                "created_at": shared.created_at.isoformat() if shared.created_at else None,
            }
    except Exception as e:
        print(f"[WARN] SQLite shared lookup failed: {e}")

    # 2. Try Neo4j if not found in SQLite (e.g. Render restarted container)
    try:
        client = _get_neo4j()
        with client.get_session() as session:
            result = session.run(
                """
                MATCH (s:SharedConversation {id: $share_id})
                RETURN s.id AS id, s.title AS title, s.topic AS topic, s.messages_json AS messages_json
                """,
                share_id=share_id,
            ).single()
            if result:
                messages_data = json.loads(result["messages_json"])
                # Re-cache into SQLite
                try:
                    re_cached = SharedConversation(
                        id=share_id,
                        title=result["title"] or "EduGraphAI Conversation",
                        topic=result["topic"],
                        messages_json=result["messages_json"],
                        created_at=datetime.utcnow(),
                    )
                    db.add(re_cached)
                    db.commit()
                except Exception:
                    db.rollback()

                return {
                    "id": result["id"],
                    "title": result["title"],
                    "topic": result["topic"],
                    "messages": messages_data,
                }
    except Exception as e:
        print(f"[WARN] Neo4j shared lookup failed: {e}")

    return None
