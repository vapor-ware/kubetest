"""A pytest plugin which helps with integration testing for Kubernetes deployments.

This plugin helps with the managing of the Kubernetes cluster and provides
useful test fixtures and functionality in order to interact with and test
the state of the cluster.
"""

import logging
import os
import warnings
from typing import Optional

import kubernetes
import pytest
import urllib3

from kubetest import errors, markers
from kubetest.client import TestClient
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
        help=(
            'the kubernetes config for kubetest; this is required for '
            'resources to be installed on the cluster'
        )
    )
    group.addoption(
        '--kube-context',
        action='store',
        metavar='context',
        default=None,
        help='the name of the kubernetes config context to use',
    )
    group.addoption(
        '--kube-disable',
        action='store_true',
        default=False,
        help='[DEPRECATED] disable automatic configuration with the kubeconfig file'
    )

    group.addoption(
        '--in-cluster',
        action='store_true',
        default=False,
        help='use the kubernetes in-cluster config',
    )

    # FIXME (etd) - this was an attempt to fix occasional permissions errors
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
        type=int,
        help='set the number of lines to tail from container logs on error. '
             'to show all lines, set this to -1.'
    )

    group.addoption(
        '--suppress-insecure-request',
        action='store',
        default=False,
        help='suppress the urllib3 InsecureRequestWarning. This is useful if testing '
             'against a cluster without HTTPS set up.'
    )


def pytest_report_header(config):
    """Augment the pytest report header with kubetest info.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_report_header
    """
    config_file = config.getoption('kube_config')
    if config_file is None:
        config_file = 'default'

    if config.getoption('in_cluster'):
        config_file = 'in-cluster'

    context = config.getoption('kube_context')
    if context is None:
        context = 'current context'

    return [
        f'kubetest config file: {config_file}',
        f'kubetest context: {context}',
    ]


def pytest_configure(config):
    """Configure pytest with kubetest additions.

    This registers the kubetest markers with pytest.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure
    """
    # Register kubetest markers
    markers.register(config)

    # Disable warnings, if configured to do so.
    if config.getoption('suppress_insecure_request'):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    # Check for configuration deprecations
    if session.config.getoption('kube_disable'):
        warnings.warn(
            '--kube-disable flag is deprecated (v0.2.0) and is no longer functional. '
            'To disable the plugin for a project, see: '
            'https://docs.pytest.org/en/latest/plugins.html',
        )

    # # Configure kubetest with the kubernetes config, if not disabled.
    # disabled = session.config.getoption('kube_disable')
    # if not disabled:
    #     # # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more, see:
    #     # # https://cloud.google.com/docs/authentication/production
    #     # gke_creds = config.getoption('google_application_credentials')
    #     # if gke_creds is not None:
    #     #     # If application credentials already exist, store them so they can be
    #     #     # reset after testing.
    #     #     old_creds = os.environ.get(GOOGLE_APPLICATION_CREDENTIALS)
    #     #     if old_creds:
    #     #         os.environ['OLD_' + GOOGLE_APPLICATION_CREDENTIALS] = old_creds
    #     #     os.environ[GOOGLE_APPLICATION_CREDENTIALS] = gke_creds
    #     pass


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
    # Previously (v0.3.[0-3]), this setup was gated to only run if the
    # --kube-config commandline flag was set. This was primarily done as an
    # optimization as to not create test metadata for tests that will not use
    # it. https://github.com/vapor-ware/kubetest/issues/130 points out that
    # the kubeconfig may be set without the --kube-config flag by overriding the
    # kubeconfig fixture. In such a case, this would have been skipped -- thus
    # there should NOT be any gating around test case metadata creation since
    # it is too early to tell whether we have all of the info we need.

    namespace_create = True
    namespace_name = None
    for mark in item.iter_markers(name='namespace'):
        namespace_create = mark.kwargs.get('create', True)
        namespace_name = mark.kwargs.get('name', None)

    # Register a new test case with the manager and setup the test case state.
    test_case = manager.new_test(
        node_id=item.nodeid,
        test_name=item.name,
        namespace_create=namespace_create,
        namespace_name=namespace_name,
    )

    # Note: These markers are not applied right now, meaning that the resource(s)
    #  which they reference are not added to the cluster yet. They are just
    #  registered with the test case so they can be applied to the cluster on
    #  test case setup.
    #
    #  At this point, the config is not loaded, so there is nothing that could be
    #  added to the cluster. It is safe to skip the teardown (which cleans up the
    #  test namespace) since nothing could be added to the namespace yet.
    try:
        # Register test case state based on markers on the test case.
        test_case.register_rolebindings(
            *markers.rolebindings_from_marker(item, test_case.ns)
        )
        test_case.register_clusterrolebindings(
            *markers.clusterrolebindings_from_marker(item, test_case.ns)
        )

        # Apply manifests for the test case, if any are specified.
        markers.apply_manifests_from_marker(item, test_case)
        markers.apply_manifest_from_marker(item, test_case)

    except Exception as e:
        test_case._pt_setup_failed = True
        raise e


def pytest_runtest_teardown(item):
    """Run teardown actions to clean up the test client.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_teardown
    """

    # See #154: Previously, this was only checking if the --kube-config command line
    # arg was passed to determine whether a test used kubetest for setup, and thus
    # whether it needed to be torn down. With the introduction of the kubeconfig
    # fixture, which allows users to override the kubeconfig in the test without having
    # to specify the --kube-config arg, this would prevent cleanup with the config was
    # specified via fixture.
    #
    # Unfortunately, due to the way the fixture is defined, we cannot simply check for
    # the presence/absence of the kubeconfig fixture in the test `item`, as it is always
    # present since there is a default kubeconfig fixture.
    #
    # As a bit of a hack, we can get the fixtures associated with the test item. When we
    # get the fixtures for `kubeconfig`, there will only be one fixture defined if no
    # custom fixture is specified - that is the default fixture. If there is a custom
    # override, there will be more than one fixture associated with the 'kubeconfig'
    # name. In such case, we should assume that a fixture was used to load the config
    # and allow test cleanup to proceed.
    _, _, fixtures = item.session._fixturemanager.getfixtureclosure(['kubeconfig'], item)

    if (
        item.config.getoption('kube_config') or
        len(fixtures.get('kubeconfig', [])) > 1 or
        item.config.getoption('in_cluster')
    ):
        manager.teardown(item.nodeid)


def pytest_runtest_makereport(item, call):
    """Create a test report for the test case. If the test case was found
    to fail, this will log out the container logs to provide more debugging
    context.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_makereport
    """

    # skip for tests without fixtures (eg: doctests)
    if not hasattr(item, 'fixturenames'):
        return

    if 'kube' in item.fixturenames and call.when == 'call':
        if call.excinfo is not None and call.excinfo.typename != 'Skipped':
            tail_lines = item.config.getoption('kube_error_log_lines')
            if tail_lines != 0:
                test_case = manager.get_test(item.nodeid)
                if test_case:
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
                print(f'keyboard interrupt: cleaning up namespace "{name}"')
                kubernetes.client.CoreV1Api().delete_namespace(
                    body=kubernetes.client.V1DeleteOptions(),
                    name=name,
                )

        crbs = kubernetes.client.RbacAuthorizationV1Api().list_cluster_role_binding()
        for crb in crbs.items:
            # if the cluster role binding has a 'kubetest:' prefix, remove it.
            name = crb.metadata.name
            if name.startswith('kubetest:'):
                print(f'keyboard interrupt: cleaning up clusterrolebinding "{crb}"')
                kubernetes.client.RbacAuthorizationV1Api().delete_cluster_role_binding(
                    body=kubernetes.client.V1DeleteOptions(),
                    name=name,
                )
    except Exception as e:
        log.error(
            'Failed to clean up kubetest artifacts from cluster on keyboard interrupt. '
            'You may need to manually remove items from your cluster. Check for '
            'namespaces with the "kubetest-" prefix and cluster role bindings with '
            f'the "kubetest:" prefix. ({e})'
        )


# ********** pytest fixtures **********

class ClusterInfo:
    """Information about the cluster the kubetest is being run on.

    This info is gathered from the current context and the loaded
    configuration.

    :ivar cluster: The name of the cluster set for the current context.
    :ivar user: The name of the user set for the current context.
    :ivar context: The name of the current context.
    :ivar host: API server address.
    :ivar verify_ssl: SSL certificate verification when calling the API.
    """

    def __init__(self, current, config):
        self.cluster = current['context']['cluster']
        self.user = current['context']['user']
        self.context = current['name']
        self.host = config.host
        self.verify_ssl = config.verify_ssl


@pytest.fixture
def clusterinfo(kubeconfig) -> ClusterInfo:
    """Get a ``ClusterInfo`` instance which provides basic information
    about the cluster the tests are being run on.
    """

    # Get an instance of a Configuration, which the kubeconfig
    # will be loaded into by default.
    config = kubernetes.client.Configuration()

    # Get the current context.
    _, current = kubernetes.config.list_kube_config_contexts(
        os.path.expandvars(os.path.expanduser(
            kubeconfig,
        ))
    )

    return ClusterInfo(
        current=current,
        config=config,
    )


@pytest.fixture
def kubeconfig(request) -> Optional[str]:
    """Return the name of the configured kube config file loaded for the tests."""

    config_file = request.session.config.getoption('kube_config')
    return config_file


@pytest.fixture
def kubecontext(request) -> Optional[str]:
    """Return the context in the kubeconfig to use for the tests.

    When None, use the current context as set in the kubeconfig.
    """

    context = request.session.config.getoption('kube_context')
    return context


@pytest.fixture()
def kube(kubeconfig, kubecontext, request) -> TestClient:
    """Return a client for managing a Kubernetes cluster for testing."""

    if request.session.config.getoption('in_cluster'):
        kubernetes.config.load_incluster_config()
    else:
        kubeconfig = kubeconfig or os.getenv("KUBECONFIG")
        if kubeconfig:
            kubernetes.config.load_kube_config(
                config_file=os.path.expandvars(os.path.expanduser(kubeconfig)),
                context=kubecontext,
            )
        else:
            log.error(
                'unable to interact with cluster: kube fixture used without kube config '
                'set. the config may be set with the flags --kube-config or --in-cluster or by'
                'an env var KUBECONFIG or custom kubeconfig fixture definition.'
            )
            raise errors.SetupError('no kube config defined for test run')

    test_case = manager.get_test(request.node.nodeid)
    if test_case is None:
        log.error(
            f'No kubetest client found for test using the "kube" fixture. ({request.node.nodeid})',  # noqa
        )
        raise errors.SetupError('error generating test client')

    # Setup the test case. This will create the namespace and any other
    # objects (e.g. role bindings) that the test case will need.
    test_case.setup()

    return test_case.client
