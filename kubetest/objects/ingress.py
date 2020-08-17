"""Kubetest wrapper for the Kubernetes ``Ingress`` API Object."""

import logging

from kubernetes import client

from kubetest import condition, utils

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class Ingress(ApiObject):
    """Kubetest wrapper around a Kubernetes `Ingress`_ API Object.

    The actual ``kubernetes.client.ExtensionsV1beta1Api`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `Ingress`_.

    .. _Ingress:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#ingress-v1beta1-extensions
    """

    obj_type = client.ExtensionsV1beta1Api

    api_clients = {
        'preferred': client.ExtensionsV1beta1Api,
        'extensions/v1beta1': client.ExtensionsV1beta1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace: str = None) -> None:
        """Create the Ingress under the given namespace.

        Args:
            namespace: The namespace to create the Ingress under.
                If the Ingress was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(
            'creating ingress "%s" in namespace "%s"',
            self.name,
            self.namespace
        )
        log.debug('ingress: %s', self.obj)

        self.obj = self.api_client.create_namespaced_ingress(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the Ingress.

        This method expects the Ingress to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
             options: Options for Ingress deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting ingress "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('ingress: %s', self.obj)

        return self.api_client.delete_namespaced_ingress(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes Ingress resource."""
        self.obj = self.api_client.read_namespaced_ingress(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> bool:
        """Check if the Ingress is in the ready state.

        Returns:
            True if in the ready state; False otherwise.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True

    def has_load_balancer_ingress(self) -> bool:
        """Check if the ingress has been assigned an ingress.

        Returns:
            True if an ingress has been assigned; False otherwise.
        """
        self.refresh()
        return self.obj.status.load_balancer.ingress is not None

    def wait_for_load_balancer_ingress(self, timeout: int = None) -> None:
        """Wait until the ingress has been assigned an ingress.

        Args:
            timeout: The maximum time to wait in seconds, for the
            Ingress to be assigned an ingress. If unspecified,
            this will wait indefinitely. If specified and the timeout
            is met or exceeded, a TimeoutError will be raised.

        Raises:
            TimeoutError: The specified timeout was exceeded.
        """
        wait_condition = condition.Condition(
            'Ingress has been assigned an ingress',
            self.has_load_balancer_ingress)

        utils.wait_for_condition(
            condition=wait_condition,
            timeout=timeout,
            interval=1)
