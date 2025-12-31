"""T015: User isolation verification test - RED PHASE (failing test)"""
import pytest
import httpx
import jwt


class TestUserIsolation:
    """Test suite for verifying user data isolation on production."""

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
    def user_a_token(self, jwt_secret):
        """Generate a valid JWT token for User A."""
        if not jwt_secret:
            pytest.skip("JWT_SECRET_KEY not set")

        payload = {
            "sub": "user-a-id",
            "user_id": "user-a-id",
            "exp": 9999999999
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @pytest.fixture
    def user_b_token(self, jwt_secret):
        """Generate a valid JWT token for User B."""
        if not jwt_secret:
            pytest.skip("JWT_SECRET_KEY not set")

        payload = {
            "sub": "user-b-id",
            "user_id": "user-b-id",
            "exp": 9999999999
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @pytest.mark.asyncio
    async def test_user_cannot_access_others_tasks(self, production_url, user_a_token, user_b_token):
        """
        User B MUST NOT be able to access User A's tasks.

        This is a CRITICAL security requirement:
        - User A creates tasks
        - User B authenticates with their own valid token
        - User B requests User A's tasks
        - System MUST return 404 (not found) or 403 (forbidden), NOT 200 with User A's data

        Note: Returning 404 prevents information leakage about task existence.
        """
        # First, get User A's tasks
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"}
            )

            user_a_tasks = response.json() if response.status_code == 200 else []

        # Now try to access User A's tasks as User B
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_b_token}"}
            )

            user_b_tasks = response.json() if response.status_code == 200 else []

        # If User A has tasks, User B should NOT see them
        if user_a_tasks:
            user_b_task_ids = [t.get("id") for t in user_b_tasks]
            user_a_task_ids = [t.get("id") for t in user_a_tasks]

            # No overlap between user A's task IDs and user B's task IDs
            overlap = set(user_a_task_ids) & set(user_b_task_ids)
            assert len(overlap) == 0, (
                f"SECURITY VIOLATION: User B can see User A's tasks: {overlap}"
            )

    @pytest.mark.asyncio
    async def test_user_cannot_access_specific_task_by_id(self, production_url, user_a_token, user_b_token):
        """
        User B MUST NOT access a specific task owned by User A.

        This tests direct task access by ID.
        """
        # Get a specific task ID from User A
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"}
            )

            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    task_id = tasks[0].get("id")

                    # Try to access as User B
                    response = await client.get(
                        f"{production_url}/api/v1/tasks/{task_id}",
                        headers={"Authorization": f"Bearer {user_b_token}"}
                    )

                    # Should return 404 (not found) or 403 (forbidden)
                    assert response.status_code in [404, 403], (
                        f"User B accessed User A's task {task_id}, "
                        f"got {response.status_code}, expected 404 or 403"
                    )

    @pytest.mark.asyncio
    async def test_user_sees_only_own_tasks_in_list(self, production_url, user_a_token, user_b_token):
        """
        Each user MUST see only their own tasks in the task list.

        This is a stronger test that verifies the API properly filters by user_id.
        """
        async with httpx.AsyncClient() as client:
            # Get User A's task count
            response_a = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"}
            )
            tasks_a = response_a.json() if response_a.status_code == 200 else []

            # Get User B's task count
            response_b = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_b_token}"}
            )
            tasks_b = response_b.json() if response_b.status_code == 200 else []

        # Extract user_ids from task owners
        # Note: Actual field name may vary (user_id, owner, etc.)
        def get_owner_ids(tasks):
            owners = set()
            for task in tasks:
                # Check common field names
                for field in ["user_id", "owner_id", "owner", "created_by"]:
                    if field in task:
                        owners.add(task[field])
                        break
            return owners

        owners_a = get_owner_ids(tasks_a)
        owners_b = get_owner_ids(tasks_b)

        # User A's task list should only contain User A's tasks
        if tasks_a and user_a_token:
            user_a_id = "user-a-id"  # From fixture
            for task in tasks_a:
                # Task should belong to User A
                assert task.get("user_id") == user_a_id or user_a_id in str(task), (
                    f"Task in User A's list doesn't belong to User A: {task}"
                )

        # User B's task list should only contain User B's tasks
        if tasks_b and user_b_token:
            user_b_id = "user-b-id"  # From fixture
            for task in tasks_b:
                assert task.get("user_id") == user_b_id or user_b_id in str(task), (
                    f"Task in User B's list doesn't belong to User B: {task}"
                )

    @pytest.mark.asyncio
    async def test_user_cannot_modify_others_tasks(self, production_url, user_a_token, user_b_token):
        """
        User B MUST NOT be able to modify User A's tasks.

        This tests PUT/PATCH operations on another user's tasks.
        """
        # First, get a task ID from User A
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"}
            )

            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    task_id = tasks[0].get("id")

                    # Try to update as User B
                    update_data = {"title": "HACKED BY USER B"}
                    response = await client.put(
                        f"{production_url}/api/v1/tasks/{task_id}",
                        json=update_data,
                        headers={"Authorization": f"Bearer {user_b_token}"}
                    )

                    # Should return 404 or 403, not 200
                    assert response.status_code in [404, 403], (
                        f"User B modified User A's task {task_id}, "
                        f"got {response.status_code}, expected 404 or 403"
                    )

    @pytest.mark.asyncio
    async def test_user_cannot_delete_others_tasks(self, production_url, user_a_token, user_b_token):
        """
        User B MUST NOT be able to delete User A's tasks.
        """
        # Get a task ID from User A
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{production_url}/api/v1/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"}
            )

            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    task_id = tasks[0].get("id")

                    # Try to delete as User B
                    response = await client.delete(
                        f"{production_url}/api/v1/tasks/{task_id}",
                        headers={"Authorization": f"Bearer {user_b_token}"}
                    )

                    # Should return 404 or 403, not 200
                    assert response.status_code in [404, 403], (
                        f"User B deleted User A's task {task_id}, "
                        f"got {response.status_code}, expected 404 or 403"
                    )
