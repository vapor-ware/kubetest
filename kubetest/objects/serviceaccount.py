"""Kubetest wrapper for the Kubernetes ``ServiceAccount`` API Object."""

import logging

from kubernetes import client

from kubetest.objects import ApiObject

log = logging.getLogger('kubetest')


class ServiceAccount(ApiObject):
    """Kubetest wrapper around a Kubernetes `ServiceAccount`_ API Object.
    The actual ``kubernetes.client.V1ServiceAccount`` instance that this
    wraps can be accessed via the ``obj`` instance member.
    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `ServiceAccount`_.
    .. _ServiceAccount:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#serviceaccount-v1-core
    """

    obj_type = client.V1ServiceAccount

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def create(self, name: str = None) -> None:
        """Create the ServiceAccount under the given name.
        Args:
            name: The name to create the ServiceAccount under. If the
                name is not provided, it will be assumed to already be
                in the underlying object spec. If it is not, namespace
                operations will fail.
        """
        if name is not None:
            self.name = name

        log.info(f'creating serviceaccount "{self.name}"')
        log.debug(f'serviceaccount: {self.obj}')

        self.obj = self.api_client.create_namespaced_service_account(
            body=self.obj,
            namespace=self.namespace,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the Namespace.
        Args:
             options: Options for ServiceAccount deletion.
        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting ServiceAccount "{self.name}"')
        log.debug(f'delete options: {options}')
        log.debug(f'service account: {self.obj}')

        return self.api_client.delete_namespaced_service_account(
            name=self.name,
            namespace=self.namespace,
            body=options
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes ServiceAccount resource."""
        self.obj = self.api_client.read_namespaced_service_account(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> bool:
        """Check if the ServiceAccount is in the ready state.

        ServiceAccount do not have a "status" field to check, so we will
        measure their readiness status by whether or not they exist
        on the cluster.

        Returns:
            True if in the ready state; False otherwise.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True
