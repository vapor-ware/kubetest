"""Unit tests for the kubetest.condition package."""

import pytest

from kubetest.condition import Condition, check_all, check_and_sort


def test_condition_init_ok():
    """Test initializing a Condition with no errors."""

    c = Condition('test', lambda x: x == 'foo', 'foo')
    assert c.fn is not None
    assert c.args == ('foo',)
    assert c.kwargs == {}


def test_condition_init_err():
    """Test initializing a Condition where the provided fn is not callable."""

    with pytest.raises(ValueError):
        Condition('test', 'not-callable')


@pytest.mark.parametrize(
    'fn,args,kwargs', [
        (lambda: True, (), {}),
        (lambda x: x, (True,), {}),
        (lambda x: x, (1,), {}),
        (lambda x: x, ('xyz',), {}),
        (lambda x: x, ({'xyz': 1}), {}),
        (lambda x: x, (), {'x': True}),
        (lambda x: x, (), {'x': 1}),
        (lambda x: x, (), {'x': 'xyz'}),
        (lambda x: x, (), {'x': ['xyz']}),
        (lambda x: x, (), {'x': {'xyz': 1}}),
    ]
)
def test_condition_check_true(fn, args, kwargs):
    """Test checking when the function returns Truthy values."""

    c = Condition('test', fn, *args, **kwargs)
    assert c.check()


@pytest.mark.parametrize(
    'fn,args,kwargs', [
        (lambda: False, (), {}),
        (lambda x: x, (False,), {}),
        (lambda x: x, (0,), {}),
        (lambda x: x, ('',), {}),
        (lambda x: x, ([],), {}),
        (lambda x: x, ({},), {}),
        (lambda x: x, (), {'x': False}),
        (lambda x: x, (), {'x': 0}),
        (lambda x: x, (), {'x': ''}),
        (lambda x: x, (), {'x': []}),
        (lambda x: x, (), {'x': {}}),
    ]
)
def test_condition_check_false(fn, args, kwargs):
    """Test checking when the function returns Falsey values."""

    c = Condition('test', fn, *args, **kwargs)
    assert not c.check()


@pytest.mark.parametrize(
    'conditions,expected', [
        ([], True),
        ([Condition('test', lambda: True)], True),
        ([Condition('test', lambda: False)], False),
        ([Condition('test', lambda: True), Condition('test', lambda: True)], True),
        ([Condition('test', lambda: True), Condition('test', lambda: False)], False),
        ([Condition('test', lambda: False), Condition('test', lambda: False)], False),
    ]
)
def test_check_all(conditions, expected):
    """Test checking all conditions."""

    actual = check_all(*conditions)
    assert expected == actual


@pytest.mark.parametrize(
    'conditions,total_met,total_unmet', [
        ([], 0, 0),
        ([Condition('test', lambda: True)], 1, 0),
        ([Condition('test', lambda: False)], 0, 1),
        ([Condition('test', lambda: True), Condition('test', lambda: True)], 2, 0),
        ([Condition('test', lambda: False), Condition('test', lambda: True)], 1, 1),
        ([Condition('test', lambda: True), Condition('test', lambda: False)], 1, 1),
        ([Condition('test', lambda: False), Condition('test', lambda: False)], 0, 2),
    ]
)
def test_check_and_sort(conditions, total_met, total_unmet):
    """Test checking and sorting conditions."""

    init_len = len(conditions)
    met, unmet = check_and_sort(*conditions)

    assert len(met) == total_met
    assert len(unmet) == total_unmet
    assert len(conditions) == init_len
