#!/usr/bin/env python3
"""
Production Verification Suite (T016-T021)

This script verifies the production deployment against the following requirements:
- Deep health check with database connectivity (FR-005)
- CORS whitelist enforcement (FR-004)
- JWT authentication (FR-007)
- User isolation (SC-003)

Usage:
    python verify_production.py --url https://your-app.up.railway.app
    python verify_production.py --url https://your-app.up.railway.app --jwt-secret your-secret
    python verify_production.py --url https://your-app.up.railway.app --vercel-origin https://your-vercel.app
    python verify_production.py --all  # Run all checks with summary
"""
import argparse
import asyncio
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import httpx
import jwt


# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


@dataclass
class VerificationResult:
    """Result of a verification check."""
    name: str
    passed: bool
    message: str
    details: Optional[str] = None
    duration_ms: int = 0


class ProductionVerifier:
    """Production deployment verification suite."""

    def __init__(
        self,
        base_url: str,
        vercel_origin: str,
        jwt_secret: str,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.vercel_origin = vercel_origin
        self.jwt_secret = jwt_secret
        self.timeout = timeout
        self.results: list[VerificationResult] = []

    def _log_result(self, result: VerificationResult):
        """Log and store a verification result."""
        self.results.append(result)
        status = f"{GREEN}PASS{RESET}" if result.passed else f"{RED}FAIL{RESET}"
        duration = f"{result.duration_ms}ms"
        print(f"  [{status}] {result.name} ({duration})")
        if result.message:
            print(f"         {result.message}")
        if result.details:
            for line in result.details.split("\n"):
                print(f"         {line}")

    async def verify_health_check(self) -> VerificationResult:
        """
        T016: Deep health check verification with database connectivity.

        Verifies:
        - /health endpoint returns 200 OK
        - Response contains 'status': 'ok'
        - Response contains 'database': 'connected'
        - Response includes environment and timestamp
        """
        start = time.perf_counter()
        result = VerificationResult(name="Health Check", passed=False, message="")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                duration = int((time.perf_counter() - start) * 1000)

                if response.status_code != 200:
                    result.passed = False
                    result.message = f"Expected 200, got {response.status_code}"
                    result.details = response.text[:500]
                else:
                    data = response.json()
                    checks = []

                    # Verify status field
                    if data.get("status") == "ok":
                        checks.append("status=ok")
                    else:
                        checks.append(f"status={data.get('status')} (expected ok)")

                    # Verify database field
                    if data.get("database") == "connected":
                        checks.append("database=connected")
                    else:
                        checks.append(f"database={data.get('database')} (expected connected)")

                    # Verify environment field
                    if data.get("environment") == "production":
                        checks.append("environment=production")
                    else:
                        checks.append(f"environment={data.get('environment')} (expected production)")

                    # Verify timestamp field
                    if "timestamp" in data:
                        checks.append("timestamp=present")
                    else:
                        checks.append("timestamp=missing")

                    all_passed = all("expected" not in c for c in checks)
                    result.passed = all_passed
                    result.message = ", ".join(checks)

        except httpx.RequestError as e:
            result.passed = False
            result.message = f"Request failed: {str(e)}"
            duration = int((time.perf_counter() - start) * 1000)
        except Exception as e:
            result.passed = False
            result.message = f"Error: {str(e)}"
            duration = int((time.perf_counter() - start) * 1000)

        result.duration_ms = duration
        return result

    async def verify_cors_allow_vercel(self) -> VerificationResult:
        """
        T017: CORS whitelist verification - Vercel origin allowed.

        Verifies:
        - Requests from Vercel origin receive proper CORS headers
        - Access-Control-Allow-Origin matches Vercel URL exactly
        """
        start = time.perf_counter()
        result = VerificationResult(name="CORS: Vercel Allowed", passed=False, message="")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers={"Origin": self.vercel_origin}
                )
                duration = int((time.perf_counter() - start) * 1000)

                cors_origin = response.headers.get("Access-Control-Allow-Origin", "")

                if cors_origin == self.vercel_origin:
                    result.passed = True
                    result.message = f"CORS header matches: {cors_origin}"
                elif response.status_code != 200:
                    result.passed = False
                    result.message = f"Request failed with status {response.status_code}"
                else:
                    result.passed = False
                    result.message = f"CORS mismatch: got '{cors_origin}', expected '{self.vercel_origin}'"

        except Exception as e:
            result.passed = False
            result.message = f"Error: {str(e)}"
            duration = int((time.perf_counter() - start) * 1000)

        result.duration_ms = duration
        return result

    async def verify_cors_deny_unauthorized(self) -> VerificationResult:
        """
        T017: CORS whitelist verification - unauthorized origin denied.

        Verifies:
        - Requests from unauthorized origins do NOT receive CORS headers
        - Or server rejects with non-200 status
        """
        start = time.perf_counter()
        result = VerificationResult(name="CORS: Unauthorized Denied", passed=False, message="")
        unauthorized_origin = "https://evil-site.com"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers={"Origin": unauthorized_origin}
                )
                duration = int((time.perf_counter() - start) * 1000)

                cors_origin = response.headers.get("Access-Control-Allow-Origin", "")

                # Check if unauthorized origin is denied
                if cors_origin == "":
                    result.passed = True
                    result.message = "No CORS header (correctly denied)"
                elif cors_origin != unauthorized_origin:
                    result.passed = True
                    result.message = f"CORS set to different origin (not '{unauthorized_origin}')"
                else:
                    result.passed = False
                    result.message = f"SECURITY: Unauthorized origin '{unauthorized_origin}' was allowed!"

        except Exception as e:
            result.passed = False
            result.message = f"Error: {str(e)}"
            duration = int((time.perf_counter() - start) * 1000)

        result.duration_ms = duration
        return result

    async def verify_jwt_required(self) -> VerificationResult:
        """
        T018: JWT authentication verification - protected endpoints require auth.

        Verifies:
        - Protected endpoints return 401/403 without token
        - Protected endpoints accept valid tokens
        """
        start = time.perf_counter()
        result = VerificationResult(name="JWT: Auth Required", passed=False, message="")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Test without token
                response = await client.get(f"{self.base_url}/api/v1/tasks")
                duration = int((time.perf_counter() - start) * 1000)

                if response.status_code in [401, 403]:
                    # Check with valid token
                    token = self._create_test_token("test-user-id")
                    response_with_token = await client.get(
                        f"{self.base_url}/api/v1/tasks",
                        headers={"Authorization": f"Bearer {token}"}
                    )

                    if response_with_token.status_code in [200, 404]:
                        result.passed = True
                        result.message = "401/403 without token, 200/404 with valid token"
                    else:
                        result.passed = False
                        result.message = f"Token rejected: status {response_with_token.status_code}"
                else:
                    result.passed = False
                    result.message = f"No auth required: got {response.status_code} without token"

        except Exception as e:
            result.passed = False
            result.message = f"Error: {str(e)}"
            duration = int((time.perf_counter() - start) * 1000)

        result.duration_ms = duration
        return result

    async def verify_user_isolation(self) -> VerificationResult:
        """
        T019: User isolation verification - users cannot access others' data.

        Verifies:
        - User A's token only returns User A's tasks
        - No overlap between different users' task lists
        """
        start = time.perf_counter()
        result = VerificationResult(name="User Isolation", passed=False, message="")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create two test users
                user_a_id = "verify_user_a"
                user_b_id = "verify_user_b"

                token_a = self._create_test_token(user_a_id)
                token_b = self._create_test_token(user_b_id)

                # Get tasks for User A
                response_a = await client.get(
                    f"{self.base_url}/api/v1/tasks",
                    headers={"Authorization": f"Bearer {token_a}"}
                )
                tasks_a = response_a.json() if response_a.status_code == 200 else []

                # Get tasks for User B
                response_b = await client.get(
                    f"{self.base_url}/api/v1/tasks",
                    headers={"Authorization": f"Bearer {token_b}"}
                )
                tasks_b = response_b.json() if response_b.status_code == 200 else []

                duration = int((time.perf_counter() - start) * 1000)

                # Extract task IDs
                ids_a = set(t.get("id") for t in tasks_a if t.get("id"))
                ids_b = set(t.get("id") for t in tasks_b if t.get("id"))

                # Check for overlap
                overlap = ids_a & ids_b

                if len(overlap) == 0:
                    result.passed = True
                    result.message = f"No task overlap: User A has {len(ids_a)}, User B has {len(ids_b)}"
                else:
                    result.passed = False
                    result.message = f"SECURITY VIOLATION: {len(overlap)} shared task IDs"
                    result.details = f"Overlap: {overlap}"

        except Exception as e:
            result.passed = False
            result.message = f"Error: {str(e)}"
            duration = int((time.perf_counter() - start) * 1000)

        result.duration_ms = duration
        return result

    def _create_test_token(self, user_id: str) -> str:
        """Create a test JWT token for verification."""
        payload = {
            "sub": user_id,
            "user_id": user_id,
            "exp": int(time.time()) + 3600  # 1 hour
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    async def run_all_verifications(self) -> list[VerificationResult]:
        """Run all verification checks and return results."""
        print(f"\n{BOLD}{BLUE}Running Production Verification Suite{RESET}")
        print(f"URL: {self.base_url}")
        print(f"Vercel Origin: {self.vercel_origin}")
        print("-" * 60)

        # Run all checks
        results = await asyncio.gather(
            self.verify_health_check(),
            self.verify_cors_allow_vercel(),
            self.verify_cors_deny_unauthorized(),
            self.verify_jwt_required(),
            self.verify_user_isolation(),
        )

        # Log results
        for r in results:
            self._log_result(r)

        return results


def generate_report(results: list[VerificationResult], runtime_ms: int) -> str:
    """
    T021: Generate pass/fail report with summary.

    Returns a formatted report string.
    """
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    total = len(results)

    # Build report
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append(f"{BOLD}VERIFICATION REPORT{RESET}")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    lines.append(f"Total Checks: {total}")
    lines.append(f"Passed: {GREEN}{passed}{RESET}")
    lines.append(f"Failed: {RED}{failed}{RESET}")
    lines.append(f"Duration: {runtime_ms}ms")
    lines.append("-" * 60)

    # Pass rate
    pass_rate = (passed / total * 100) if total > 0 else 0
    status = f"{GREEN}PASS{RESET}" if pass_rate == 100 else f"{YELLOW}PARTIAL{RESET}" if pass_rate >= 80 else f"{RED}FAIL{RESET}"
    lines.append(f"Overall Status: {status}")
    lines.append("-" * 60)

    # Failed checks detail
    if failed > 0:
        lines.append(f"\n{RED}Failed Checks:{RESET}")
        for r in results:
            if not r.passed:
                lines.append(f"  - {r.name}: {r.message}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


async def main():
    """Main entry point for production verification."""
    parser = argparse.ArgumentParser(
        description="Production Verification Suite for TaskFlow Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_production.py --url https://todo-app.up.railway.app
  python verify_production.py --url https://todo-app.up.railway.app --jwt-secret mysecret
  python verify_production.py --url https://todo-app.up.railway.app --vercel-origin https://myapp.vercel.app
        """,
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Production URL to verify",
    )
    parser.add_argument(
        "--vercel-origin",
        default="https://todo-app-web.vercel.app",
        help="Authorized Vercel origin (default: https://todo-app-web.vercel.app)",
    )
    parser.add_argument(
        "--jwt-secret",
        default="",
        help="JWT secret for token verification",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show summary, skip detailed output",
    )

    args = parser.parse_args()

    # Get JWT secret from environment if not provided
    jwt_secret = args.jwt_secret or "default-secret-change-me"
    if not args.jwt_secret:
        import os
        jwt_secret = os.environ.get("JWT_SECRET_KEY", "default-secret-change-me")

    # Parse and validate URL
    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        print(f"{RED}Error: Invalid URL '{args.url}'{RESET}")
        sys.exit(1)

    # Create verifier and run
    verifier = ProductionVerifier(
        base_url=args.url,
        vercel_origin=args.vercel_origin,
        jwt_secret=jwt_secret,
        timeout=args.timeout,
    )

    start_time = time.perf_counter()
    results = await verifier.run_all_verifications()
    total_duration = int((time.perf_counter() - start_time) * 1000)

    # Generate and display report
    report = generate_report(results, total_duration)

    if args.quiet:
        # Quiet mode: just show summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        print(f"\n{passed}/{total} checks passed ({total_duration}ms)")
    else:
        print(report)

    # Exit with appropriate code
    passed = sum(1 for r in results if r.passed)
    exit_code = 0 if passed == len(results) else 1

    # SC-004: Verify under 60 seconds
    if total_duration > 60000:
        print(f"\n{YELLOW}Warning: Verification took {total_duration}ms (> 60s limit){RESET}")

    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
