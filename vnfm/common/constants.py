from enum import Enum


class InstantiationState(str, Enum):
    NOT_INSTANTIATED = "NOT_INSTANTIATED"
    INSTANTIATED = "INSTANTIATED"


class TaskState(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    TERMINATING = "TERMINATING"
    SCALING = "SCALING"
    UPDATING = "UPDATING"


class LcmOperationType(str, Enum):
    INSTANTIATE = "INSTANTIATE"
    SCALE = "SCALE"
    SCALE_TO_LEVEL = "SCALE_TO_LEVEL"
    TERMINATE = "TERMINATE"
    UPDATE = "UPDATE"
    HEAL = "HEAL"
    CHANGE_EXT_CONN = "CHANGE_EXT_CONN"


class LcmOperationStatus(str, Enum):
    STARTING = "STARTING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"


class ResourceType(str, Enum):
    VDU = "VDU"
    CP = "CP"
    VL = "VL"
    STORAGE = "STORAGE"


class VimType(str, Enum):
    KUBERNETES = "KUBERNETES"
    OPENSTACK = "OPENSTACK"
