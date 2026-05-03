import pytest


class TestAuth:
    async def test_login_success(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "nobody", "password": "pass"},
        )
        assert response.status_code == 401

    async def test_access_protected_without_token(self, client):
        response = await client.get("/api/v1/vnflcm/vnf_instances")
        assert response.status_code == 401

    async def test_access_protected_with_token(self, authorized_client):
        response = await authorized_client.get("/api/v1/vnflcm/vnf_instances")
        assert response.status_code == 200
