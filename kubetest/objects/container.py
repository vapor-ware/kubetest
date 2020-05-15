"""Kubetest wrapper for the Kubernetes ``Container`` API Object."""

import logging

from kubernetes import client

log = logging.getLogger('kubetest')


class Container:
    """Kubetest wrapper around a Kubernetes `Container`_ API Object.

    The actual ``kubernetes.client.V1Container`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `Container`_.

    This wrapper does **NOT** subclass the ``objects.ApiObject`` like other
    object wrappers because it is not intended to be created or
    managed from manifest file. It is merely meant to wrap the
    Container spec for a Pod to make Container-targeted actions
    easier.

    .. _Container:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#container-v1-core
    """

    def __init__(self, api_object, pod) -> None:
        self.obj = api_object
        self.pod = pod

    def get_restart_count(self) -> int:
        """Get the number of times the Container has been restarted.

        Returns:
            The number of times the Container has been restarted.
        """
        container_name = self.obj.name
        pod_status = self.pod.status()

        # If there are no container status, the container hasn't started
        # yet, so there cannot be any restarts.
        if pod_status.container_statuses is None:
            return 0

        for status in pod_status.container_statuses:
            if status.name == container_name:
                return status.restart_count

        raise RuntimeError(
            f'Unable to determine container status for {container_name}'
        )

    def get_logs(self) -> str:
        """Get all the logs for the Container.

        Returns:
            The Container logs.
        """
        return client.CoreV1Api().read_namespaced_pod_log(
            name=self.pod.name,
            namespace=self.pod.namespace,
            container=self.obj.name,
        )

    def search_logs(self, *keyword: str) -> bool:
        """Search for keywords/phrases in the Container's logs.

        Args:
            *keyword: Keywords to search for within the logs.

        Returns:
            True if found; False otherwise.
        """
        logs = self.get_logs()

        for k in keyword:
            if logs.find(k) == -1:
                return False
        return True
