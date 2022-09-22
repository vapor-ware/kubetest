"""Kubetest wrapper for the Kubernetes ``ClusterRole `` API Object."""

import logging

from kubernetes import client

from kubetest.objects import ApiObject

log = logging.getLogger("kubetest")


class ClusterRole(ApiObject):
    """Kubetest wrapper around a Kubernetes `ClusterRole`_ API Object.

    The actual ``kubernetes.client.V1ClusterRole`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `ClusterRole_.

    .. _ClusterRole:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.22/#clusterrole-v1-rbac-authorization-k8s-io
    """

    obj_type = client.V1ClusterRole

    api_clients = {
        "preferred": client.RbacAuthorizationV1Api,
        "rbac.authorization.k8s.io/v1": client.RbacAuthorizationV1Api,
    }

    def create(self, namespace: str = None) -> None:
        """Create the ClusterRole under the given namespace.

        Args:
            namespace: This argument is ignored for ClusterRole.
        """
        log.info(
            f'creating clusterrole "{self.name}" in namespace "{self.namespace}"'
        )
        log.debug(f"clusterrole: {self.obj}")

        self.obj = self.api_client.create_cluster_role(
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the ClusterRole.

        This method expects the ClusterRole to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for ClusterRole deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting clusterrole "{self.name}"')
        log.debug(f"delete options: {options}")
        log.debug(f"clusterrole: {self.obj}")

        return self.api_client.delete_cluster_role(
            name=self.name,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes ClusterRole resource."""
        self.obj = self.api_client.read_cluster_role(name=self.name)

    def is_ready(self) -> bool:
        """Check if the ClusterRole is in the ready state.

        ClusterRole do not have a "status" field to check, so we
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
