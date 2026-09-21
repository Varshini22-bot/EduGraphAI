"""
import_to_cloud_neo4j.py

Production-grade migration utility to import the EduGraphAI Knowledge Graph
into Neo4j AuraDB (or any cloud/managed Neo4j instance).

Features:
- Idempotent: Uses MERGE so running multiple times will never duplicate data.
- High Performance: Uses batched UNWIND Cypher statements.
- Schema & Index Optimization: Creates uniqueness constraints and label indexes.
- Complete Property Preservation: Preserves all node and edge properties.
- Verification: Validates node and relationship counts post-import.
- AuraDB Compatible: Supports neo4j+s:// and neo4j+ssc:// with connection pooling.

Usage:
  # Using environment variables from .env:
  python tools/import_to_cloud_neo4j.py

  # Or providing custom credentials via CLI:
  python tools/import_to_cloud_neo4j.py \\
    --uri neo4j+s://<your-instance-id>.databases.neo4j.io \\
    --user neo4j \\
    --password <your-password> \\
    --database neo4j
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Any

# Ensure project root / Backend is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from neo4j import GraphDatabase

# Try loading .env if available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BACKEND_DIR, ".env"))
except Exception:
    pass

DEFAULT_DATA_FILE = os.path.join(
    BACKEND_DIR, "data", "cloud_export", "knowledge_graph_export.json"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Import EduGraphAI Knowledge Graph into Neo4j AuraDB / Cloud instance."
    )
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        help="Neo4j connection URI (e.g. neo4j+s://xxxx.databases.neo4j.io)",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("NEO4J_USERNAME", "neo4j"),
        help="Neo4j username (default: neo4j)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PASSWORD", ""),
        help="Neo4j password",
    )
    parser.add_argument(
        "--database",
        default=os.getenv("NEO4J_DATABASE", "neo4j"),
        help="Target database name (default: neo4j)",
    )
    parser.add_argument(
        "--data-file",
        default=DEFAULT_DATA_FILE,
        help="Path to export JSON file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=250,
        help="Batch size for UNWIND Cypher operations (default: 250)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Skip import and only verify the target database counts",
    )
    return parser.parse_args()


def create_driver(uri: str, user: str, password: str):
    """Creates a configured Neo4j driver with cloud connection pool settings."""
    return GraphDatabase.driver(
        uri,
        auth=(user, password),
        max_connection_lifetime=300,
        connection_timeout=30.0,
    )


def create_constraints_and_indexes(session):
    """Creates uniqueness constraints and performance indexes."""
    print("\n[Step 1/5] Creating Constraints and Indexes...")

    statements = [
        # Concept unique constraint
        "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
        # Subject unique constraint
        "CREATE CONSTRAINT subject_name_unique IF NOT EXISTS FOR (s:Subject) REQUIRE s.name IS UNIQUE",
        # Concept label lookup index
        "CREATE INDEX concept_label_idx IF NOT EXISTS FOR (c:Concept) ON (c.label)",
    ]

    for stmt in statements:
        try:
            session.run(stmt)
            print(f"  [Applied] {stmt.split()[1]} {stmt.split()[2]}")
        except Exception as e:
            # Aura or older versions might have slightly different constraint syntax
            print(f"  [Note] Constraint statement: {e}")


def import_nodes(session, subjects: List[Dict], concepts: List[Dict], batch_size: int):
    """Imports Subject and Concept nodes using batched MERGE statements."""
    print("\n[Step 2/5] Importing Subject Nodes...")
    query_subjects = """
    UNWIND $batch AS row
    MERGE (s:Subject {name: row.name})
    SET s += row.properties
    """
    session.run(query_subjects, batch=subjects)
    print(f"  Merged {len(subjects)} Subject nodes.")

    print("\n[Step 3/5] Importing Concept Nodes...")
    query_concepts = """
    UNWIND $batch AS row
    MERGE (c:Concept {id: row.id})
    SET c.label = row.label,
        c.type = row.type,
        c.subject = row.subject
    SET c += row.properties
    """
    for i in range(0, len(concepts), batch_size):
        chunk = concepts[i:i + batch_size]
        session.run(query_concepts, batch=chunk)
        print(f"  Merged concepts {i + 1} to {min(i + batch_size, len(concepts))} of {len(concepts)}...")


def import_relationships(session, relationships: List[Dict], batch_size: int):
    """Imports relationships grouped by relationship type for Cypher optimization."""
    print(f"\n[Step 4/5] Importing {len(relationships)} Relationships...")

    # Group by relationship type
    by_type: Dict[str, List[Dict]] = {}
    for r in relationships:
        rel_type = r["type"]
        by_type.setdefault(rel_type, []).append({
            "source": r["source"],
            "target": r["target"],
            "props": r.get("properties", {})
        })

    for rel_type, rel_list in sorted(by_type.items()):
        print(f"  Importing type ':{rel_type}' ({len(rel_list)} edges)...")

        query = f"""
        UNWIND $batch AS row
        MATCH (a) WHERE (a:Concept AND a.id = row.source) OR (a:Subject AND a.name = row.source)
        MATCH (b) WHERE (b:Concept AND b.id = row.target) OR (b:Subject AND b.name = row.target)
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += row.props
        """

        for i in range(0, len(rel_list), batch_size):
            chunk = rel_list[i:i + batch_size]
            session.run(query, batch=chunk)


def verify_database(session, expected_nodes: int = 475, expected_rels: int = 972):
    """Verifies node counts, relationship counts, and sample query responses."""
    print("\n[Step 5/5] Verifying Target Database State...")

    node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

    print(f"  Target Total Nodes        : {node_count} (Expected: {expected_nodes})")
    print(f"  Target Total Relationships: {rel_count} (Expected: {expected_rels})")

    # Sample query verification
    test_res = session.run("""
        MATCH (c:Concept {label: 'Quick Sort'})-[r]->(target)
        RETURN type(r) AS rel, coalesce(target.label, target.name) AS target_name
    """).data()

    print(f"  Sample verification query on 'Quick Sort': {len(test_res)} outgoing edges found.")
    for row in test_res:
        print(f"    -[:{row['rel']}]-> {row['target_name']}")

    is_valid = (node_count == expected_nodes and rel_count == expected_rels)
    if is_valid:
        print("\n>>> DATABASE VERIFICATION SUCCESSFUL: 100% MATCH! <<<")
    else:
        print(f"\n>>> WARNING: Counts (Nodes: {node_count}, Relationships: {rel_count}) do not match expected ({expected_nodes}, {expected_rels})! <<<")

    return is_valid


def main():
    args = parse_args()

    print("=" * 70)
    print("EduGraphAI - Neo4j Cloud Migration & Ingestion Utility")
    print("=" * 70)
    print(f"Target URI      : {args.uri}")
    print(f"Target Username : {args.user}")
    print(f"Target Database : {args.database}")
    print(f"Data File       : {args.data_file}")

    if not os.path.exists(args.data_file):
        print(f"Error: Data file not found: {args.data_file}")
        sys.exit(1)

    with open(args.data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    subjects = data.get("subjects", [])
    concepts = data.get("concepts", [])
    relationships = data.get("relationships", [])
    expected_nodes = len(subjects) + len(concepts)
    expected_rels = len(relationships)

    print(f"Loaded {len(subjects)} subjects, {len(concepts)} concepts, {len(relationships)} relationships.")

    driver = create_driver(args.uri, args.user, args.password)
    start_time = time.time()

    try:
        with driver.session(database=args.database) as session:
            # Connectivity check
            session.run("RETURN 1").single()
            print("Connected successfully to target Neo4j instance.")

            if not args.verify_only:
                create_constraints_and_indexes(session)
                import_nodes(session, subjects, concepts, args.batch_size)
                import_relationships(session, relationships, args.batch_size)

            valid = verify_database(session, expected_nodes, expected_rels)
            elapsed = time.time() - start_time
            print(f"\nOperation completed in {elapsed:.2f} seconds.")
            sys.exit(0 if valid else 1)

    except Exception as e:
        print(f"\nError during migration: {e}")
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
