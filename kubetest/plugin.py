"""A pytest plugin which helps with integration testing for Kubernetes deployments.

This plugin helps with the managing of the Kubernetes cluster and provides
useful test fixtures and functionality in order to interact with and test
the state of the cluster.
"""

import kubernetes
import pytest

from kubetest.manager import KubetestManager

# A global instance of the KubetestManager. This will be used by various
# pytest hooks and fixtures in order to create and manage the TestClient
# instances. The manager is in charge of creating new TestClients for each
# test that requests one via the `k8s` fixture, and to manage the lifecycle
# of the test namespace.
manager = KubetestManager()


# ********** pytest hooks **********

def pytest_addoption(parser):
    """Add options to pytest to configure kubetest.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_addoption
    """

    group = parser.getgroup('kubetest', 'kubernetes integration test support')
    group.addoption(
        '--kubeconfig',
        action='store',
        metavar='path',
        default=None,
        help='the kubernetes config for kubetest'
    )
    group.addoption(
        '--kubedisable',
        action='store_true',
        default=False,
        help='disable automatic configuration with the kubeconfig file'
    )


def pytest_configure(config):
    """Configure kubetest by loading in the kube config file.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure
    """
    disabled = config.getvalue('kubedisable')
    if not disabled:
        config_file = config.getvalue('kubeconfig')
        kubernetes.config.load_kube_config(config_file=config_file)


def pytest_runtest_teardown(item):
    """Run teardown actions to clean up the test client.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_teardown
    """
    client = manager.get_client(item.nodeid)
    if client is not None:
        # teardown will delete the test client's namespace. deleting
        # a namespace will delete all the things in the namespace, so
        # that makes cleanup easier.
        client.teardown()


# ********** pytest fixtures **********

@pytest.fixture()
def kube(request):
    """Create and setup a client for managing a Kubernetes cluster for testing."""
    test_client = manager.new_client(
        node_id=request.node.nodeid,
        test_name=request.node.name
    )

    test_client.setup()
    return test_client
