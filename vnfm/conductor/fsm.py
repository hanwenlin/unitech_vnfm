from enum import Enum
from typing import Dict, Callable, Optional, Any
import logging

from vnfm.common.constants import TaskState, LcmOperationType, LcmOperationStatus
from vnfm.db.models import VnfInstance

logger = logging.getLogger(__name__)


class FSMEvent(str, Enum):
    INSTANTIATE = "INSTANTIATE"
    SCALE_IN = "SCALE_IN"
    SCALE_OUT = "SCALE_OUT"
    UPDATE = "UPDATE"
    TERMINATE = "TERMINATE"
    DELETE = "DELETE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


class VnfFsm:
    TRANSITIONS: Dict[tuple, TaskState] = {
        (TaskState.PENDING, FSMEvent.INSTANTIATE): TaskState.PROCESSING,
        (TaskState.PENDING, FSMEvent.UPDATE): TaskState.UPDATING,
        (TaskState.PENDING, FSMEvent.DELETE): TaskState.TERMINATING,
        (TaskState.ACTIVE, FSMEvent.SCALE_IN): TaskState.SCALING,
        (TaskState.ACTIVE, FSMEvent.SCALE_OUT): TaskState.SCALING,
        (TaskState.ACTIVE, FSMEvent.UPDATE): TaskState.UPDATING,
        (TaskState.ACTIVE, FSMEvent.TERMINATE): TaskState.TERMINATING,
        (TaskState.ACTIVE, FSMEvent.DELETE): TaskState.TERMINATING,
        (TaskState.PROCESSING, FSMEvent.COMPLETE): TaskState.ACTIVE,
        (TaskState.PROCESSING, FSMEvent.FAIL): TaskState.ERROR,
        (TaskState.SCALING, FSMEvent.COMPLETE): TaskState.ACTIVE,
        (TaskState.SCALING, FSMEvent.FAIL): TaskState.ERROR,
        (TaskState.UPDATING, FSMEvent.COMPLETE): TaskState.ACTIVE,
        (TaskState.UPDATING, FSMEvent.FAIL): TaskState.ERROR,
        (TaskState.TERMINATING, FSMEvent.COMPLETE): TaskState.PENDING,
        (TaskState.TERMINATING, FSMEvent.FAIL): TaskState.ERROR,
        (TaskState.ERROR, FSMEvent.INSTANTIATE): TaskState.PROCESSING,
        (TaskState.ERROR, FSMEvent.UPDATE): TaskState.UPDATING,
        (TaskState.ERROR, FSMEvent.TERMINATE): TaskState.TERMINATING,
    }

    @classmethod
    def transition(cls, instance: VnfInstance, event: FSMEvent) -> TaskState:
        key = (instance.task_state, event)
        if key not in cls.TRANSITIONS:
            raise ValueError(f"Invalid transition from {instance.task_state} via {event}")
        new_state = cls.TRANSITIONS[key]
        instance.task_state = new_state
        logger.info(f"FSM transition: {instance.id} {key[0].value} -> {new_state.value}")
        return new_state

    @classmethod
    def get_driver_method(cls, event: FSMEvent) -> Optional[str]:
        mapping = {
            FSMEvent.INSTANTIATE: "instantiate",
            FSMEvent.SCALE_IN: "scale_in",
            FSMEvent.SCALE_OUT: "scale_out",
            FSMEvent.UPDATE: "update",
            FSMEvent.TERMINATE: "terminate",
            FSMEvent.DELETE: "delete",
        }
        return mapping.get(event)
