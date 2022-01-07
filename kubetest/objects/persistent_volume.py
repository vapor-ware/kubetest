"""Kubetest wrapper for the Kubernetes ``PersistentVolume`` API Object."""

import logging
from typing import Optional, Any

from kubernetes import client
from kubernetes.client import ApiException

from kubetest.objects import ApiObject

LOG = logging.getLogger("kubetest")


class PersistentVolume(ApiObject):
    """Kubetest wrapper around a Kubernetes `PersistentVolume`_ API Object.

    The actual ``kubernetes.client.V1PersistentVolume`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `V1PersistentVolume`_.

    .. _PersistentVolume:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#persistentvolume-v1-core
    """
    obj_type = client.V1PersistentVolume

    api_clients = {
        "preferred": client.CoreV1Api,
        "v1": client.CoreV1Api,
    }

    def create(self, namespace: str = None) -> None:
        pass

    def delete(self, options: client.V1DeleteOptions = None) -> Optional[Any]:
        if options is None:
            options = client.V1DeleteOptions()

        LOG.info(f'deleting pv "{self.name}"')
        LOG.debug(f"delete options: {options}")
        LOG.debug(f"pv: {self.obj}")
        try:
            self.refresh()

            return self.api_client.delete_persistent_volume(
                name=self.name,
                body=options,
            )
        except ApiException as e:
            # If we can no longer find the pv, it is already deleted.
            if e.status == 404 and e.reason == "Not Found":
                return None
            else:
                # If we get any other exception, raise it.
                LOG.error("error deleting persistent volume")
                raise e

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes PV resource."""
        self.obj = self.api_client.read_persistent_volume(
            self.name,
        )

    def is_ready(self) -> bool:
        pass

    def status(self) -> str:
        self.refresh()
        return self.obj.status.phase

    def storage_class(self) -> str:
        return self.obj.spec.storage_class_name
