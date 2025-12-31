"""T013: CORS enforcement verification test - RED PHASE (failing test)"""
import pytest
import httpx


class TestCORSEnforcement:
    """Test suite for verifying CORS security hardening on production."""

    @pytest.fixture
    def production_url(self):
        """Return the production Railway URL from environment or default."""
        import os
        return os.environ.get("PRODUCTION_URL", "https://todo-app.up.railway.app")

    @pytest.fixture
    def vercel_origin(self):
        """Return the authorized Vercel production domain."""
        import os
        return os.environ.get("VERCEL_ORIGIN", "https://todo-app-web.vercel.app")

    @pytest.fixture
    def unauthorized_origin(self):
        """Return a non-Vercel origin that should be blocked."""
        return "https://evil-site.com"

    @pytest.mark.asyncio
    async def test_vercel_origin_allowed(self, production_url, vercel_origin):
        """
        FR-004: CORS MUST allow requests from authorized Vercel production domain.

        This test verifies that:
        1. Requests from Vercel domain include proper CORS headers
        2. Access-Control-Allow-Origin matches the Vercel URL exactly
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/health",
                headers={"Origin": vercel_origin}
            )

            # Assert CORS headers are present for authorized origin
            assert response.status_code == 200, (
                f"Request from Vercel origin failed with status {response.status_code}"
            )

            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            assert cors_origin == vercel_origin, (
                f"CORS origin is '{cors_origin}', expected '{vercel_origin}'"
            )

    @pytest.mark.asyncio
    async def test_unauthorized_origin_denied(self, production_url, unauthorized_origin):
        """
        FR-004: CORS MUST deny requests from non-Vercel domains.

        This test verifies that:
        1. Requests from unauthorized domains do NOT include CORS headers
        2. Or the server rejects the request with 403/any non-200 status
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/health",
                headers={"Origin": unauthorized_origin}
            )

            # Non-Vercel origins should either:
            # a) Not receive CORS headers, OR
            # b) Receive a 403/4xx response

            cors_origin = response.headers.get("Access-Control-Allow-Origin")

            # Either no CORS header OR it's not the unauthorized origin
            if cors_origin is not None:
                assert cors_origin != unauthorized_origin, (
                    f"CORS should NOT allow unauthorized origin '{unauthorized_origin}'"
                )

    @pytest.mark.asyncio
    async def test_no_origin_header(self, production_url):
        """
        Requests without Origin header should succeed (same-origin requests).
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{production_url}/health")

            assert response.status_code == 200, (
                f"Same-origin request failed with status {response.status_code}"
            )

    @pytest.mark.asyncio
    async def test_cors_credentials_allowed(self, production_url, vercel_origin):
        """
        FR-004: CORS SHOULD allow credentials for authorized origins.

        This verifies that credentials (cookies/auth) can be sent.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/health",
                headers={"Origin": vercel_origin}
            )

            # Check if credentials are allowed
            # Access-Control-Allow-Credentials should be true
            # Note: This may not apply to health endpoint, but verify if present
            if "Access-Control-Allow-Credentials" in response.headers:
                creds = response.headers.get("Access-Control-Allow-Credentials")
                assert creds.lower() == "true", (
                    f"Credentials header is '{creds}', expected 'true'"
                )
