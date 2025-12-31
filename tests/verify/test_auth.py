"""T014: JWT authentication verification test - RED PHASE (failing test)"""
import pytest
import httpx
from unittest.mock import patch, MagicMock
import jwt


class TestJWTAuthentication:
    """Test suite for verifying JWT authentication on production endpoints."""

    @pytest.fixture
    def production_url(self):
        """Return the production Railway URL from environment or default."""
        import os
        return os.environ.get("PRODUCTION_URL", "https://todo-app.up.railway.app")

    @pytest.fixture
    def jwt_secret(self):
        """Return the JWT secret from environment."""
        import os
        return os.environ.get("JWT_SECRET_KEY")

    @pytest.fixture
    def valid_token(self, jwt_secret):
        """
        Generate a valid JWT token for testing.

        This creates a token that would be valid for an existing user.
        """
        if not jwt_secret:
            pytest.skip("JWT_SECRET_KEY not set")

        # This would need a real user_id from the database
        # For testing, we use a mock payload
        payload = {
            "sub": "test-user-id",
            "user_id": "test-user-id",
            "exp": 9999999999  # Far future
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @pytest.fixture
    def expired_token(self, jwt_secret):
        """Generate an expired JWT token."""
        if not jwt_secret:
            pytest.skip("JWT_SECRET_KEY not set")

        payload = {
            "sub": "test-user-id",
            "user_id": "test-user-id",
            "exp": 0  # Already expired
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_auth(self, production_url):
        """
        Protected endpoints MUST require JWT authentication.

        This test verifies that accessing a protected endpoint without
        an Authorization header returns 401 Unauthorized.
        """
        async with httpx.AsyncClient() as client:
            # Try to access a protected endpoint without auth
            response = await client.get(f"{production_url}/api/v1/tasks")

            # Should return 401 or 403 (not 200)
            assert response.status_code in [401, 403], (
                f"Protected endpoint returned {response.status_code}, "
                f"expected 401 or 403 for unauthenticated request"
            )

    @pytest.mark.asyncio
    async def test_valid_token_allows_access(self, production_url, valid_token):
        """
        Valid JWT tokens MUST allow access to protected endpoints.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {valid_token}"}
            )

            # Should return 200 (success) or 404 (no tasks found)
            # But NOT 401 or 403
            assert response.status_code not in [401, 403], (
                f"Valid token returned {response.status_code}, "
                f"expected 200 or 404 for authenticated request. "
                f"Response: {response.text}"
            )

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, production_url, expired_token):
        """
        Expired JWT tokens MUST be rejected.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {expired_token}"}
            )

            # Should return 401 (unauthorized)
            assert response.status_code == 401, (
                f"Expired token returned {response.status_code}, "
                f"expected 401 for expired token"
            )

    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self, production_url):
        """
        Tokens with invalid signatures MUST be rejected.
        """
        import os

        # Create a token with wrong secret
        wrong_secret = "wrong-secret-key-for-testing"
        payload = {
            "sub": "test-user-id",
            "user_id": "test-user-id",
            "exp": 9999999999
        }
        invalid_token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {invalid_token}"}
            )

            # Should return 401 (unauthorized)
            assert response.status_code == 401, (
                f"Invalid signature token returned {response.status_code}, "
                f"expected 401 for invalid signature"
            )

    @pytest.mark.asyncio
    async def test_malformed_token_rejected(self, production_url):
        """
        Malformed JWT tokens MUST be rejected.
        """
        malformed_tokens = [
            "not-a-jwt-at-all",
            "Bearer",  # No token
            "Bearer.incomplete.token",
            "",  # Empty
        ]

        for token in malformed_tokens:
            async with httpx.AsyncClient() as client:
                auth_header = f"Bearer {token}" if token else ""
                response = await client.get(
                    f"{production_url}/api/v1/tasks",
                    headers={"Authorization": auth_header} if auth_header else {}
                )

                assert response.status_code in [401, 403], (
                    f"Malformed token '{token[:20]}...' returned {response.status_code}, "
                    f"expected 401 or 403"
                )
