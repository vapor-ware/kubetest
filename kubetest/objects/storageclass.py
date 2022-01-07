"""Kubetest wrapper for the Kubernetes ``storageClass`` API Object."""

from distutils.util import strtobool
import logging

from kubernetes import client
from kubetest.objects import ApiObject

LOG = logging.getLogger(__name__)


class StorageClass(ApiObject):
    """Kubetest wrapper around a Kubernetes `StorageClass`_ API Object.

    The actual ``kubernetes.client.V1StorageClass`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `V1StorageClass`_.

    .. _StorageClass:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#storageclass-v1-storage-k8s-io
    """

    obj_type = client.V1StorageClass

    api_clients = {
        'preferred': client.StorageV1Api,
        'v1': client.StorageV1Api,
        'storage.k8s.io/v1beta1': client.StorageV1beta1Api
    }

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes StorageClass resource."""
        storage_classes = client.StorageV1Api(api_client=self.api_client).list_storage_class()
        for storage_class in storage_classes.items:
            if storage_class.metadata.name == self.name:
                self.obj = storage_class
                return
        LOG.warning(f'unable to refresh storage class: no storage_class found with name: {self.name}')

    def create(self, namespace: str = None) -> None:
        pass

    def delete(self, options: client.V1DeleteOptions) -> client.V1Status:
        pass

    def is_ready(self) -> bool:
        pass

    def is_default(self) -> bool:
        # "metadata" "annotations" "storageclass.kubernetes.io/is-default-class": "true"
        flag = self.obj.metadata.annotations.get("storageclass.kubernetes.io/is-default-class", "0")
        return bool(strtobool(flag.lower()))
