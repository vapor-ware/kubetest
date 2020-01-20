"""Kubetest wrapper for the Kubernetes ``PersistentVolume`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class PersistentVolume(ApiObject):
    """Kubetest wrapper around a Kubernetes `PersistentVolume`_ API Object.

    The actual ``kubernetes.client.V1PersistentVolume`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `PersistentVolume`_.

    .. _PersistentVolume:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#persistentvolume-v1-core
    """

    obj_type = client.V1PersistentVolume

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the PersistentVolume under the given namespace.

        Args:
            namespace (str): This argument is ignored for PersistentVolumes.
        """
        log.info('creating persistentvolume "%s"', self.name)
        log.debug('persistentvolume: %s', self.obj)

        self.obj = self.api_client.create_persistent_volume(
            body=self.obj,
        )

    def delete(self, options):
        """Delete the PersistentVolume.

        Args:
             options (client.V1DeleteOptions): Options for PersistentVolume deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting persistentvolume "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('persistentvolume: %s', self.obj)

        return self.api_client.delete_persistent_volume(
            name=self.name,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes PersistentVolume resource."""
        self.obj = self.api_client.read_persistent_volume(
            name=self.name,
        )

    def is_ready(self):
        """Check if the PersistentVolume is in the ready state.

        PersistentVolumes have a "status" field to check. However, as this
        field may change from "available" to "bound" quickly if another
        object is using the PersistentVolume, we will measure their
        readiness status by whether or not they exist on the cluster.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True
