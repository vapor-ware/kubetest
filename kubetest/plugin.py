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


def pytest_report_header(config):
    """Augment the pytest report header with kubetest info.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_report_header
    """
    disabled = config.getvalue('kube_disable')
    if not disabled:
        config_file = config.getvalue('kube_config')
        if config_file is None:
            config_file = 'default'

        return [
            'kubetest config file: {}'.format(config_file),
        ]


def pytest_configure(config):
    """Configure kubetest by loading in the kube config file.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure
    """
    # Setup the kubetest logger
    log_level = config.getvalue('kube_log_level')
    level = logging._nameToLevel.get(log_level.upper(), logging.WARNING)
    logger = logging.getLogger('kubetest')
    logger.setLevel(level)

    # Register kubetest markers
    config.addinivalue_line(
        'markers',
        'rolebinding(kind, name, subject_kind=None, subject_name=None): create and use '
        'a Kubernetes RoleBinding for the test case. The generated role binding will '
        'use the generated test-case namespace and will be automatically removed once '
        'the test completes. The role kind (Role, ClusterRole) must be specified along '
        'with the name of the role. Only existing Roles or ClusterRoles can be used. '
        'Optionally, the subject_kind (User, Group, ServiceAccount) and subject_name '
        'can be specified to set a target subject for the RoleBinding. If no subject '
        'is specified, it will default to all users in the namespace and all service '
        'accounts. If a subject is specified, both the subject kind and name must be '
        'present. The RoleBinding will always use the apiGroup '
        '"rbac.authorization.k8s.io" for both subjects and roleRefs. For more '
        'information, see '
        'https://kubernetes.io/docs/reference/access-authn-authz/rbac/'
    )
    config.addinivalue_line(
        'markers',
        'clusterrolebinding(name, subject_kind=None, subject_name=None): create and use '
        'a Kubernetes ClusterRoleBinding for the test case. The generated cluster role '
        'binding will be automatically created and removed for each marked test. The '
        'name of the role must be specified. Only existing ClusterRoles can be used. '
        'Optionally, the subject_kind (User, Group, ServiceAccount) and subject_name '
        'can be specified to set a target subject for the ClusterRoleBinding. If no '
        'subject is specified, it will default to all users in the namespace and all '
        'service accounts. If a subject is specified, both the subject kind and name '
        'must be present. The ClusterRoleBinding will always use the apiGroup '
        '"rbac.authorization.k8s.io" for both subjects and roleRefs. For more '
        'information, see '
        'https://kubernetes.io/docs/reference/access-authn-authz/rbac/'
    )

    # Configure kubetest with the kubernetes config, if not disabled.
    disabled = config.getvalue('kube_disable')
    if not disabled:
        # # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more, see:
        # # https://cloud.google.com/docs/authentication/production
        # gke_creds = config.getvalue('google_application_credentials')
        # if gke_creds is not None:
        #     # If application credentials already exist, store them so they can be
        #     # reset after testing.
        #     old_creds = os.environ.get(GOOGLE_APPLICATION_CREDENTIALS)
        #     if old_creds:
        #         os.environ['OLD_' + GOOGLE_APPLICATION_CREDENTIALS] = old_creds
        #     os.environ[GOOGLE_APPLICATION_CREDENTIALS] = gke_creds

        # Read in the kubeconfig file
        config_file = config.getvalue('kube_config')
        kubernetes.config.load_kube_config(config_file=config_file)


# def pytest_unconfigure(config):
#     """Unconfigure kubetest.
#
#     See Also:
#         https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_unconfigure
#     """
#     # Unset/reset the GOOGLE_APPLICATION_CREDENTIALS environment variable. For more,
#     # see: https://cloud.google.com/docs/authentication/production
#     gke_creds = config.getvalue('google_application_credentials')
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
    disabled = item.config.getvalue('kube_disable')
    if not disabled:

        # Register test case state based on markers on the test case
        test_case.register_rolebindings(
            *markers.rolebindings_from_marker(item, test_case.ns)
        )
        test_case.register_clusterrolebindings(
            *markers.clusterrolebindings_from_marker(item, test_case.ns)
        )


def pytest_runtest_teardown(item):
    """Run teardown actions to clean up the test client.

    See Also:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_teardown
    """
    disabled = item.config.getvalue('kube_disable')
    if not disabled:
        test_case = manager.get_test(item.nodeid)
        if test_case is not None:
            # teardown will delete the test client's namespace. deleting
            # a namespace will delete all the things in the namespace, so
            # that makes cleanup easier.
            test_case.teardown()


# ********** pytest fixtures **********

@pytest.fixture()
def kube(request):
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
    test_case.setup()

    return test_case.client
