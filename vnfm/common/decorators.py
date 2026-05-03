import functools
import inspect

from vnfm.common.exceptions import VnfInstanceConflictState


def _to_set(value):
    if value is None:
        return None
    if isinstance(value, set):
        return value
    if isinstance(value, (list, tuple)):
        return set(value)
    return {value}


def check_vnf_state(action, instantiation_state=None, task_state=None):
    """Decorator to check vnf states are valid for particular action.

    If the vnf is in the wrong state, it will raise VnfInstanceConflictState.

    Example::
        @check_vnf_state(
            action='instantiate',
            instantiation_state=InstantiationState.NOT_INSTANTIATED,
            task_state=TaskState.PENDING,
        )
        async def instantiate(self, vnf_instance, ...):
            ...
    """
    allowed_inst_state = _to_set(instantiation_state)
    allowed_task_state = _to_set(task_state)

    def outer(f):
        if inspect.iscoroutinefunction(f):
            @functools.wraps(f)
            async def async_inner(*args, **kw):
                vnf_instance = _extract_vnf_instance(args, kw)
                _validate_state(vnf_instance, action, allowed_inst_state, allowed_task_state)
                return await f(*args, **kw)
            return async_inner
        else:
            @functools.wraps(f)
            def inner(*args, **kw):
                vnf_instance = _extract_vnf_instance(args, kw)
                _validate_state(vnf_instance, action, allowed_inst_state, allowed_task_state)
                return f(*args, **kw)
            return inner
    return outer


def _extract_vnf_instance(args, kw):
    """Extract vnf_instance from positional args or keywords."""
    if 'vnf_instance' in kw:
        return kw['vnf_instance']
    if len(args) >= 2:
        return args[1]
    raise ValueError("vnf_instance not found in arguments")


def _validate_state(vnf_instance, action, allowed_inst_state, allowed_task_state):
    if allowed_inst_state is not None and vnf_instance.instantiation_state not in allowed_inst_state:
        raise VnfInstanceConflictState(
            attr='instantiation_state',
            uuid=vnf_instance.id,
            state=vnf_instance.instantiation_state,
            action=action,
        )
    if allowed_task_state is not None and vnf_instance.task_state not in allowed_task_state:
        raise VnfInstanceConflictState(
            attr='task_state',
            uuid=vnf_instance.id,
            state=vnf_instance.task_state,
            action=action,
        )
