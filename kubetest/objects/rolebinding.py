"""Kubetest wrapper for the Kubernetes ``RoleBinding`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class RoleBinding(ApiObject):
    """Kubetest wrapper around a Kubernetes `RoleBinding`_ API Object.

    The actual ``kubernetes.client.V1RoleBinding`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `RoleBinding`_.

    .. _RoleBinding:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#rolebinding-v1-rbac-authorization-k8s-io
    """

    obj_type = client.V1RoleBinding

    api_clients = {
        'preferred': client.RbacAuthorizationV1Api,
        'rbac.authorization.k8s.io/v1': client.RbacAuthorizationV1Api,
        'rbac.authorization.k8s.io/v1alpha1': client.RbacAuthorizationV1alpha1Api,
        'rbac.authorization.k8s.io/v1beta1': client.RbacAuthorizationV1beta1Api,
    }

    def create(self, namespace: str = None) -> None:
        """Create the RoleBinding under the given namespace.

        Args:
            namespace: The namespace to create the RoleBinding under.
                If the RoleBinding was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(f'creating rolebinding "{self.name}" in namespace "{self.namespace}"')  # noqa
        log.debug(f'rolebinding: {self.obj}')

        self.obj = self.api_client.create_namespaced_role_binding(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the RoleBinding.

        This method expects the RoleBinding to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for RoleBinding deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting rolebinding "{self.name}"')
        log.debug(f'delete options: {options}')
        log.debug(f'rolebinding: {self.obj}')

        return self.api_client.delete_namespaced_role_binding(
            namespace=self.namespace,
            name=self.name,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes RoleBinding resource."""
        self.obj = self.api_client.read_namespaced_role_binding(
            namespace=self.namespace,
            name=self.name,
        )

    def is_ready(self) -> bool:
        """Check if the RoleBinding is in the ready state.

        RoleBindings do not have a "status" field to check, so we
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
