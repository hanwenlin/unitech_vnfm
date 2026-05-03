import logging
from vnfm.drivers.specs import hookimpl
from vnfm.common.constants import VimType

logger = logging.getLogger(__name__)


class K8sVimDriver:
    @hookimpl
    def get_vim_type(self) -> str:
        return VimType.KUBERNETES.value

    @hookimpl
    async def create(self, context, vnf_instance, params):
        logger.info(f"[K8s] create vnf={vnf_instance.id}")
        return {"status": "created", "vim_type": "kubernetes"}

    @hookimpl
    async def instantiate(self, context, vnf_instance, params):
        logger.info(f"[K8s] instantiate vnf={vnf_instance.id}")
        namespace = params.get("namespace", "default")
        return {"status": "active", "namespace": namespace, "pods": []}

    @hookimpl
    async def scale_in(self, context, vnf_instance, params):
        logger.info(f"[K8s] scale_in vnf={vnf_instance.id}")
        return {"status": "scaled_in"}

    @hookimpl
    async def scale_out(self, context, vnf_instance, params):
        logger.info(f"[K8s] scale_out vnf={vnf_instance.id}")
        return {"status": "scaled_out"}

    @hookimpl
    async def update_image(self, context, vnf_instance, params):
        logger.info(f"[K8s] update_image vnf={vnf_instance.id}")
        return {"status": "updated"}

    @hookimpl
    async def update(self, context, vnf_instance, params):
        logger.info(f"[K8s] update vnf={vnf_instance.id}")
        return {"status": "updated"}

    @hookimpl
    async def terminate(self, context, vnf_instance, params):
        logger.info(f"[K8s] terminate vnf={vnf_instance.id}")
        return {"status": "terminated"}

    @hookimpl
    async def delete(self, context, vnf_instance, params):
        logger.info(f"[K8s] delete vnf={vnf_instance.id}")
        return {"status": "deleted"}

    @hookimpl
    async def status(self, context, vnf_instance):
        logger.info(f"[K8s] status vnf={vnf_instance.id}")
        return {"status": "active", "pods": []}
