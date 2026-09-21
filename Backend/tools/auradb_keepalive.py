"""
auradb_keepalive.py

Utility script to ping cloud Neo4j AuraDB instances to prevent 3-day inactivity auto-pauses.

Neo4j AuraDB Free pauses databases after 72 hours (3 days) of query inactivity.
Running this script periodically (e.g., once daily via cron, Windows Task Scheduler,
or background loop) resets the 3-day inactivity timer by executing a lightweight query.

Usage:
    # Single heartbeat ping:
    python tools/auradb_keepalive.py

    # Continuous daemon mode (e.g., runs once every 24 hours):
    python tools/auradb_keepalive.py --loop --interval-hours 24
"""

import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# Ensure Backend root is in sys.path when running from tools directory
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from neo4j import GraphDatabase, exceptions as neo4j_exceptions
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE


def ping_auradb(uri: str = NEO4J_URI, username: str = NEO4J_USERNAME, password: str = NEO4J_PASSWORD, database: str = NEO4J_DATABASE) -> bool:
    """
    Executes a minimal ping query (RETURN 1) against the specified Neo4j database.
    Returns True on success, False on failure.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Probing Neo4j database at {uri}...")

    if not uri or uri.startswith("bolt://localhost") or uri.startswith("bolt://127.0.0.1"):
        print(f"[{now_str}] NOTICE: Configured URI ({uri}) appears to be a local instance, not AuraDB.")

    start_time = time.perf_counter()
    driver = None
    try:
        driver = GraphDatabase.driver(
            uri,
            auth=(username, password),
            connection_timeout=15.0,
            max_connection_lifetime=60,
        )
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 AS ping, datetime() AS server_time").single()
            server_time = result["server_time"] if result else "unknown"

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"[{now_str}] SUCCESS: Neo4j AuraDB heartbeat confirmed in {elapsed_ms}ms! (Server time: {server_time})")
        print(f"[{now_str}] Inactivity timer reset. The database will remain active.")
        return True

    except (neo4j_exceptions.ServiceUnavailable, neo4j_exceptions.SessionExpired, TimeoutError) as conn_err:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"[{now_str}] FAILED: Unable to reach Neo4j database ({conn_err}) after {elapsed_ms}ms.", file=sys.stderr)
        print(f"[{now_str}] If this is AuraDB Free, the instance may already be paused.", file=sys.stderr)
        print(f"[{now_str}] Visit https://console.neo4j.io to click 'Resume' (~60s to warm up).", file=sys.stderr)
        return False

    except Exception as err:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"[{now_str}] ERROR: Unexpected error during ping: {err} ({elapsed_ms}ms)", file=sys.stderr)
        return False

    finally:
        if driver:
            try:
                driver.close()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="Neo4j AuraDB Keepalive Heartbeat Utility")
    parser.add_argument("--loop", action="store_true", help="Run continuously in a loop")
    parser.add_argument("--interval-hours", type=float, default=24.0, help="Interval between pings in hours (default: 24.0)")
    args = parser.parse_args()

    if not args.loop:
        success = ping_auradb()
        sys.exit(0 if success else 1)

    print(f"Starting continuous Neo4j keepalive loop (interval: {args.interval_hours} hours)...")
    interval_seconds = args.interval_hours * 3600

    while True:
        ping_auradb()
        print(f"Sleeping for {args.interval_hours} hours until next heartbeat...")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nKeepalive daemon stopped by user.")
            break


if __name__ == "__main__":
    main()
