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


def pytest_configure(config):
    """Configure kubetest by loading in the kube config file.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure
    """
    config_file = config.getvalue('kubeconfig')
    kubernetes.config.load_kube_config(config_file=config_file)


def pytest_runtest_teardown(item):
    """Run teardown actions to clean up the test client.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_teardown
    """
    client = manager.get_client(item.nodeid)
    if client is not None:
        client.teardown()


# ********** pytest fixtures **********

@pytest.fixture()
def k8s(request):
    """Create and setup a client that can be used for managing a Kubernetes cluster for tests."""
    test_client = manager.new_client(
        node_id=request.node.nodeid,
        test_name=request.node.name
    )

    test_client.setup()
    return test_client
