from pathlib import Path
from civet.abstract_data import DataSource
from typing import Any, Sequence
from unittest.mock import call, MagicMock, ANY
from dataclasses import dataclass


FINAL_OUTPUT = 'test_final_output'


@dataclass(frozen=True)
class Intermediate:
    key: int | str


def assert_save_chain(ds: DataSource, expected: list[call]):
    """
    Assertion of a `DataSource` against a list of calls it is expected to make
    to the shell.
    """
    mock_run = MagicMock()
    ds.save(FINAL_OUTPUT, shell=mock_run, require_output=False)
    assert_call_args_list(mock_run.call_args_list, expected)


def assert_call_args_list(actual: list[call], expected: list[call]):
    """
    Compare two lists of `call` have the same args. `_Intermediate` are
    validated to be equal across subsequent calls.
    """
    intermediates: dict[int | str, Path] = {}
    for actual_call, expected_call in zip(actual, expected):
        expected_anys = _intermediates2any(expected_call)
        print(expected_anys)
        assert actual_call == expected_anys
        for actual_intermediate, expected_intermediate in zip(actual_call.args, expected_call.args):
            if not isinstance(expected_intermediate, Intermediate):
                continue
            if expected_intermediate.key in intermediates:
                assert actual_intermediate == intermediates[expected_intermediate.key]
            else:
                intermediates[expected_intermediate.key] = actual_intermediate
        if expected_call.kwargs:
            raise ValueError('kwargs not supported')


def _intermediates2any(c: call) -> call:
    args = [_intermediate2any(a) for a in c.args]
    kwargs = {k: _intermediate2any(v) for k, v in c.kwargs.items()}
    return call(*args, **kwargs)


def _intermediate2any(a: Any) -> Any:
    if isinstance(a, Intermediate):
        return ANY
    if isinstance(a, (list, tuple)):
        return a.__class__(_intermediate2any(e) for e in a)
    if isinstance(a, dict):
        raise TypeError('Unsupported')
    return a


__example_actual = [
    call(['cp', 'one', 'two']),
    call(['mv', 'two', 'three']),
    call(['wow', '-i', 'three', 'four'])
]

__example_expected = [
    call(['cp', Intermediate(1), Intermediate(2)]),
    call(['mv', Intermediate(2), Intermediate(3)]),
    call(['wow', '-i', Intermediate(3), ANY])
]

assert_call_args_list(__example_actual, __example_expected)
