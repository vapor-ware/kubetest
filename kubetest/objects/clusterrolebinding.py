"""Kubetest wrapper for the Kubernetes `ClusterRoleBinding` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


# FIXME (etd) - ClusterRoleBindings are not tied to a namespace, so they will
# not be automatically deleted when we delete the test namespace. We'll need a
# different avenue for deleting resources from the cluster. It mostly depends on
# the use cases for this resource (test-scope, session-scope, etc).
class ClusterRoleBinding(ApiObject):
    """Kubetest wrapper around a Kubernetes ClusterRoleBinding API Object.

    The actual `kubernetes.client.V1ClusterRoleBinding` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the ClusterRoleBinding.
    """

    obj_type = client.V1ClusterRoleBinding

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the ClusterRoleBinding under the given namespace.

        Args:
            namespace (str): This argument is ignored for ClusterRoleBindings.
        """
        log.info('creating clusterrolebinding "%s" in namespace "%s"', self.name, self.namespace)  # noqa
        log.debug('clusterrolebinding: %s', self.obj)
        self.obj = client.RbacAuthorizationV1Api().create_cluster_role_binding(
            body=self.obj,
        )

    def delete(self, options):
        """Delete the ClusterRoleBinding.

        This method expects the ClusterRoleBinding to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options (client.V1DeleteOptions): Options for ClusterRoleBinding deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting clusterrolebinding "%s" with options "%s"', self.name, options)
        log.debug('clusterrolebinding: %s', self.obj)

        return client.RbacAuthorizationV1Api().delete_cluster_role_binding(
            self.name,
            options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Api ClusterRoleBinding object."""
        self.obj = client.RbacAuthorizationV1Api().read_cluster_role_binding(
            name=self.name
        )

    def is_ready(self):
        """Check if the ClusterRoleBinding is in the ready state.

        ClusterRoleBindings do not have a 'status' field to check, so we
        will measure their readiness status by whether or not they exist
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
