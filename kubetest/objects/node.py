"""Kubetest wrapper for the Kubernetes `Node` API Object."""

import logging

from kubernetes import client

log = logging.getLogger('kubetest')


class Node:
    """Kubetest wrapper around a Kubernetes `Node`_ API Object.

    The actual ``kubernetes.client.V1Node`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `Node`_.

    This wrapper does **NOT** subclass the ``objects.ApiObject`` like
    other object wrappers because it is not intended to be created or
    managed from manifest file. It is merely meant to wrap the
    Node spec to make Node-based interactions easier

    .. _Node:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#node-v1-core
    """

    def __init__(self, api_object):
        self.obj = api_object
        self.name = api_object.metadata.name

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def refresh(self):
        """Refresh the underlying Kubernetes Node resource."""
        nodes = client.CoreV1Api().list_node()
        for node in nodes.items:
            if node.metadata.name == self.name:
                self.obj = node
                return
        log.warning('unable to refresh node: no node found with name: %s', self.name)

    def status(self):
        """Get the status of the Node.

        Returns:
            client.V1NodeStatus: The status of the Node.
        """
        log.info('checking status of node "%s"', self.name)
        self.refresh()
        return self.obj.status

    def is_ready(self):
        """Check whether the Node is in the ready state.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        status = self.status()

        # if there is no status, the node is definitely not ready
        if status is None:
            return False

        # if there are no conditions set, the node is not ready
        if status.conditions is None:
            return False

        for cond in status.conditions:
            # we only care about the 'ready' condition
            if cond.type.lower() != 'ready':
                continue

            # check that the readiness condition is true
            return cond.status.lower() == 'true'

        # Catchall
        return False
