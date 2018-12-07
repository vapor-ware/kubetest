"""A pytest plugin which helps with integration testing for Kubernetes deployments.

This plugin helps with the managing of the Kubernetes cluster and provides
useful test fixtures and functionality in order to interact with and test
the state of the cluster.
"""

# import os
import logging

import kubernetes
import pytest

from kubetest import markers
from kubetest.manager import KubetestManager

GOOGLE_APPLICATION_CREDENTIALS = 'GOOGLE_APPLICATION_CREDENTIALS'

log = logging.getLogger('kubetest')

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
        '--kube-config',
        action='store',
        metavar='path',
        default=None,
        help='the kubernetes config for kubetest'
    )
    group.addoption(
        '--kube-disable',
        action='store_true',
        default=False,
        help='disable automatic configuration with the kubeconfig file'
    )

    # FIXME (etd) - this was an attempt to fix occassional permissions errors
    # (https://github.com/vapor-ware/kubetest/issues/11) but in doing so, it looks
    # like I hosed my permissions, so I'm just commenting all of this out for now...
    # group.addoption(
    #     '--google-application-credentials',
    #     action='store',
    #     metavar='path',
    #     default=None,
    #     help='google application credentials for GKE clusters'
    # )

    group.addoption(
        '--kube-log-level',
        action='store',
        default='warning',
        help='log level for the kubetest logger'
    )

    group.addoption(
        '--kube-error-log-lines',
        action='store',
        default=50,
        help='set the number of lines to tail from container logs on error. '
             'to show all lines, set this to -1.'
    )


def pytest_report_header(config):
    """Augment the pytest report header with kubetest info.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_report_header
    """
    disabled = config.getoption('kube_disable')
    if not disabled:
        config_file = config.getoption('kube_config')
        if config_file is None:
            config_file = 'default'

        return [
            'kubetest config file: {}'.format(config_file),
        ]


def pytest_configure(config):
    """Configure pytest with kubetest additions.

    This registers the kubetest markers with pytest.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure
    """
    # Register kubetest markers
    markers.register(config)


def pytest_sessionstart(session):
    """Configure kubetest for the test session.

    Kubetest setup happens at session start (pytest_sessionstart) rather
    than on configuration (pytest_configure) so that we only have the
    expectation of a cluster config and available cluster when there are
    actually tests available. For example, if we are simply calling any of

        pytest --help
        pytest --markers
        pytest --fixtures

    we do not want to configure kubetest and force the expectation of
    cluster availability.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_sessionstart
    """
    # Setup the kubetest logger
    log_level = session.config.getoption('kube_log_level')
    level = logging._nameToLevel.get(log_level.upper(), logging.WARNING)
    logger = logging.getLogger('kubetest')
    logger.setLevel(level)

    # Configure kubetest with the kubernetes config, if not disabled.
    disabled = session.config.getoption('kube_disable')
    if not disabled:
        # # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more, see:
        # # https://cloud.google.com/docs/authentication/production
        # gke_creds = config.getoption('google_application_credentials')
        # if gke_creds is not None:
        #     # If application credentials already exist, store them so they can be
        #     # reset after testing.
        #     old_creds = os.environ.get(GOOGLE_APPLICATION_CREDENTIALS)
        #     if old_creds:
        #         os.environ['OLD_' + GOOGLE_APPLICATION_CREDENTIALS] = old_creds
        #     os.environ[GOOGLE_APPLICATION_CREDENTIALS] = gke_creds
        pass


# def pytest_sessionfinish(session):
#     """Unconfigure the test session for kubetest.
#
#     See Also:
#         https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_sessionfinish
#     """
#     # Unset/reset the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more,
#     # see: https://cloud.google.com/docs/authentication/production
#     gke_creds = config.getoption('google_application_credentials')
#     if gke_creds is not None:
#         # If there are old credentials stored, reset them. Otherwise, just unset
#         # the environment variable.
#         old = os.environ.get('OLD_' + GOOGLE_APPLICATION_CREDENTIALS)
#         if old:
#             os.environ[GOOGLE_APPLICATION_CREDENTIALS] = old
#             del os.environ['OLD_' + GOOGLE_APPLICATION_CREDENTIALS]
#         else:
#             del os.environ[GOOGLE_APPLICATION_CREDENTIALS]


def pytest_runtest_setup(item):
    """Run setup actions to prepare the test case.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_setup
    """
    # Register a new test case with the manager and setup the test case state.
    test_case = manager.new_test(
        node_id=item.nodeid,
        test_name=item.name,
    )

    # FIXME (etd) - not sure this is really what we want to do. does it make sense
    # to entirely disable the plugin just be specifying the disable flag? probably..
    # but there must be a better way than adding this check (perhaps unregistering the
    # plugin in the pytest_configure hook?)
    disabled = item.config.getoption('kube_disable')
    if not disabled:

        # Register test case state based on markers on the test case
        test_case.register_rolebindings(
            *markers.rolebindings_from_marker(item, test_case.ns)
        )
        test_case.register_clusterrolebindings(
            *markers.clusterrolebindings_from_marker(item, test_case.ns)
        )

        # Apply manifests for the test case, if any are specified.
        markers.apply_manifest_from_marker(item, test_case)


def pytest_runtest_teardown(item):
    """Run teardown actions to clean up the test client.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_teardown
    """
    disabled = item.config.getoption('kube_disable')
    if not disabled:
        manager.teardown(item.nodeid)


def pytest_runtest_makereport(item, call):
    """Create a test report for the test case. If the test case was found
    to fail, this will log out the container logs to provide more debugging
    context.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_makereport
    """
    disabled = item.config.getoption('kube_disable')
    if not disabled:
        if call.when == 'call':
            if call.excinfo is not None:
                tail_lines = item.config.getoption('kube_error_log_lines')
                if tail_lines != 0:
                    test_case = manager.get_test(item.nodeid)
                    logs = test_case.yield_container_logs(
                        tail_lines=tail_lines
                    )
                    for container_log in logs:
                        # Add a report section to the test output
                        item.add_report_section(
                            when=call.when,
                            key='kubernetes container logs',
                            content=container_log
                        )


def pytest_keyboard_interrupt():
    """Clean up the cluster from kubetest artifacts if the tests
    are manually terminated via keyboard interrupt.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_keyboard_interrupt
    """
    try:
        namespaces = kubernetes.client.CoreV1Api().list_namespace()
        for ns in namespaces.items:
            # if the namespace has a 'kubetest-' prefix, remove it.
            name = ns.metadata.name
            status = ns.status
            if (
                    name.startswith('kubetest-') and
                    status is not None and
                    status.phase.lower() == 'active'
            ):
                print('keyboard interrupt: cleaning up namespace "{}"'.format(name))
                kubernetes.client.CoreV1Api().delete_namespace(
                    body=kubernetes.client.V1DeleteOptions(),
                    name=name,
                )

        crbs = kubernetes.client.RbacAuthorizationV1Api().list_cluster_role_binding()
        for crb in crbs.items:
            # if the cluster role binding has a 'kubetest:' prefix, remove it.
            name = crb.metadata.name
            if name.startswith('kubetest:'):
                print(
                    'keyboard interrupt: cleaning up clusterrolebinding "{}"'.format(crb)
                )
                kubernetes.client.RbacAuthorizationV1Api().delete_cluster_role_binding(
                    body=kubernetes.client.V1DeleteOptions(),
                    name=name,
                )
    except Exception as e:
        log.error(
            'Failed to clean up kubetest artifacts from cluster on keyboard interrupt. '
            'You may need to manually remove items from your cluster. Check for '
            'namespaces with the "kubetest-" prefix and cluster role bindings with '
            'the "kubetest:" prefix. ({})'.format(e)
        )


# ********** pytest fixtures **********

@pytest.fixture
def kubeconfig(request):
    config_file = request.session.config.getoption('kube_config')
    return config_file


@pytest.fixture()
def kube(kubeconfig, request):
    """Return a client for managing a Kubernetes cluster for testing."""
    test_case = manager.get_test(request.node.nodeid)
    if test_case is None:
        logging.getLogger('kubetest').warning(
            'No kubetest test client found for test using the "kube" fixture. '
            '(are you running with the --kube-disable flag?)'
        )
        return None

    # Setup the test case. This will create the namespace and any other
    # objects (e.g. role bindings) that the test case will need.
    kubernetes.config.load_kube_config(config_file=kubeconfig)
    test_case.setup()

    return test_case.client
