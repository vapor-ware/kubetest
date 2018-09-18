"""Kubetest manager for test client instances and namespace management."""

import logging

from kubetest import client, utils

log = logging.getLogger('kubetest')


class KubetestManager:
    """The manager for kubetest state.

    The KubetestManager is in charge of providing test clients for the tests
    that request them and mediating the namespace management corresponding to
    those test clients.
    """

    def __init__(self):
        # A dictionary that will map test node IDs to their corresponding
        # TestClient instances. This allows easy lookup per node to access
        # the test client, which is needed for the various pytest hooks.
        self.clients = {}

    def new_client(self, node_id, test_name):
        """Create a new TestClient.

        This should be called by the `k8s` fixture, which will return this
        client to the test requesting the client.

        Args:
            node_id (str): The id of the test node.
            test_name (str): The name of the test requesting a client.

        Returns:
            TestClient: A test client configured for the named test case.
        """
        ns = utils.new_namespace(test_name)

        log.info('creating test client for %s with namespace %s', node_id, ns)
        test_client = client.TestClient(ns)

        # Add the test client to the manager's client dictionary for tracking.
        self.clients[node_id] = test_client

        return test_client

    def get_client(self, node_id):
        """Get the test client for the specified test node.

        Returns:
            TestClient: The test client for the given node.
            None: No test client found for the given node.
        """
        return self.clients.get(node_id)
