import pluggy

hookspec = pluggy.HookspecMarker("vnfm.vim")
hookimpl = pluggy.HookimplMarker("vnfm.vim")


class VimDriverSpec:
    @hookspec
    def get_vim_type(self) -> str:
        """Return the VIM type string, e.g. 'KUBERNETES' or 'OPENSTACK'."""

    @hookspec
    async def create(self, context, vnf_instance, params):
        """Create underlying resources for a VNF."""

    @hookspec
    async def instantiate(self, context, vnf_instance, params):
        """Instantiate a VNF on the VIM."""

    @hookspec
    async def scale_in(self, context, vnf_instance, params):
        """Scale in a VNF."""

    @hookspec
    async def scale_out(self, context, vnf_instance, params):
        """Scale out a VNF."""

    @hookspec
    async def update_image(self, context, vnf_instance, params):
        """Update VNF image."""

    @hookspec
    async def update(self, context, vnf_instance, params):
        """Update VNF configuration."""

    @hookspec
    async def terminate(self, context, vnf_instance, params):
        """Terminate a VNF."""

    @hookspec
    async def delete(self, context, vnf_instance, params):
        """Delete a VNF and all its resources."""

    @hookspec
    async def status(self, context, vnf_instance):
        """Get VNF status from VIM."""
