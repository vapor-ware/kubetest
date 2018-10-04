"""Kubetest wrapper for the Kubernetes ``ConfigMap`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class ConfigMap(ApiObject):
    """Kubetest wrapper around a Kubernetes `ConfigMap`_ API Object.

    The actual ``kubernetes.client.V1ConfigMap`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `ConfigMap`_.

    .. _ConfigMap:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#configmap-v1-core
    """

    obj_type = client.V1ConfigMap

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the ConfigMap under the given namespace.

        Args:
            namespace (str): The namespace to create the ConfigMap under.
                If the ConfigMap was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info('creating configmap "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('configmap: %s', self.obj)

        self.obj = self.api_client.create_namespaced_config_map(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the ConfigMap.

        This method expects the ConfigMap to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options (client.V1DeleteOptions): Options for ConfigMap deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting configmap "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('configmap: %s', self.obj)

        return self.api_client.delete_namespaced_config_map(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes ConfigMap resource."""
        self.obj = self.api_client.read_namespaced_config_map(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the ConfigMap is in the ready state.

        ConfigMaps do not have a "status" field to check, so we will
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
