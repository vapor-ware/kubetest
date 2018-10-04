"""Kubetest wrapper for the Kubernetes ``Secret`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class Secret(ApiObject):
    """Kubetest wrapper around a Kubernetes `Secret`_ API Object.

    The actual ``kubernetes.client.V1Secret`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `Secret`_.

    .. _Secret:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#secret-v1-core
    """

    obj_type = client.V1Secret

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the Secret under the given namespace.

        Args:
            namespace (str): The namespace to create the Secret under.
                If the Secret was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info('creating secret "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('secret: %s', self.obj)

        self.obj = self.api_client.create_namespaced_secret(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the Secret.

        This method expects the Secret to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for Secret deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting secret "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('secret: %s', self.obj)
        return self.api_client.delete_namespaced_secret(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Secret resource."""
        self.obj = self.api_client.read_namespaced_secret(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the Secret is in the ready state.

        Secrets do not have a "status" field to check, so we will
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
