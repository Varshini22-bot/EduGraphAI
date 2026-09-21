"""
neo4j_client.py

Central Neo4j connection manager with resilient cloud-to-local failover.

Features:
- Cloud-optimized connection pooling (max_connection_lifetime, connection_timeout).
- Intelligent Hybrid Auto-Failover: If primary cloud AuraDB is paused or unreachable,
  it automatically fails over to local Neo4j (if available) without dropping queries.
- Health Check & Diagnostics: Reports connection status, active target, and latency.
- Graceful session management.
"""

import time
from typing import Optional, Dict, Any
from neo4j import GraphDatabase, exceptions as neo4j_exceptions

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    NEO4J_DATABASE,
    NEO4J_MODE,
    NEO4J_FALLBACK_URI,
    NEO4J_FALLBACK_USERNAME,
    NEO4J_FALLBACK_PASSWORD,
)


class Neo4jClient:
    def __init__(
        self,
        mode: Optional[str] = None,
        primary_uri: Optional[str] = None,
        primary_user: Optional[str] = None,
        primary_pass: Optional[str] = None,
        fallback_uri: Optional[str] = None,
        fallback_user: Optional[str] = None,
        fallback_pass: Optional[str] = None,
    ):
        self._primary_driver = None
        self._fallback_driver = None
        self.active_target: str = "primary"  # "primary" or "fallback"
        self._mode = mode or NEO4J_MODE
        self.primary_uri = primary_uri or (NEO4J_FALLBACK_URI if self._mode == "local" else NEO4J_URI)
        self.primary_user = primary_user or (NEO4J_FALLBACK_USERNAME if self._mode == "local" else NEO4J_USERNAME)
        self.primary_pass = primary_pass or (NEO4J_FALLBACK_PASSWORD if self._mode == "local" else NEO4J_PASSWORD)
        self.fallback_uri = fallback_uri or NEO4J_FALLBACK_URI
        self.fallback_user = fallback_user or NEO4J_FALLBACK_USERNAME
        self.fallback_pass = fallback_pass or NEO4J_FALLBACK_PASSWORD

    def _create_driver(self, uri: str, username: str, password: str):
        """Creates a driver configured for cloud and local resilience."""
        is_cloud = uri.startswith("neo4j+s://") or uri.startswith("neo4j+ssc://")
        return GraphDatabase.driver(
            uri,
            auth=(username, password),
            max_connection_lifetime=300 if is_cloud else 3600,
            connection_timeout=30.0 if is_cloud else 5.0,
            max_connection_pool_size=50,
        )

    @property
    def primary_driver(self):
        if self._primary_driver is None:
            self._primary_driver = self._create_driver(self.primary_uri, self.primary_user, self.primary_pass)
        return self._primary_driver

    @property
    def fallback_driver(self):
        if self._fallback_driver is None:
            self._fallback_driver = self._create_driver(
                self.fallback_uri,
                self.fallback_user,
                self.fallback_pass,
            )
        return self._fallback_driver

    def close(self):
        """Closes all initialized drivers."""
        if self._primary_driver:
            try:
                self._primary_driver.close()
            except Exception:
                pass
            self._primary_driver = None
        if self._fallback_driver:
            try:
                self._fallback_driver.close()
            except Exception:
                pass
            self._fallback_driver = None

    def _get_raw_session(self, database: Optional[str] = None):
        target_db = database or NEO4J_DATABASE
        if self.active_target == "fallback" and self._mode == "auto":
            try:
                return self.fallback_driver.session(database=target_db)
            except Exception:
                self.active_target = "primary"
        return self.primary_driver.session(database=target_db)

    def get_session(self, database: str = None):
        """
        Returns a resilient Neo4j session proxy.
        In 'auto' mode, queries run against the primary cloud database and automatically
        fail over to the fallback local Neo4j instance if the cloud is paused or unreachable.
        """
        return ResilientSession(self, database=database)

    def check_health(self) -> Dict[str, Any]:
        """Performs a live connectivity probe and returns structured diagnostics."""
        target_db = NEO4J_DATABASE
        start_t = time.perf_counter()

        # Check primary
        primary_ok = False
        primary_latency = 0.0
        primary_err = None
        is_cloud = self.primary_uri.startswith("neo4j+s://") or self.primary_uri.startswith("neo4j+ssc://")

        try:
            with self.primary_driver.session(database=target_db) as s:
                s.run("RETURN 1 AS ping").single()
            primary_latency = round((time.perf_counter() - start_t) * 1000, 2)
            primary_ok = True
        except Exception as e:
            primary_err = str(e)

        if primary_ok:
            self.active_target = "primary"
            return {
                "healthy": True,
                "mode": self._mode,
                "active_target": "cloud" if is_cloud else "local",
                "active_uri": self.primary_uri,
                "database": target_db,
                "latency_ms": primary_latency,
                "paused": False,
                "failover_active": False,
            }

        # If primary failed and in auto mode, check fallback
        can_fallback = (
            self._mode == "auto"
            and (self.primary_uri != self.fallback_uri or self._fallback_driver is not None)
        )
        if can_fallback:
            fb_start = time.perf_counter()
            try:
                with self.fallback_driver.session(database=target_db) as s:
                    s.run("RETURN 1 AS ping").single()
                fb_latency = round((time.perf_counter() - fb_start) * 1000, 2)
                self.active_target = "fallback"
                return {
                    "healthy": True,
                    "mode": self._mode,
                    "active_target": "local (failover)",
                    "active_uri": self.fallback_uri,
                    "database": target_db,
                    "latency_ms": fb_latency,
                    "paused": is_cloud,
                    "failover_active": True,
                    "primary_error": primary_err,
                }
            except Exception:
                pass

        # Both failed or cloud-only mode
        return {
            "healthy": False,
            "mode": self._mode,
            "active_target": "none",
            "active_uri": self.primary_uri,
            "database": target_db,
            "latency_ms": None,
            "paused": is_cloud,
            "error": primary_err,
            "guidance": (
                "AuraDB instance may be paused. Visit console.neo4j.io and click 'Resume' (~60s), "
                "or start your local Neo4j database service."
            )
        }


class ResilientSession:
    """
    A session wrapper that intercepts connectivity errors (such as an AuraDB auto-pause
    or network disconnect) and transparently fails over to the local fallback driver.
    """
    def __init__(self, client: Neo4jClient, database: Optional[str] = None):
        self.client = client
        self.database = database or NEO4J_DATABASE
        self._raw_session = None

    def __enter__(self):
        self._ensure_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _ensure_session(self):
        if self._raw_session is None:
            self._raw_session = self.client._get_raw_session(self.database)
        return self._raw_session

    def run(self, query: str, **parameters):
        session = self._ensure_session()
        try:
            return session.run(query, **parameters)
        except (
            neo4j_exceptions.ServiceUnavailable,
            neo4j_exceptions.SessionExpired,
            neo4j_exceptions.TransientError,
            TimeoutError,
            OSError,
        ) as e:
            can_fallback = (
                self.client._mode == "auto"
                and self.client.active_target == "primary"
                and (self.client.primary_uri != self.client.fallback_uri or self.client._fallback_driver is not None)
            )
            if can_fallback:
                print(
                    f"[NEO4J RESILIENCE] Primary query failed ({type(e).__name__}: {e}). "
                    f"Auto-failing over to fallback: {self.client.fallback_uri}"
                )
                try:
                    session.close()
                except Exception:
                    pass
                self.client.active_target = "fallback"
                self._raw_session = self.client.fallback_driver.session(database=self.database)
                return self._raw_session.run(query, **parameters)
            raise

    def close(self):
        if self._raw_session is not None:
            try:
                self._raw_session.close()
            except Exception:
                pass
            self._raw_session = None


# Create one shared client
neo4j_client = Neo4jClient()


# Helper functions
def get_driver():
    return neo4j_client.primary_driver if neo4j_client.active_target == "primary" else neo4j_client.fallback_driver


def get_session(database: str = None):
    return neo4j_client.get_session(database=database)


def check_graph_health() -> Dict[str, Any]:
    return neo4j_client.check_health()