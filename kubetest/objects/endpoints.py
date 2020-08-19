"""Kubetest wrapper for the Kubernetes ``Endpoint`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class Endpoints(ApiObject):
    """Kubetest wrapper around a Kubernetes `Endpoints`_ API Object.

    The actual ``kubernetes.client.V1Endpoints`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `Endpoints`_.

    .. _Endpoints:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#endpoints-v1-core
    """

    obj_type = client.V1Endpoints

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def create(self, namespace: str = None) -> None:
        """Create the Endpoints under the given namespace.

        Args:
            namespace: The namespace to create the Endpoints under.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(f'creating endpoints "{self.name}" in namespace "{self.namespace}"')
        log.debug(f'endpoints: {self.obj}')

        self.obj = self.api_client.create_namespaced_endpoints(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the Endpoints.

        This method expects the Endpoints to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options: Options for Endpoint deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting endpoints "{self.name}"')
        log.debug(f'delete options: {options}')
        log.debug(f'endpoints: {self.obj}')

        return self.api_client.delete_namespaced_endpoints(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes Endpoints resource."""
        self.obj = self.api_client.read_namespaced_endpoints(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> bool:
        """Check if the Endpoints are in the ready state.

        The readiness of an Endpoint is determined by whether all of its
        subsets have no addresses in the "not ready" state.

        Returns:
            True if in the ready state; False otherwise.
        """
        self.refresh()

        # check if any of the endpoint subsets has and addresses
        # in the not ready state.
        if self.obj.subsets is None:
            return False

        for subset in self.obj.subsets:
            if subset.not_ready_addresses is not None and len(subset.not_ready_addresses) > 0:
                return False
        return True
