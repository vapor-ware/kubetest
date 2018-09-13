"""Unit tests for the kubetest.utils package."""

import pytest

from kubetest import utils


@pytest.mark.parametrize(
    'name,expected', [
        ('', 'kubetest--1536849367'),
        ('TestName', 'kubetest-testname-1536849367'),
        ('TESTNAME', 'kubetest-testname-1536849367'),
        ('Test-Name', 'kubetest-test-name-1536849367'),
        ('Test1_FOO-BAR_2', 'kubetest-test1-foo-bar-2-1536849367'),
        ('123456', 'kubetest-123456-1536849367'),
        ('___', 'kubetest-----1536849367'),
    ]
)
def test_new_namespace(name, expected):
    """Test creating a new namespace for the given function name."""

    # mock the return of time.time() so we know what it will return
    utils.time.time = lambda: 1536849367.0

    actual = utils.new_namespace(name)
    assert actual == expected
