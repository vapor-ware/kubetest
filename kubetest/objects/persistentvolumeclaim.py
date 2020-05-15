"""Kubetest wrapper for the Kubernetes ``PersistentVolumeClaim`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class PersistentVolumeClaim(ApiObject):
    """Kubetest wrapper around a Kubernetes `PersistentVolumeClaim`_ API Object.

    The actual ``kubernetes.client.V1PersistentVolumeClaim`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `PersistentVolumeClaim`_.

    .. _PersistentVolumeClaim:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#persistentvolumeclaim-v1-core
    """

    obj_type = client.V1PersistentVolumeClaim

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace: str = None) -> None:
        """Create the PersistentVolumeClaim under the given namespace.

        Args:
            namespace: The namespace to create the PersistentVolumeClaim under.
                If the PersistentVolumeClaim was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(
            'creating persistentvolumeclaim "%s" in namespace "%s"',
            self.name,
            self.namespace
        )
        log.debug('persistentvolumeclaim: %s', self.obj)

        self.obj = self.api_client.create_namespaced_persistent_volume_claim(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the PersistentVolumeClaim.

        This method expects the PersistentVolumeClaim to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for PersistentVolumeClaim deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting persistentvolumeclaim "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('persistentvolumeclaim: %s', self.obj)

        return self.api_client.delete_namespaced_persistent_volume_claim(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes PersistentVolumeClaim resource."""
        self.obj = self.api_client.read_namespaced_persistent_volume_claim(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> bool:
        """Check if the PersistentVolumeClaim is in the ready state.

        PersistentVolumeClaims have a "status" field to check. However, as this
        field may change from "available" to "bound" quickly if another
        object is using the PersistentVolumeClaim, we will measure their
        readiness status by whether or not they exist on the cluster.

        Returns:
            True if in the ready state; False otherwise.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True
