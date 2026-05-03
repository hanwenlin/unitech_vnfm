import logging
from vnfm.drivers.specs import hookimpl
from vnfm.common.constants import VimType

logger = logging.getLogger(__name__)


class OpenStackVimDriver:
    @hookimpl
    def get_vim_type(self) -> str:
        return VimType.OPENSTACK.value

    @hookimpl
    async def create(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] create vnf={vnf_instance.id}")
        return {"status": "created", "vim_type": "openstack"}

    @hookimpl
    async def instantiate(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] instantiate vnf={vnf_instance.id}")
        return {"status": "active", "servers": []}

    @hookimpl
    async def scale_in(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] scale_in vnf={vnf_instance.id}")
        return {"status": "scaled_in"}

    @hookimpl
    async def scale_out(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] scale_out vnf={vnf_instance.id}")
        return {"status": "scaled_out"}

    @hookimpl
    async def update_image(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] update_image vnf={vnf_instance.id}")
        return {"status": "updated"}

    @hookimpl
    async def update(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] update vnf={vnf_instance.id}")
        return {"status": "updated"}

    @hookimpl
    async def terminate(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] terminate vnf={vnf_instance.id}")
        return {"status": "terminated"}

    @hookimpl
    async def delete(self, context, vnf_instance, params):
        logger.info(f"[OpenStack] delete vnf={vnf_instance.id}")
        return {"status": "deleted"}

    @hookimpl
    async def status(self, context, vnf_instance):
        logger.info(f"[OpenStack] status vnf={vnf_instance.id}")
        return {"status": "active", "servers": []}
