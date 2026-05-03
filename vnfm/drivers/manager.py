import pluggy
from typing import Dict, Optional

from vnfm.drivers.specs import VimDriverSpec


class VimDriverManager:
    def __init__(self):
        self.pm = pluggy.PluginManager("vnfm.vim")
        self.pm.add_hookspecs(VimDriverSpec)
        self._drivers: Dict[str, any] = {}

    def register(self, driver):
        self.pm.register(driver)
        vim_type = driver.get_vim_type()
        self._drivers[vim_type.upper()] = driver

    def unregister(self, driver):
        self.pm.unregister(driver)
        vim_type = driver.get_vim_type()
        self._drivers.pop(vim_type.upper(), None)

    def get_driver(self, vim_type: str):
        driver = self._drivers.get(vim_type.upper())
        if not driver:
            raise ValueError(f"No driver registered for VIM type: {vim_type}")
        return driver

    def list_drivers(self):
        return list(self._drivers.keys())

    async def call(self, vim_type: str, method: str, *args, **kwargs):
        driver = self.get_driver(vim_type)
        func = getattr(driver, method, None)
        if not func:
            raise ValueError(f"Driver {vim_type} has no method {method}")
        return await func(*args, **kwargs)


vim_manager = VimDriverManager()
