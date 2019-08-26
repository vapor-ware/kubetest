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

    def create(self):
        """Create the PersistentVolume under the given namespace.

        Args:
            namespace (str): The namespace to create the PersistentVolume under.
                If the PersistentVolume was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        log.info('creating persistentvolume "%s"', self.name)
        log.debug('persistentvolume: %s', self.obj)

        self.obj = self.api_client.create_persistent_volume(
            body=self.obj,
        )

    def delete(self, options):
        """Delete the PersistentVolume.

        This method expects the PersistentVolume to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

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

        PersistentVolumes do not have a "status" field to check, so we will
        measure their readiness status by whether or not they exist
        on the cluster.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True
