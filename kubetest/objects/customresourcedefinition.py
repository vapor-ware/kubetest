"""Kubetest wrapper for the Kubernetes ``CustomResourceDefinition`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class CustomResourceDefinition(ApiObject):
    """Kubetest wrapper around a Kubernetes `CustomResourceDefinition`_ API Object.

    The actual ``kubernetes.client.V1beta1CustomResourceDefinition`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `V1beta1CustomResourceDefinition`_.

    .. V1beta1CustomResourceDefinition:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.17/#customresourcedefinition-v1beta1-apiextensions-k8s-io
    """

    obj_type = client.V1beta1CustomResourceDefinition

    api_clients = {
        'preferred': client.ApiextensionsV1beta1Api,
        'apiextensions.k8s.io/v1beta1': client.ApiextensionsV1beta1Api,
    }

    def create(self, namespace: str = None) -> None:
        """Create the customresourcedefinition under the given namespace.

        Args:
            namespace: This argument is ignored for customresourcedefinitions.
        """
        log.info(
            f'creating customresourcedefinition "{self.name}" in namespace "{self.namespace}"')
        log.debug(f'customresourcedefinition: {self.obj}')

        self.obj = self.api_client.create_custom_resource_definition(
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the customresourcedefinition.

        This method expects the customresourcedefinition to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for customresourcedefinition deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting customresourcedefinition "{self.name}"')
        log.debug(f'delete options: {options}')
        log.debug(f'customresourcedefinition: {self.obj}')

        return self.api_client.delete_custom_resource_definition(
            name=self.name,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes customresourcedefinition resource."""
        self.obj = self.api_client.read_custom_resource_definition(
            name=self.name
        )

    def is_ready(self) -> bool:
        """Check if the customresourcedefinition is in the ready state.

        customresourcedefinitions do not have a "status" field to check, so we
        will measure their readiness status by whether or not they exist
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
