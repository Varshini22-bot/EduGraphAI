"""
test_p2_hardening.py

Automated test suite for Part 14 P2 security hardening:
1. P2A: Graph health does not expose Neo4j/AuraDB URI, database identifier, or raw socket information.
2. P2B: In-memory sliding-window rate limiting on /auth/login and /auth/register.
3. P2C: Password length policy enforcement (minimum 8 characters).
4. P2D: Active /query and /ask routes remain intact and registered in OpenAPI schema.
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure Backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database.database import Base, get_db
from database.models import User
from database.auth import hash_password
from utils.rate_limiter import login_rate_limiter, register_rate_limiter
from graph.neo4j_client import check_graph_health, Neo4jClient
from app import app


class TestGraphHealthURIProtection(unittest.TestCase):
    """Verifies that /graph/health and check_graph_health() redact infrastructure URIs and IDs."""

    def test_healthy_probe_structure_is_safe(self):
        """A healthy probe must not leak URI, hostname, or database identifier."""
        # Create a mock client that simulates a healthy cloud connection
        client = Neo4jClient(mode="cloud", primary_uri="neo4j+s://secret-db.databases.neo4j.io")
        # Replace the driver run call with a harmless mock
        class MockSession:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def run(self, *args, **kwargs):
                class MockRecord:
                    def single(self):
                        return 1
                return MockRecord()

        class MockDriver:
            def session(self, **kwargs):
                return MockSession()

        client._primary_driver = MockDriver()
        health = client.check_health()

        # Operational status must be present
        self.assertTrue(health["healthy"])
        self.assertEqual(health["mode"], "cloud")
        self.assertEqual(health["active_target"], "cloud")
        self.assertIn("latency_ms", health)
        self.assertFalse(health["paused"])
        self.assertFalse(health["failover_active"])

        # Sensitive identifiers must NEVER be present
        self.assertNotIn("active_uri", health)
        self.assertNotIn("database", health)
        for key, val in health.items():
            if isinstance(val, str):
                self.assertNotIn("secret-db.databases.neo4j.io", val)
                self.assertNotIn("neo4j+s://", val)
                self.assertNotIn("bolt://", val)

    def test_unhealthy_probe_structure_is_safe(self):
        """An unhealthy probe must not expose URIs, IP addresses, or internal hostnames in error strings."""
        client = Neo4jClient(mode="cloud", primary_uri="neo4j+s://secret-db.databases.neo4j.io")
        # Force failure
        class FailingDriver:
            def session(self, **kwargs):
                raise ConnectionRefusedError("Failed to connect to 127.0.0.1:7687 or secret-db.databases.neo4j.io")

        client._primary_driver = FailingDriver()
        health = client.check_health()

        self.assertFalse(health["healthy"])
        self.assertEqual(health["active_target"], "none")
        self.assertTrue(health["static_fallback_active"])
        self.assertIn("guidance", health)

        # Sensitive keys must be omitted
        self.assertNotIn("active_uri", health)
        self.assertNotIn("database", health)

        # Ensure error message is generic/sanitized and does not leak raw IP/hostname
        if "error" in health and health["error"]:
            self.assertNotIn("127.0.0.1", health["error"])
            self.assertNotIn("secret-db.databases.neo4j.io", health["error"])
            self.assertNotIn("bolt://", health["error"])
            self.assertNotIn("neo4j+s://", health["error"])

    def test_api_graph_health_endpoint_response_is_safe(self):
        """The FastAPI /graph/health endpoint must return safe JSON without active_uri or database."""
        client = TestClient(app)
        response = client.get("/graph/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("healthy", data)
        self.assertNotIn("active_uri", data)
        self.assertNotIn("database", data)


class TestPasswordPolicyValidation(unittest.TestCase):
    """Verifies that the registration endpoint enforces the minimum 8-character password policy."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def setUp(self):
        login_rate_limiter.reset()
        register_rate_limiter.reset()
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def test_single_character_password_rejected(self):
        """1-character password must be rejected with 422 Unprocessable Entity."""
        res = self.client.post(
            "/auth/register",
            json={"email": "pwd1@example.com", "full_name": "Test User", "password": "a"},
        )
        self.assertEqual(res.status_code, 422)
        errors = res.json().get("detail", [])
        self.assertTrue(any("at least 8 characters" in str(e) for e in errors))

    def test_seven_character_password_rejected(self):
        """7-character password must be rejected with 422 Unprocessable Entity."""
        res = self.client.post(
            "/auth/register",
            json={"email": "pwd7@example.com", "full_name": "Test User", "password": "Pass12!"},
        )
        self.assertEqual(res.status_code, 422)
        errors = res.json().get("detail", [])
        self.assertTrue(any("at least 8 characters" in str(e) for e in errors))

    def test_eight_character_password_accepted(self):
        """8-character password meets minimum requirement and succeeds with 201 Created."""
        res = self.client.post(
            "/auth/register",
            json={"email": "pwd8@example.com", "full_name": "Test User", "password": "Pass123!"},
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["email"], "pwd8@example.com")
        self.assertTrue(data["is_active"])

    def test_long_password_accepted(self):
        """Standard long secure password succeeds with 201 Created."""
        res = self.client.post(
            "/auth/register",
            json={"email": "pwdlong@example.com", "full_name": "Test User", "password": "CorrectHorseBatteryStaple99!"},
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["email"], "pwdlong@example.com")


class TestAuthenticationRateLimiting(unittest.TestCase):
    """Verifies that authentication routes apply in-memory sliding-window rate limiting."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def setUp(self):
        login_rate_limiter.reset()
        register_rate_limiter.reset()
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def test_login_rate_limiting_triggers_after_max_attempts(self):
        """Repeated login attempts beyond limit (5) must return 429 Too Many Requests."""
        # 5 attempts within limit
        for i in range(5):
            res = self.client.post(
                "/auth/login",
                data={"username": "test@example.com", "password": f"WrongAttempt{i}!"},
                headers={"X-Forwarded-For": "198.51.100.1"},
            )
            # Below rate limit: rejected by credentials check with 401
            self.assertEqual(res.status_code, 401)
            self.assertEqual(res.json()["detail"], "Incorrect email or password")

        # 6th attempt: blocked by rate limiter
        res_blocked = self.client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "WrongAttempt6!"},
            headers={"X-Forwarded-For": "198.51.100.1"},
        )
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Too many requests", res_blocked.json()["detail"])
        self.assertIn("Retry-After", res_blocked.headers)

    def test_register_rate_limiting_triggers_after_max_attempts(self):
        """Repeated registration attempts beyond limit (5) must return 429."""
        for i in range(5):
            res = self.client.post(
                "/auth/register",
                json={"email": f"reg_{i}@example.com", "full_name": f"User {i}", "password": "SecurePassword123!"},
                headers={"X-Forwarded-For": "198.51.100.2"},
            )
            self.assertEqual(res.status_code, 201)

        # 6th attempt from the same client IP
        res_blocked = self.client.post(
            "/auth/register",
            json={"email": "reg_overflow@example.com", "full_name": "User Overflow", "password": "SecurePassword123!"},
            headers={"X-Forwarded-For": "198.51.100.2"},
        )
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Too many requests", res_blocked.json()["detail"])
        self.assertIn("Retry-After", res_blocked.headers)

    def test_different_ips_have_independent_quotas(self):
        """Rate limiting on one IP does not affect requests from another IP."""
        # Exhaust quota on IP A
        for _ in range(5):
            self.client.post(
                "/auth/login",
                data={"username": "userA@example.com", "password": "WrongPassword!"},
                headers={"X-Forwarded-For": "203.0.113.10"},
            )

        # IP A is blocked
        res_a = self.client.post(
            "/auth/login",
            data={"username": "userA@example.com", "password": "WrongPassword!"},
            headers={"X-Forwarded-For": "203.0.113.10"},
        )
        self.assertEqual(res_a.status_code, 429)

        # IP B still has normal quota available (returns 401 credentials error, not 429)
        res_b = self.client.post(
            "/auth/login",
            data={"username": "userB@example.com", "password": "WrongPassword!"},
            headers={"X-Forwarded-For": "203.0.113.20"},
        )
        self.assertEqual(res_b.status_code, 401)


class TestActiveRoutesIntegrity(unittest.TestCase):
    """Verifies that active API routes (/ask and POST /query) remain registered and functional."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_openapi_schema_contains_active_query_and_ask_routes(self):
        """OpenAPI spec must register /ask and /query (POST), but not legacy unmounted /query/."""
        res = self.client.get("/openapi.json")
        self.assertEqual(res.status_code, 200)
        paths = res.json().get("paths", {})

        self.assertIn("/ask", paths)
        self.assertIn("get", paths["/ask"])

        self.assertIn("/query", paths)
        self.assertIn("post", paths["/query"])

        # Confirm unmounted legacy route prefix is not present
        self.assertNotIn("/query/", paths)

    def test_empty_query_endpoint_validation(self):
        """POST /query with empty question returns HTTP 400."""
        res = self.client.post("/query", json={"question": "   "})
        self.assertEqual(res.status_code, 400)
        self.assertIn("Question cannot be empty", res.json()["detail"])

    def test_empty_ask_endpoint_validation(self):
        """GET /ask with empty query returns valid fallback guidance without 500 error."""
        res = self.client.get("/ask?query=")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["status"])
        self.assertIn("Please enter a valid question", data["answer"])


if __name__ == "__main__":
    unittest.main()
