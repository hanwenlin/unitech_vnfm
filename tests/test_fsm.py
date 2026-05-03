import pytest
from vnfm.conductor.fsm import VnfFsm, FSMEvent
from vnfm.common.constants import TaskState
from vnfm.db.models import VnfInstance


class TestVnfFsm:
    def test_instantiate_from_pending(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.PENDING
        new_state = VnfFsm.transition(instance, FSMEvent.INSTANTIATE)
        assert new_state == TaskState.PROCESSING
        assert instance.task_state == TaskState.PROCESSING

    def test_complete_instantiate(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.PROCESSING
        new_state = VnfFsm.transition(instance, FSMEvent.COMPLETE)
        assert new_state == TaskState.ACTIVE

    def test_scale_out_from_active(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.ACTIVE
        new_state = VnfFsm.transition(instance, FSMEvent.SCALE_OUT)
        assert new_state == TaskState.SCALING

    def test_scale_in_from_active(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.ACTIVE
        new_state = VnfFsm.transition(instance, FSMEvent.SCALE_IN)
        assert new_state == TaskState.SCALING

    def test_terminate_from_active(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.ACTIVE
        new_state = VnfFsm.transition(instance, FSMEvent.TERMINATE)
        assert new_state == TaskState.TERMINATING

    def test_complete_terminate(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.TERMINATING
        new_state = VnfFsm.transition(instance, FSMEvent.COMPLETE)
        assert new_state == TaskState.PENDING

    def test_fail_from_processing(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.PROCESSING
        new_state = VnfFsm.transition(instance, FSMEvent.FAIL)
        assert new_state == TaskState.ERROR

    def test_update_from_active(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.ACTIVE
        new_state = VnfFsm.transition(instance, FSMEvent.UPDATE)
        assert new_state == TaskState.UPDATING

    def test_delete_from_active(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.ACTIVE
        new_state = VnfFsm.transition(instance, FSMEvent.DELETE)
        assert new_state == TaskState.TERMINATING

    def test_invalid_transition_raises(self):
        instance = VnfInstance(name="test", vnfd_id="vnfd-1")
        instance.task_state = TaskState.PENDING
        with pytest.raises(ValueError):
            VnfFsm.transition(instance, FSMEvent.COMPLETE)

    def test_get_driver_method(self):
        assert VnfFsm.get_driver_method(FSMEvent.INSTANTIATE) == "instantiate"
        assert VnfFsm.get_driver_method(FSMEvent.SCALE_IN) == "scale_in"
        assert VnfFsm.get_driver_method(FSMEvent.SCALE_OUT) == "scale_out"
        assert VnfFsm.get_driver_method(FSMEvent.UPDATE) == "update"
        assert VnfFsm.get_driver_method(FSMEvent.TERMINATE) == "terminate"
        assert VnfFsm.get_driver_method(FSMEvent.DELETE) == "delete"
        assert VnfFsm.get_driver_method(FSMEvent.COMPLETE) is None
        assert VnfFsm.get_driver_method(FSMEvent.FAIL) is None
