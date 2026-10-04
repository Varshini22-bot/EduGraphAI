"""
test_auth_hardening.py

Automated unit and integration tests for Part 13 security hardening:
1. Production rejection of missing or default insecure JWT secret keys.
2. Development mode fallback preservation.
3. Inactive user authentication rejection in CRUD authenticate_user().
4. Inactive user token resolution rejection in get_current_user().
5. FastAPI /auth/login and /auth/me behavior for active vs inactive users.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from fastapi import HTTPException
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
from database import crud
from database.auth import create_access_token, get_current_user, hash_password
from app import app


class TestJWTSecretConfiguration(unittest.TestCase):
    """Verifies that JWT_SECRET_KEY security requirements are strictly enforced."""

    def test_production_mode_missing_secret_raises_runtime_error(self):
        """Production startup must fail with RuntimeError if JWT_SECRET_KEY is empty."""
        env = os.environ.copy()
        env["DEBUG"] = "false"
        env["JWT_SECRET_KEY"] = ""

        result = subprocess.run(
            [sys.executable, "-c", "import config"],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(backend_dir),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FATAL CONFIGURATION ERROR", result.stderr)
        self.assertIn("JWT_SECRET_KEY environment variable is required in production mode", result.stderr)

    def test_production_mode_insecure_default_secret_raises_runtime_error(self):
        """Production startup must fail with RuntimeError if default fallback key is used."""
        env = os.environ.copy()
        env["DEBUG"] = "false"
        env["JWT_SECRET_KEY"] = "knowledge_graph_secret_key_change_this"

        result = subprocess.run(
            [sys.executable, "-c", "import config"],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(backend_dir),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FATAL CONFIGURATION ERROR", result.stderr)
        self.assertIn("Insecure default JWT_SECRET_KEY detected in production mode", result.stderr)

    def test_production_mode_known_insecure_defaults_rejected(self):
        """Production startup must reject all known insecure placeholder secrets."""
        placeholders = [
            "change-this-secret-in-production",
            "change-this-to-a-secure-random-32-byte-hex-string",
        ]
        for placeholder in placeholders:
            env = os.environ.copy()
            env["DEBUG"] = "false"
            env["JWT_SECRET_KEY"] = placeholder

            result = subprocess.run(
                [sys.executable, "-c", "import config"],
                env=env,
                capture_output=True,
                text=True,
                cwd=str(backend_dir),
            )
            self.assertNotEqual(result.returncode, 0, f"Expected failure for placeholder: {placeholder}")
            self.assertIn("Insecure default JWT_SECRET_KEY detected", result.stderr)

    def test_production_mode_valid_secret_succeeds(self):
        """Production startup succeeds when a valid, cryptographically secure secret is supplied."""
        env = os.environ.copy()
        env["DEBUG"] = "false"
        env["JWT_SECRET_KEY"] = "a-very-strong-production-key-9f8e7d6c5b4a3210-secure"

        result = subprocess.run(
            [sys.executable, "-c", "import config; print(config.JWT_SECRET_KEY)"],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(backend_dir),
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "a-very-strong-production-key-9f8e7d6c5b4a3210-secure")

    def test_development_mode_fallback_allowed(self):
        """Development mode (DEBUG=True) allows empty secret with fallback for developer convenience."""
        env = os.environ.copy()
        env["DEBUG"] = "true"
        env["JWT_SECRET_KEY"] = ""

        result = subprocess.run(
            [sys.executable, "-c", "import config; print(config.JWT_SECRET_KEY)"],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(backend_dir),
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "knowledge_graph_secret_key_change_this")


class TestUserAuthenticationSecurity(unittest.TestCase):
    """Verifies that inactive users cannot authenticate via password or access protected routes."""

    @classmethod
    def setUpClass(cls):
        # Create an isolated in-memory SQLite database
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )
        Base.metadata.create_all(bind=cls.engine)

    def setUp(self):
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def test_active_user_authentication_success(self):
        """Active user authenticates successfully with correct password."""
        user = User(
            email="active_user@example.com",
            full_name="Active User",
            hashed_password=hash_password("ValidPass123!"),
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()

        authenticated = crud.authenticate_user(self.db, "active_user@example.com", "ValidPass123!")
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.email, "active_user@example.com")

    def test_active_user_wrong_password_fails(self):
        """Active user fails authentication with incorrect password."""
        user = User(
            email="active_user@example.com",
            full_name="Active User",
            hashed_password=hash_password("ValidPass123!"),
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()

        authenticated = crud.authenticate_user(self.db, "active_user@example.com", "WrongPassword!")
        self.assertIsNone(authenticated)

    def test_inactive_user_authentication_fails(self):
        """Inactive user with correct password MUST be rejected by authenticate_user."""
        inactive_user = User(
            email="inactive_user@example.com",
            full_name="Inactive User",
            hashed_password=hash_password("ValidPass123!"),
            is_active=False,
        )
        self.db.add(inactive_user)
        self.db.commit()

        authenticated = crud.authenticate_user(self.db, "inactive_user@example.com", "ValidPass123!")
        self.assertIsNone(authenticated, "Inactive user should not be authenticated")

    def test_get_current_user_with_active_user(self):
        """Active user is resolved normally from valid JWT token."""
        user = User(
            email="token_active@example.com",
            full_name="Token Active",
            hashed_password=hash_password("ValidPass123!"),
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()

        token = create_access_token(data={"sub": user.email})
        resolved_user = get_current_user(token=token, db=self.db)
        self.assertIsNotNone(resolved_user)
        self.assertEqual(resolved_user.email, "token_active@example.com")

    def test_get_current_user_with_inactive_user_fails(self):
        """Inactive user token resolution MUST raise 401 HTTPException."""
        inactive_user = User(
            email="token_inactive@example.com",
            full_name="Token Inactive",
            hashed_password=hash_password("ValidPass123!"),
            is_active=False,
        )
        self.db.add(inactive_user)
        self.db.commit()

        token = create_access_token(data={"sub": inactive_user.email})
        with self.assertRaises(HTTPException) as cm:
            get_current_user(token=token, db=self.db)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, "Could not validate credentials")


class TestFastAPIAuthEndpoints(unittest.TestCase):
    """End-to-end endpoint tests for /auth/login and /auth/me with active/inactive users."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )
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
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def test_login_active_user_success(self):
        """POST /auth/login returns 200 and access_token for active user."""
        user = User(
            email="login_active@example.com",
            full_name="Active Person",
            hashed_password=hash_password("CorrectPassword123"),
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()

        response = self.client.post(
            "/auth/login",
            data={"username": "login_active@example.com", "password": "CorrectPassword123"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("token_type"), "bearer")

        # Verify access to /auth/me
        token = data["access_token"]
        me_resp = self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.json()["email"], "login_active@example.com")
        self.assertTrue(me_resp.json()["is_active"])

    def test_login_inactive_user_rejected(self):
        """POST /auth/login returns 401 Unauthorized for inactive user."""
        inactive_user = User(
            email="login_inactive@example.com",
            full_name="Inactive Person",
            hashed_password=hash_password("CorrectPassword123"),
            is_active=False,
        )
        self.db.add(inactive_user)
        self.db.commit()

        response = self.client.post(
            "/auth/login",
            data={"username": "login_inactive@example.com", "password": "CorrectPassword123"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Incorrect email or password")

    def test_me_endpoint_rejects_inactive_user_token(self):
        """GET /auth/me returns 401 Unauthorized if account is marked inactive."""
        inactive_user = User(
            email="disabled_account@example.com",
            full_name="Disabled Account",
            hashed_password=hash_password("CorrectPassword123"),
            is_active=False,
        )
        self.db.add(inactive_user)
        self.db.commit()

        token = create_access_token(data={"sub": inactive_user.email})
        response = self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Could not validate credentials")


if __name__ == "__main__":
    unittest.main()
