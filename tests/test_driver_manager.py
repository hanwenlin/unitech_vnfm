import pytest
from vnfm.drivers.manager import VimDriverManager
from vnfm.drivers.specs import VimDriverSpec
from vnfm.common.constants import VimType


class DummyK8sDriver:
    def get_vim_type(self):
        return VimType.KUBERNETES.value

    async def create(self, context, vnf_instance, params):
        return {"status": "created"}


class DummyOpenStackDriver:
    def get_vim_type(self):
        return VimType.OPENSTACK.value

    async def create(self, context, vnf_instance, params):
        return {"status": "created"}


class TestVimDriverManager:
    @pytest.fixture
    def manager(self):
        return VimDriverManager()

    def test_register_and_get_driver(self, manager):
        driver = DummyK8sDriver()
        manager.register(driver)
        assert VimType.KUBERNETES.value in manager.list_drivers()
        assert manager.get_driver("KUBERNETES") == driver
        assert manager.get_driver("kubernetes") == driver

    def test_unregister_driver(self, manager):
        driver = DummyK8sDriver()
        manager.register(driver)
        manager.unregister(driver)
        assert VimType.KUBERNETES.value not in manager.list_drivers()

    def test_get_driver_not_found(self, manager):
        with pytest.raises(ValueError):
            manager.get_driver("UNKNOWN")

    def test_register_multiple(self, manager):
        k8s = DummyK8sDriver()
        os_driver = DummyOpenStackDriver()
        manager.register(k8s)
        manager.register(os_driver)
        assert len(manager.list_drivers()) == 2

    @pytest.mark.asyncio
    async def test_call_driver_method(self, manager):
        driver = DummyK8sDriver()
        manager.register(driver)
        result = await manager.call("KUBERNETES", "create", {}, None, {})
        assert result == {"status": "created"}

    @pytest.mark.asyncio
    async def test_call_driver_method_not_found(self, manager):
        driver = DummyK8sDriver()
        manager.register(driver)
        with pytest.raises(ValueError):
            await manager.call("KUBERNETES", "nonexistent", {}, None, {})
