"""Kubetest manager for test client instances and namespace management."""

import logging

from kubetest import client, utils
from kubetest.objects import Namespace

log = logging.getLogger('kubetest')


class TestMeta:
    """TestMeta holds information associated with a single test node.

    Args:
        name (str): The name of the test.
        node_id (str): The id of the test node.
    """

    def __init__(self, name, node_id):
        self.name = name
        self.node_id = node_id
        self.ns = utils.new_namespace(name)

        # lazy load
        self._client = None
        self._namespace = None

        self.rolebindings = []
        self.clusterrolebindings = []

    @property
    def client(self):
        """Get the TestClient for the test case."""
        if self._client is None:
            self._client = client.TestClient(self.ns)
        return self._client

    @property
    def namespace(self):
        """Get the Namespace API Object associated with the test case."""
        if self._namespace is None:
            self._namespace = Namespace.new(self.ns)
        return self._namespace

    def setup(self):
        """Setup the cluster state for the test case.

        This performs all actions needed in order for the test client to be
        ready to use by a test case.
        """
        # create the test case namespace
        self.namespace.create()

        # if there are any role bindings, create them.
        for rb in self.rolebindings:
            self.client.create(rb)

        # if there are any cluster role bindings, create them.
        for crb in self.clusterrolebindings:
            self.client.create(crb)

    def teardown(self):
        """Clean up the cluster state for the given test case.

        This performs all actions needed in order to clean up the state that
        was previously set up for the test client in `setup`.
        """
        # delete the test case namespace. this will also delete anything
        # in the namespace, which includes RoleBindings.
        self.namespace.delete()

        # ClusterRoleBindings are not bound to a namespace, so we will need
        # to delete them ourselves.
        for crb in self.clusterrolebindings:
            self.client.delete(crb)

    def register_rolebinding(self, rolebinding):
        """Register a RoleBinding requirement with the test case.

        Args:
            rolebinding (RoleBinding): The RoleBinding that is needed for the
                test case.
        """
        self.rolebindings.append(rolebinding)

    def register_clusterrolebinding(self, clusterrolebinding):
        """Register a ClusterRoleBinding requirement with the test case.

        Args:
            clusterrolebinding (ClusterRoleBinding): The ClusterRoleBinding that
                is needed for the test case.
        """
        self.clusterrolebindings.append(clusterrolebinding)


class KubetestManager:
    """The manager for kubetest state.

    The KubetestManager is in charge of providing test clients for the tests
    that request them and mediating the namespace management corresponding to
    those test clients.
    """

    def __init__(self):

        # A dictionary mapping test node IDs to their corresponding TestMeta
        # object. Each test node will have a TestMeta created when the client
        # is created for the test node.
        self.nodes = {}

    def new_test(self, node_id, test_name):
        """Create a new TestMeta for a test case.

        This will be called by the test setup hook in order to create a new
        TestMeta for the manager to keep track of.

        Args:
            node_id (str): The id of the test node.
            test_name (str): The name of the test.

        Returns:
            TestMeta: The newly created TestMeta for the test case.
        """
        log.info('creating test meta for %s', node_id)
        meta = TestMeta(
            node_id=node_id,
            name=test_name,
        )
        self.nodes[node_id] = meta
        return meta

    def get_test(self, node_id):
        """Get the test metadata for the specified test node.

        Args:
            node_id (str): The id of the test node.

        Returns:
            TestMeta: The test metadata for the given node.
            None: No test metadata was found for the given node.
        """
        return self.nodes.get(node_id)
