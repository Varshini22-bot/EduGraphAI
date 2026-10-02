"""
static_graph_store.py

Embedded static Knowledge Graph store that reads from the curated export dataset
(Backend/data/cloud_export/knowledge_graph_export.json).

Acts as an automated high-resilience fallback when cloud Neo4j AuraDB is
temporarily paused (e.g. 72-hour inactivity auto-pause on free tier) or when
the local database service is unavailable.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class StaticGraphStore:
    _initialized: bool = False
    _labels: List[str] = []
    _concepts_by_id: Dict[str, Dict[str, Any]] = {}
    _concepts_by_lower: Dict[str, Dict[str, Any]] = {}
    _outgoing_map: Dict[str, List[Dict[str, Any]]] = {}
    _incoming_map: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def _find_export_path(cls) -> Optional[Path]:
        candidates = [
            Path(__file__).resolve().parent.parent / "data" / "cloud_export" / "knowledge_graph_export.json",
            Path(__file__).resolve().parent.parent.parent / "Backend" / "data" / "cloud_export" / "knowledge_graph_export.json",
            Path("Backend/data/cloud_export/knowledge_graph_export.json").resolve(),
            Path("data/cloud_export/knowledge_graph_export.json").resolve(),
        ]
        for p in candidates:
            if p.is_file():
                return p
        return None

    @classmethod
    def load(cls) -> bool:
        if cls._initialized:
            return True

        export_file = cls._find_export_path()
        if not export_file:
            logger.warning("[STATIC STORE] knowledge_graph_export.json not found.")
            return False

        try:
            with open(export_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            concepts_by_id: Dict[str, Dict[str, Any]] = {}
            concepts_by_lower: Dict[str, Dict[str, Any]] = {}
            labels_set = set()

            for c in data.get("concepts", []):
                cid = c.get("id") or ""
                lbl = c.get("label") or cid
                node_dict = {
                    "id": cid,
                    "label": lbl,
                    "type": c.get("type", "Concept"),
                    "subject": c.get("subject", "General"),
                    "properties": c.get("properties", {}),
                }
                concepts_by_id[cid] = node_dict
                if lbl:
                    concepts_by_lower[lbl.lower()] = node_dict
                    labels_set.add(lbl)
                if cid:
                    concepts_by_lower[cid.lower()] = node_dict

            for s in data.get("subjects", []):
                name = s.get("name") or ""
                if name:
                    node_dict = {
                        "id": name,
                        "label": name,
                        "type": "Subject",
                        "subject": name,
                        "properties": s.get("properties", {}),
                    }
                    concepts_by_id[name] = node_dict
                    concepts_by_lower[name.lower()] = node_dict
                    labels_set.add(name)

            outgoing_map: Dict[str, List[Dict[str, Any]]] = {}
            incoming_map: Dict[str, List[Dict[str, Any]]] = {}

            for r in data.get("relationships", []):
                src_id = r.get("source") or ""
                tgt_id = r.get("target") or ""
                rtype = r.get("type") or "RELATED_TO"

                src_node = concepts_by_id.get(src_id)
                tgt_node = concepts_by_id.get(tgt_id)

                src_label = src_node["label"] if src_node else src_id
                tgt_label = tgt_node["label"] if tgt_node else tgt_id

                out_rel = {
                    "relationship": rtype,
                    "target": tgt_label,
                    "target_type": tgt_node["type"] if tgt_node else "Concept",
                    "target_subject": tgt_node["subject"] if tgt_node else "General",
                }
                in_rel = {
                    "source": src_label,
                    "relationship": rtype,
                    "source_type": src_node["type"] if src_node else "Concept",
                    "source_subject": src_node["subject"] if src_node else "General",
                }

                outgoing_map.setdefault(src_label.lower(), []).append(out_rel)
                if src_id.lower() != src_label.lower():
                    outgoing_map.setdefault(src_id.lower(), []).append(out_rel)

                incoming_map.setdefault(tgt_label.lower(), []).append(in_rel)
                if tgt_id.lower() != tgt_label.lower():
                    incoming_map.setdefault(tgt_id.lower(), []).append(in_rel)

            cls._concepts_by_id = concepts_by_id
            cls._concepts_by_lower = concepts_by_lower
            cls._outgoing_map = outgoing_map
            cls._incoming_map = incoming_map
            cls._labels = sorted(list(labels_set))
            cls._initialized = True
            logger.info(
                "[STATIC STORE] Successfully indexed %d concepts and %d labels from curated export.",
                len(concepts_by_id),
                len(cls._labels),
            )
            return True
        except Exception as e:
            logger.error("[STATIC STORE] Failed to load static export: %s", e)
            return False

    @classmethod
    def get_all_topic_labels(cls) -> List[str]:
        cls.load()
        return list(cls._labels)

    @classmethod
    def get_topic(cls, topic: Optional[str]) -> Optional[Dict[str, Any]]:
        if not topic or not str(topic).strip():
            return None
        cls.load()
        node = cls._concepts_by_lower.get(str(topic).strip().lower())
        return dict(node) if node else None

    @classmethod
    def topic_exists(cls, topic: Optional[str]) -> bool:
        return cls.get_topic(topic) is not None

    @classmethod
    def get_outgoing(cls, topic: Optional[str]) -> List[Dict[str, Any]]:
        if not topic or not str(topic).strip():
            return []
        cls.load()
        return list(cls._outgoing_map.get(str(topic).strip().lower(), []))

    @classmethod
    def get_incoming(cls, topic: Optional[str]) -> List[Dict[str, Any]]:
        if not topic or not str(topic).strip():
            return []
        cls.load()
        return list(cls._incoming_map.get(str(topic).strip().lower(), []))

    @classmethod
    def get_neighbors(cls, topic: Optional[str]) -> List[Dict[str, Any]]:
        if not topic or not str(topic).strip():
            return []
        cls.load()
        outgoing = cls.get_outgoing(topic)
        incoming = cls.get_incoming(topic)
        return outgoing + incoming

    @classmethod
    def search(cls, keyword: str) -> List[Dict[str, Any]]:
        cls.load()
        kw = keyword.strip().lower()
        matches = []
        for c in cls._concepts_by_id.values():
            if kw in c.get("label", "").lower() or kw in c.get("id", "").lower():
                matches.append({
                    "label": c.get("label"),
                    "type": c.get("type"),
                    "subject": c.get("subject"),
                })
                if len(matches) >= 20:
                    break
        return matches

    @classmethod
    def get_complete_response(cls, topic: str) -> Dict[str, Any]:
        cls.load()
        node = cls.get_topic(topic)
        if not node:
            return {
                "status": False,
                "message": "Topic not found",
                "is_connection_error": False,
                "node": None,
                "outgoing": [],
                "incoming": [],
            }

        outgoing = cls.get_outgoing(topic)
        incoming = cls.get_incoming(topic)

        return {
            "status": True,
            "node": node,
            "outgoing": outgoing,
            "incoming": incoming,
            "is_fallback": True,
        }
