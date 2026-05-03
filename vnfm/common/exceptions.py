class VnfmException(Exception):
    pass


class VnfdValidationError(VnfmException):
    pass


class VnfNotFound(VnfmException):
    pass


class VimDriverError(VnfmException):
    pass


class AuthError(VnfmException):
    pass


class VnfInstanceConflictState(VnfmException):
    def __init__(self, attr, uuid, state, action):
        self.attr = attr
        self.uuid = uuid
        self.state = state
        self.action = action
        super().__init__(
            f"VNF instance {uuid} has invalid {attr}='{state.value if hasattr(state, 'value') else state}' "
            f"for action '{action}'"
        )