import pytest


class TestVnfLcm:
    @pytest.fixture
    async def sample_package(self, authorized_client):
        resp = await authorized_client.post(
            "/api/v1/catalog/vnf_packages",
            json={
                "name": "sample-pkg",
                "vnfd_id": "vnfd-sample-001",
            },
        )
        return resp.json()

    @pytest.fixture
    async def sample_vim(self, authorized_client):
        resp = await authorized_client.post(
            "/api/v1/vim/vim_auths",
            json={
                "name": "sample-vim",
                "vim_type": "KUBERNETES",
                "vim_url": "https://k8s.example.com",
            },
        )
        return resp.json()

    async def test_create_vnf_instance(self, authorized_client, sample_package, sample_vim):
        payload = {
            "name": "test-vnf",
            "description": "Test VNF instance",
            "vnf_package_id": sample_package["id"],
            "vnfd_id": sample_package["vnfd_id"],
            "vim_id": sample_vim["id"],
        }
        response = await authorized_client.post("/api/v1/vnflcm/vnf_instances", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-vnf"
        assert data["task_state"] == "PENDING"
        assert data["instantiation_state"] == "NOT_INSTANTIATED"

    async def test_list_vnf_instances(self, authorized_client):
        response = await authorized_client.get("/api/v1/vnflcm/vnf_instances")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    async def test_get_vnf_instance(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "get-vnf",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.get(f"/api/v1/vnflcm/vnf_instances/{vnf_id}")
        assert response.status_code == 200
        assert response.json()["id"] == vnf_id

    async def test_get_vnf_instance_not_found(self, authorized_client):
        response = await authorized_client.get("/api/v1/vnflcm/vnf_instances/nonexistent")
        assert response.status_code == 404

    async def test_instantiate_vnf(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "inst-vnf",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/instantiate",
            json={"params": {}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "INSTANTIATE"
        assert data["status"] == "accepted"

    async def test_instantiate_vnf_not_pending(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "inst-twice",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        # First instantiate
        await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/instantiate",
            json={"params": {}},
        )

        # Second instantiate should fail
        response = await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/instantiate",
            json={"params": {}},
        )
        assert response.status_code == 409

    async def test_terminate_vnf(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "term-vnf",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/terminate",
            json={"params": {}},
        )
        assert response.status_code == 200
        assert response.json()["operation"] == "TERMINATE"

    async def test_terminate_pending_vnf_fails(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "term-pending",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/terminate",
            json={"params": {}},
        )
        assert response.status_code == 409

    async def test_scale_vnf(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "scale-vnf",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/scale",
            json={"params": {"type": "scale_out"}},
        )
        assert response.status_code == 200
        assert response.json()["operation"] == "SCALE_OUT"

    async def test_scale_vnf_not_active_fails(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "scale-fail",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.post(
            f"/api/v1/vnflcm/vnf_instances/{vnf_id}/scale",
            json={"params": {"type": "scale_out"}},
        )
        assert response.status_code == 409

    async def test_delete_vnf_instance(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "del-vnf",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.delete(f"/api/v1/vnflcm/vnf_instances/{vnf_id}")
        assert response.status_code == 204

        get_resp = await authorized_client.get(f"/api/v1/vnflcm/vnf_instances/{vnf_id}")
        assert get_resp.status_code == 404

    async def test_lifecycle_events(self, authorized_client, sample_package, sample_vim):
        create_resp = await authorized_client.post(
            "/api/v1/vnflcm/vnf_instances",
            json={
                "name": "lcm-vnf",
                "vnf_package_id": sample_package["id"],
                "vnfd_id": sample_package["vnfd_id"],
                "vim_id": sample_vim["id"],
            },
        )
        vnf_id = create_resp.json()["id"]

        response = await authorized_client.get(f"/api/v1/vnflcm/vnf_instances/{vnf_id}/lifecycle")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
