"""Kubetest wrapper for the Kubernetes ``ClusterRoleBinding`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class ClusterRoleBinding(ApiObject):
    """Kubetest wrapper around a Kubernetes `ClusterRoleBinding`_ API Object.

    The actual ``kubernetes.client.V1ClusterRoleBinding`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `ClusterRoleBinding`_.

    .. _ClusterRoleBinding:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#clusterrolebinding-v1-rbac-authorization-k8s-io
    """

    obj_type = client.V1ClusterRoleBinding

    api_clients = {
        'preferred': client.RbacAuthorizationV1Api,
        'rbac.authorization.k8s.io/v1': client.RbacAuthorizationV1Api,
        'rbac.authorization.k8s.io/v1alpha1': client.RbacAuthorizationV1alpha1Api,
        'rbac.authorization.k8s.io/v1beta1': client.RbacAuthorizationV1beta1Api,
    }

    def create(self, namespace: str = None) -> None:
        """Create the ClusterRoleBinding under the given namespace.

        Args:
            namespace: This argument is ignored for ClusterRoleBindings.
        """
        log.info(
            f'creating clusterrolebinding "{self.name}" in namespace "{self.namespace}"')
        log.debug(f'clusterrolebinding: {self.obj}')

        self.obj = self.api_client.create_cluster_role_binding(
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the ClusterRoleBinding.

        This method expects the ClusterRoleBinding to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for ClusterRoleBinding deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting clusterrolebinding "{self.name}"')
        log.debug(f'delete options: {options}')
        log.debug(f'clusterrolebinding: {self.obj}')

        return self.api_client.delete_cluster_role_binding(
            name=self.name,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes ClusterRoleBinding resource."""
        self.obj = self.api_client.read_cluster_role_binding(
            name=self.name
        )

    def is_ready(self) -> bool:
        """Check if the ClusterRoleBinding is in the ready state.

        ClusterRoleBindings do not have a "status" field to check, so we
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
