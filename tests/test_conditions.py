"""Unit tests for the kubetest.condition package."""

import pytest

from kubetest import condition


def test_condition_init_ok():
    """Test initializing a Condition with no errors."""

    c = condition.Condition(lambda x: x == 'foo', 'foo')
    assert c.fn is not None
    assert c.args == ('foo',)
    assert c.kwargs == {}


def test_condition_init_err():
    """Test initializing a Condition where the provided fn is not callable."""

    with pytest.raises(ValueError):
        condition.Condition('not-callable')


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

    c = condition.Condition(fn, *args, **kwargs)
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

    c = condition.Condition(fn, *args, **kwargs)
    assert not c.check()


@pytest.mark.parametrize(
    'conditions,expected', [
        ([], True),
        ([condition.Condition(lambda: True)], True),
        ([condition.Condition(lambda: False)], False),
        ([condition.Condition(lambda: True), condition.Condition(lambda: True)], True),
        ([condition.Condition(lambda: True), condition.Condition(lambda: False)], False),
        ([condition.Condition(lambda: False), condition.Condition(lambda: False)], False),
    ]
)
def test_check_all(conditions, expected):
    """Test checking all conditions."""

    actual = condition.check_all(*conditions)
    assert expected == actual
