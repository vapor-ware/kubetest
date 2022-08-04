"""Kubetest wrapper for the Kubernetes ``CustomObjects`` API Object."""

from typing import Dict

from kubernetes import client
from .api_object import ApiObject


class CustomObject(ApiObject):
    obj_type = Dict

    api_clients = {
        'preferred': client.CustomObjectsApi,
        'v1': client.CustomObjectsApi,
    }

    def __init__(self, api_object, crd=None, group=None, version=None, plural=None):
        super().__init__(api_object)
        self._group = crd.obj.spec.group if crd else group
        self._version = crd.obj.spec.versions[-1].name if crd else version
        self._plural = crd.obj.spec.names.plural if crd else plural

    @property
    def version(self) -> str:
        """The API version of the Kubernetes object (`obj.apiVersion``)."""
        return self.obj['apiVersion']

    @property
    def name(self) -> str:
        """The name of the Kubernetes object (``obj.metadata.name``)."""
        return self.obj['metadata']['name']

    @name.setter
    def name(self, name: str):
        """Set the name of the Kubernetes objects (``obj.metadata.name``)."""
        self.obj['metadata']['name'] = name

    @property
    def namespace(self) -> str:
        """The namespace of the Kubernetes object (``obj.metadata.namespace``)."""
        return self.obj['metadata'].get('namespace')

    @namespace.setter
    def namespace(self, name: str):
        """Set the namespace of the object, if it hasn't already been set.
        Raises:
            AttributeError: The namespace has already been set.
        """
        if self.obj['metadata'].get('namespace') is None:
            self.obj['metadata']['namespace'] = name
        else:
            raise AttributeError(
                "Cannot set namespace - object already has a namespace"
            )

    def create(self, namespace: str = None) -> None:
        pass

    def delete(self, options: client.V1DeleteOptions) -> client.V1Status:
        pass

    def refresh(self) -> None:
        if self.namespace:
            self.obj = self.api_client.get_namespaced_custom_object(
                self._group,
                self._version,
                self.namespace,
                self._plural,
                self.name
            )
        else:
            self.obj = self.api_client.get_cluster_custom_object(
                self._group,
                self._version,
                self._plural,
                self.name
            )

    def is_ready(self) -> bool:
        return self.obj is not None

    def patch(self, body, **kwargs):
        if self.namespace:
            self.obj = self.api_client.patch_namespaced_custom_object(
                self._group,
                self._version,
                self.namespace,
                self._plural,
                self.name,
                body,
                **kwargs
            )
        else:
            self.obj = self.api_client.patch_cluster_custom_object(
                self._group,
                self._version,
                self._plural,
                self.name,
                body,
                **kwargs
            )

    def annotate(self, annotations):
        self.patch(body={"metadata": {"annotations": annotations}})
