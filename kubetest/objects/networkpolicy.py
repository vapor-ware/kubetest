"""Kubetest wrapper for the Kubernetes ``NetworkPolicy`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class NetworkPolicy(ApiObject):
    """Kubetest wrapper around a Kubernetes `NetworkPolicy`_ API Object.

    The actual ``kubernetes.client.NetworkingV1Api`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `NetworkPolicy`_.

    .. _NetworkPolicy:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#networkpolicy-v1-networking-k8s-io
    """

    obj_type = client.V1NetworkPolicy

    api_clients = {
        'preffered': client.NetworkingV1Api,
        'networking.k8s.io/v1': client.NetworkingV1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace: str = None) -> None:
        """Create the NetworkPolicy under the given namespace.

        Args:
            namespace: The namespace to create the NetworkPolicy under.
                If the NetworkPolicy was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(
            'creating networkpolicy "%s" in namespace "%s"',
            self.name,
            self.namespace
        )
        log.debug('network_policy: %s', self.obj)

        self.obj = self.api_client.create_namespaced_network_policy(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the NetworkPolicy.

        This method expects the NetworkPolicy to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for NetworkPolicy deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting network_policy "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('network_policy: %s', self.obj)

        return self.api_client.delete_namespaced_network_policy(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes NetworkPolicy resource."""
        self.obj = self.api_client.read_namespaced_network_policy(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> None:
        """Check if the NetworkPolicy is in the ready state.

        Returns:
            True if in the ready state; False otherwise.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True
