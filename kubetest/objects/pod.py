"""Kubetest wrapper for the Kubernetes `Pod` API Object."""

import json
import logging

from kubernetes import client

from kubetest import condition, utils

from .api_object import ApiObject
from .container import Container

log = logging.getLogger('kubetest')


class Pod(ApiObject):
    """Kubetest wrapper around a Kubernetes Pod API Object.

    The actual `kubernetes.client.V1Pod` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the Pod.
    """

    obj_type = client.V1Pod

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the Pod under the given namespace.

        Args:
            namespace (str): The namespace to create the Pod under.
                If the Pod was loaded via the Kubetest client, the
                namespace will already be set, so it is not needed
                here. Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info('creating pod "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('pod: %s', self.obj)
        self.obj = client.CoreV1Api().create_namespaced_pod(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the Pod.

        This method expects the Pod to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will
        need to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for Pod deletion.

        Return:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting pod "%s" with options "%s"', self.name, options)
        log.debug('pod: %s', self.obj)
        return client.CoreV1Api().delete_namespaced_pod(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Api Pod object."""
        self.obj = client.CoreV1Api().read_namespaced_pod_status(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the Pod is in the ready state.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        self.refresh()

        # if there is no status, the pod is definitely not ready
        status = self.obj.status
        if status is None:
            return False

        # check the pod phase to make sure it is running. a pod in
        # the 'failed' or 'success' state will no longer be running,
        # so we only care if the pod is in the 'running' state.
        phase = status.phase
        if phase.lower() != 'running':
            return False

        for cond in status.conditions:
            # we only care about the condition type 'ready'
            if cond.type.lower() != 'ready':
                continue

            # check that the readiness condition is True
            return cond.status.lower() == 'true'

        # Catchall
        return False

    def status(self):
        """Get the status of the Pod.

        Returns:
            client.V1PodStatus: The status of the Pod.
        """
        log.info('checking status of pod "%s"', self.name)
        # first, refresh the pod state to ensure latest status
        self.refresh()

        # return the status of the pod
        return self.obj.status

    def get_containers(self):
        """Get the containers for the pod.

        Returns:
            list[Container]: A list of containers that belong to the Pod.
        """
        log.info('getting containers for pod "%s"', self.name)
        self.refresh()

        containers = [Container(c, self) for c in self.obj.spec.containers]
        log.debug('contianers: %s', containers)
        return containers

    def get_container(self, name):
        """Get a container in the Pod by name.

        Args:
            name (str): The name of the Container.

        Returns:
            Container: The Pod's Container with the matching name.
            None: No Container with the given name was found.
        """
        for c in self.get_containers():
            if c.obj.name == name:
                return c
        return None

    def get_restart_count(self):
        """Get the total number of Container restarts for the Pod.

        Returns:
            int: The total number of Container restarts.
        """
        container_statuses = self.status().container_statuses
        if container_statuses is None:
            return 0

        total = 0
        for container_status in container_statuses:
            total += container_status.restart_count

        return total

    def http_proxy_get(self, path):
        """Issue a GET request to a proxy for the Pod.

        Args:
            path (str): The URI to hit on the Pod.

        Returns:
            str: The response data.
        """
        return client.CoreV1Api().connect_get_namespaced_pod_proxy_with_path(
            name=self.name,
            namespace=self.namespace,
            path=path,
        )

    def http_proxy_get_json(self, path):
        """Issue a GET request to a proxy for the Pod and return
        the JSON response as a dictionary.

        Args:
            path (str): The URI to hit on the Pod.

        Returns:
            dict: The response data.
        """
        data = self.http_proxy_get(path)
        data = data.replace("'", '"')
        return json.loads(data)

    def containers_started(self):
        """Check if the Pod's Containers have all started.

        Returns:
            bool: True if all Containers have started; False otherwise.
        """
        # start the flag as true - we will check the state and set
        # this to False if any container is not yet running.
        containers_started = True

        status = self.status()
        if status.container_statuses is not None:
            for container_status in status.container_statuses:
                if container_status.state is not None:
                    if container_status.state.running is not None:
                        if container_status.state.running.started_at is not None:
                            # The container is started, so move on to check the
                            # next container
                            continue
                # If we get here, then the container has not started.
                containers_started = containers_started and False
                break

        return containers_started

    def wait_until_containers_start(self, timeout=None):
        """Wait until all containers in the Pod have started.

        This will wait for the images to be pulled and for the containers
        to be created and started. This will unblock once all pod containers
        have been started.

        This is different than waiting until ready, since a container may
        not be ready immediately after it has been started.

        Args:
            timeout (int): The maximum time to wait, in seconds, for the
                Pod's containers to be started. If unspecified, this will
                wait indefinitely. If specified and the timeout is met or
                exceeded, a TimeoutError will be raised.

        Raises:
            TimeoutError: The specified timeout was exceeded.
        """
        wait_condition = condition.Condition(
            'all pod containers started',
            self.containers_started,
        )

        utils.wait_for_condition(
            condition=wait_condition,
            timeout=timeout,
            interval=1,
        )
