"""
Integration tests for authentication, legacy user password setup,
pending approvals, session revocation, and admin endpoints.
"""

import pytest
import pytest_asyncio
import httpx
import time
from main import app


@pytest.mark.asyncio
async def test_full_auth_lifecycle():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200

        # 2. Unknown username pays scrypt and returns 401
        res = await client.post(
            "/api/auth/login",
            json={"username": "unknown_user_test", "password": "WrongPassword123!"},
        )
        assert res.status_code == 401

        # 3. Setup password for brian
        res = await client.post(
            "/api/auth/setup-password",
            json={
                "username": "brian",
                "password": "BrianPassword123!",
                "confirm_password": "BrianPassword123!",
            },
        )
        # Either 200 (first time) or 400 (already set)
        if res.status_code == 200:
            token = res.json()["token"]
            assert "infreight_session=" in res.headers.get("set-cookie", "")
        else:
            # Login if password already set
            login_res = await client.post(
                "/api/auth/login",
                json={"username": "brian", "password": "BrianPassword123!"},
            )
            assert login_res.status_code == 200
            token = login_res.json()["token"]

        # 4. Profile check (/api/auth/me)
        me_res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me = me_res.json()["user"]
        assert me["username"] == "brian"
        assert me["role"] == "admin"

        # 5. Wrong password returns 401
        wrong_res = await client.post(
            "/api/auth/login",
            json={"username": "brian", "password": "IncorrectPassword!"},
        )
        assert wrong_res.status_code == 401

        # 6. Admin overview
        admin_res = await client.get("/api/admin/overview", headers={"Authorization": f"Bearer {token}"})
        assert admin_res.status_code == 200
        overview = admin_res.json()
        assert "users" in overview
        assert "stats" in overview
        assert "audit" in overview

        # 7. Register a new user
        test_username = f"hire_{int(time.time())}"
        signup_res = await client.post(
            "/api/auth/signup",
            json={
                "displayName": "New Member",
                "username": test_username,
                "password": "NewMemberPass123!",
            },
        )
        assert signup_res.status_code == 200
        new_user = signup_res.json()["user"]
        assert new_user["status"] == "pending"

        # 8. Pending member cannot log in yet
        blocked_res = await client.post(
            "/api/auth/login",
            json={"username": test_username, "password": "NewMemberPass123!"},
        )
        assert blocked_res.status_code == 403
        assert "waiting for admin approval" in blocked_res.json()["detail"]

        # 9. Admin approves new member
        uid = new_user["id"]
        approve_res = await client.post(
            f"/api/admin/users/{uid}/approve",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["user"]["status"] == "active"

        # 10. Approved member can now log in
        member_login = await client.post(
            "/api/auth/login",
            json={"username": test_username, "password": "NewMemberPass123!"},
        )
        assert member_login.status_code == 200
        member_token = member_login.json()["token"]

        # 11. Member cannot access admin overview
        forbidden_res = await client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert forbidden_res.status_code == 403

        # 12. Admin disables member -> member session revoked
        disable_res = await client.post(
            f"/api/admin/users/{uid}/disable",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert disable_res.status_code == 200

        # Member is immediately unauthorized on next request
        check_member = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert check_member.status_code == 401

        # 13. Admin deletes member
        del_res = await client.delete(
            f"/api/admin/users/{uid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert del_res.status_code == 200

        # 14. Admin self-protection: cannot delete self
        self_del_res = await client.delete(
            f"/api/admin/users/{me['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert self_del_res.status_code == 400
        assert "cannot delete your own account" in self_del_res.json()["detail"]
