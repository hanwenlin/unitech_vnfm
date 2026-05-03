import pytest


class TestVim:
    async def test_create_vim_auth(self, authorized_client):
        payload = {
            "name": "k8s-test",
            "vim_type": "KUBERNETES",
            "vim_url": "https://k8s.example.com",
            "username": "admin",
            "password": "secret",
            "is_default": True,
        }
        response = await authorized_client.post("/api/v1/vim/vim_auths", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "k8s-test"
        assert data["vim_type"] == "KUBERNETES"

    async def test_list_vim_auths(self, authorized_client):
        response = await authorized_client.get("/api/v1/vim/vim_auths")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    async def test_get_vim_auth(self, authorized_client):
        create_resp = await authorized_client.post(
            "/api/v1/vim/vim_auths",
            json={
                "name": "os-test",
                "vim_type": "OPENSTACK",
                "vim_url": "https://os.example.com",
            },
        )
        vim_id = create_resp.json()["id"]

        response = await authorized_client.get(f"/api/v1/vim/vim_auths/{vim_id}")
        assert response.status_code == 200
        assert response.json()["id"] == vim_id

    async def test_get_vim_auth_not_found(self, authorized_client):
        response = await authorized_client.get("/api/v1/vim/vim_auths/nonexistent")
        assert response.status_code == 404

    async def test_delete_vim_auth(self, authorized_client):
        create_resp = await authorized_client.post(
            "/api/v1/vim/vim_auths",
            json={
                "name": "vim-del",
                "vim_type": "KUBERNETES",
                "vim_url": "https://del.example.com",
            },
        )
        vim_id = create_resp.json()["id"]

        response = await authorized_client.delete(f"/api/v1/vim/vim_auths/{vim_id}")
        assert response.status_code == 204

        get_resp = await authorized_client.get(f"/api/v1/vim/vim_auths/{vim_id}")
        assert get_resp.status_code == 404
