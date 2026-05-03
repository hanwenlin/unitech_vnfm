import pytest


class TestCatalog:
    async def test_create_vnf_package(self, authorized_client):
        payload = {
            "name": "test-package",
            "description": "A test package",
            "vnfd_id": "vnfd-test-001",
            "provider": "test-provider",
            "tosca_template": """
tosca_definitions_version: tosca_simple_yaml_1_2
description: Test VNF
topology_template:
  node_templates:
    VDU1:
      type: tosca.nodes.nfv.Vdu.Compute
""",
        }
        response = await authorized_client.post("/api/v1/catalog/vnf_packages", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-package"
        assert data["vnfd_id"] == "vnfd-test-001"
        assert data["onboarding_state"] == "ONBOARDED"

    async def test_create_vnf_package_invalid_tosca(self, authorized_client):
        payload = {
            "name": "bad-package",
            "vnfd_id": "vnfd-bad-001",
            "tosca_template": "invalid yaml: :::",
        }
        response = await authorized_client.post("/api/v1/catalog/vnf_packages", json=payload)
        assert response.status_code == 400

    async def test_list_vnf_packages(self, authorized_client):
        response = await authorized_client.get("/api/v1/catalog/vnf_packages")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    async def test_get_vnf_package(self, authorized_client):
        create_resp = await authorized_client.post(
            "/api/v1/catalog/vnf_packages",
            json={
                "name": "pkg-get",
                "vnfd_id": "vnfd-get-001",
            },
        )
        pkg_id = create_resp.json()["id"]

        response = await authorized_client.get(f"/api/v1/catalog/vnf_packages/{pkg_id}")
        assert response.status_code == 200
        assert response.json()["id"] == pkg_id

    async def test_get_vnf_package_not_found(self, authorized_client):
        response = await authorized_client.get("/api/v1/catalog/vnf_packages/nonexistent")
        assert response.status_code == 404

    async def test_delete_vnf_package(self, authorized_client):
        create_resp = await authorized_client.post(
            "/api/v1/catalog/vnf_packages",
            json={
                "name": "pkg-delete",
                "vnfd_id": "vnfd-del-001",
            },
        )
        pkg_id = create_resp.json()["id"]

        response = await authorized_client.delete(f"/api/v1/catalog/vnf_packages/{pkg_id}")
        assert response.status_code == 204

        get_resp = await authorized_client.get(f"/api/v1/catalog/vnf_packages/{pkg_id}")
        assert get_resp.status_code == 404
