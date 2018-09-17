"""A pytest plugin which helps with integration testing for Kubernetes deployments.

This plugin helps with the managing of the Kubernetes cluster and provides
useful test fixtures and functionality in order to interact with and test
the state of the cluster.
"""

import os

import kubernetes
import pytest

from kubetest.manager import KubetestManager

GOOGLE_APPLICATION_CREDENTIALS = 'GOOGLE_APPLICATION_CREDENTIALS'

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

    # Set the kubernetes config to use for the cluster. This defaults to
    # the same config used by kubectl at ~/.kube/config
    group.addoption(
        '--kube-config',
        action='store',
        metavar='path',
        default=None,
        help='the kubernetes config for kubetest'
    )

    # Disable kubetest from auto-configuring
    group.addoption(
        '--kube-disable',
        action='store_true',
        default=False,
        help='disable automatic configuration with the kubeconfig file'
    )

    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    # with the path to .json credentials
    group.addoption(
        '--google-application-credentials',
        action='store',
        metavar='path',
        default=None,
        help='google application credentials for GKE clusters'
    )


def pytest_configure(config):
    """Configure kubetest by loading in the kube config file.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure
    """
    disabled = config.getvalue('kube_disable')

    if not disabled:
        # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more, see:
        # https://cloud.google.com/docs/authentication/production
        gke_creds = config.getvalue('google_application_credentials')
        if gke_creds is not None:
            # If application credentials already exist, store them so they can be
            # reset after testing.
            old_creds = os.environ.get(GOOGLE_APPLICATION_CREDENTIALS)
            if old_creds:
                os.environ['OLD_' + GOOGLE_APPLICATION_CREDENTIALS] = old_creds
            os.environ[GOOGLE_APPLICATION_CREDENTIALS] = gke_creds

        # Read in the kubeconfig file
        config_file = config.getvalue('kube_config')
        kubernetes.config.load_kube_config(config_file=config_file)


def pytest_unconfigure(config):
    """Unconfigure kubetest.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_unconfigure
    """
    # Unset/reset the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more,
    # see: https://cloud.google.com/docs/authentication/production
    gke_creds = config.getvalue('google_application_credentials')
    if gke_creds is not None:
        # If there are old credentials stored, reset them. Otherwise, just unset
        # the environment variable.
        old = os.environ.get('OLD_' + GOOGLE_APPLICATION_CREDENTIALS)
        if old:
            os.environ[GOOGLE_APPLICATION_CREDENTIALS] = old
            del os.environ['OLD_' + GOOGLE_APPLICATION_CREDENTIALS]
        else:
            del os.environ[GOOGLE_APPLICATION_CREDENTIALS]


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
