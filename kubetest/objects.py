"""
"""

import abc
import time

import yaml
from kubernetes import client
from kubernetes.client.rest import ApiException

from kubetest.manifest import new_object
from kubetest.utils import label_string

# A global map that matches the Api Client class to its corresponding
# apiVersion so we can get the correct client for the manifest version.
# TODO (etd): investigate - there may be a better way of doing this?
#   https://github.com/kubernetes-client/python/blob/master/examples/example3.py
api_clients = {
    'apps/v1': client.AppsV1Api,
    'apps/v1beta1': client.AppsV1beta1Api,
    'apps/v1beta2': client.AppsV1beta2Api,
}


class ApiObject(abc.ABC):
    """ApiObject is the base class for all Kubernetes API objects."""

    # The Kubernetes API object type. Each subclass should
    # define its own obj_type.
    obj_type = None

    def __init__(self, api_object):
        # The underlying Kubernetes Api Object
        self.obj = api_object

        # The api client for the object. This will be determined
        # by the apiVersion of the object's manifest.
        self._api_client = None

    @property
    def version(self):
        """The API version of the Kubernetes object (e.g. apiVersion)."""
        return self.obj.api_version

    @property
    def name(self):
        """The name of the Kubernetes object (metadata.name)."""
        return self.obj.metadata.name

    @property
    def namespace(self):
        """The namespace of the Kubernetes object (metadata.namespace)."""
        return self.obj.metadata.namespace

    @namespace.setter
    def namespace(self, name):
        """Set the namespace of the object, if it hasn't already been set.

        Raises:
            AttributeError: The namespace has already been set.
        """
        if self.obj.metadata.namespace is None:
            self.obj.metadata.namespace = name
        else:
            raise AttributeError('Cannot set namespace - object already has a namespace')

    @property
    def api_client(self):
        """The API client for the Kubernetes object. This is determined
        by the apiVersion of the object configuration.

        Raises:
            ValueError: The API version is not supported.
        """
        if self._api_client is None:
            c = api_clients.get(self.version)
            # If we didn't find the client in the api_clients dict, raise
            # an error - missing clients will need to be added manually.
            if c is None:
                raise ValueError(
                    'Unsupported Api Client version: {}'.format(self.version)
                )
            # If we did find it, initialize that client version.
            self._api_client = c()
        return self._api_client

    def wait_until_ready(self, timeout=None):
        """Wait until the Api Object is in the ready state.

        Args:
            timeout (int): The maximum time to wait, in seconds, for
                the Api Object to reach the ready state. If unspecified,
                this will wait indefinitely. If specified and the timeout
                is met or exceeded, a TimeoutError will be raised.

        Raises:
             TimeoutError: The specified timeout was exceeded.
        """
        # define the maximum time at which we should stop waiting, if set
        max_time = None
        if timeout is not None:
            max_time = time.time() + timeout

        # wait until the Api Object is either in the ready state or times out
        while True:
            if max_time and time.time() >= max_time:
                raise TimeoutError(
                    'timed out ({}s) while waiting for {} to be ready'
                    .format(timeout, self.obj.type)
                )

            # if the object is ready, return
            if self.is_ready():
                return

            # if the object is not ready, sleep for a bit and check again
            time.sleep(1)

    def wait_until_deleted(self, timeout=None):
        """Wait until the Api Object is deleted from the cluster.

        Args:
            timeout (int): The maximum time to wait, in seconds, for
                the Api Object to be deleted from the cluster. If
                unspecified, this will wait indefinitely. If specified
                and the timeout is met or exceeded, a TimeoutError will
                be raised.

        Raises:
            TimeoutError: The specified timeout was exceeded.
        """
        # define the maximum time at which we should stop waiting, if set
        max_time = None
        if timeout is not None:
            max_time = time.time() + timeout

        # wait until the Api Object is either removed from the cluster or
        # times out
        while True:
            if max_time and time.time() >= max_time:
                raise TimeoutError(
                    'timed out ({}s) while waiting for {} to be deleted'
                    .format(timeout, self.obj.type)
                )

            try:
                self.refresh()
            except ApiException as e:
                # If we can no longer find the deployment, it is deleted.
                # If we get any other exception, raise it.
                if e.status == 404 and e.reason == 'Not Found':
                    return
                else:
                    raise e

            time.sleep(1)

    @classmethod
    def load(cls, path):
        """Load the Kubernetes API Object from file.

        Generally, this is used to load the Kubernetes manifest files
        and parse them into their appropriate API Object type.

        Args:
            path (str): The path to the YAML config file (manifest)
                containing the configuration for the API Object.

        Returns:
            ApiObject: The API object corresponding to the configuration
                loaded from YAML file.
        """
        with open(path, 'r') as f:
            manifest = yaml.load(f)

        obj = new_object(cls.obj_type, manifest)
        return cls(obj)

    @abc.abstractmethod
    def create(self, namespace=None):
        """Create the underlying Kubernetes Api Object in the cluster
        under the given namespace.

        Args:
            namespace (str): The namespace to create the Api Object under.
                If no namespace is provided, it will use the instance's
                namespace member, which is set when the object is created
                via the Kubetest client. (optional)
        """

    @abc.abstractmethod
    def delete(self, options):
        """Delete the underlying Kubernetes Api Object from the cluster.

        This method expects the Api Object to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for deployment deletion.
        """

    @abc.abstractmethod
    def refresh(self):
        """Refresh the local state of the underlying Kubernetes Api Object."""

    @abc.abstractmethod
    def is_ready(self):
        """Check if the Api Object is in the ready state.

        Returns:
            bool: True if in the ready state; False otherwise.
        """


class Configmap(ApiObject):
    """Kubetest wrapper around a Kubernetes ConfigMap API Object.

    The actual `kubernetes.client.V1ConfigMap` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the ConfigMap.
    """

    obj_type = client.V1ConfigMap

    def __init__(self, api_object):
        super().__init__(api_object)

    def create(self, namespace=None):
        """Create the ConfigMap under the given namespace.

        Args:
            namespace (str): The namespace to create the ConfigMap under.
                If the ConfigMap was loaded via the Kubetest Client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        self.obj = client.CoreV1Api().create_namespaced_config_map(
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

        return client.CoreV1Api().delete_namespaced_config_map(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Api ConfigMap object."""
        self.obj = client.CoreV1Api().read_namespaced_config_map(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the ConfigMap is in the ready state."""
        self.refresh()

        # if there is no status, the configmap is definitely not ready
        status = self.obj.status
        if status is None:
            return False

        # TODO: figure out what configmap status looks like


class Deployment(ApiObject):
    """Kubetest wrapper around a Kubernetes Deployment API Object.

    The actual `kubernetes.client.V1Deployment` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the Deployment.
    """

    obj_type = client.V1Deployment

    def __init__(self, api_object):
        super().__init__(api_object)

    def create(self, namespace=None):
        """Create the Deployment under the given namespace.

        Args:
            namespace (str): The namespace to create the Deployment under.
                If the Deployment was loaded via the Kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        self.obj = self.api_client.create_namespaced_deployment(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the Deployment.

        This method expects the Deployment to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for Deployment deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        return self.api_client.delete_namespaced_deployment(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Api Deployment object."""
        self.obj = self.api_client.read_namespaced_deployment_status(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the Deployment is in the ready state.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        self.refresh()

        # if there is no status, the deployment is definitely not ready
        status = self.obj.status
        if status is None:
            return False

        # check the status for the number of total replicas and compare
        # it to the number of ready replicas. if the numbers are
        # equal, the deployment is ready; otherwise it is not ready.
        # TODO (etd) - we may want some logging in here eventually
        total = status.replicas
        ready = status.ready_replicas

        if total is None:
            return False

        return total == ready

    def status(self):
        """Get the status of the Deployment.

        Returns:
            client.V1DeploymentStatus: The status of the Deployment.
        """
        # first, refresh the deployment state to ensure the latest status
        self.refresh()

        # return the status from the deployment
        return self.obj.status

    def get_pods(self):
        """Get the pods for the deployment.

        Returns:
            list[Pod]: A list of pods that belong to the deployment.
        """
        pods = client.CoreV1Api().list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_string(self.obj.metadata.labels),
        )
        return [Pod(p) for p in pods.items]


class Pod(ApiObject):
    """Kubetest wrapper around a Kubernetes Pod API Object.

    """

    obj_type = client.V1Pod

    def __init__(self, api_object):
        super().__init__(api_object)

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

        for condition in status.conditions:
            # we only care about the condition type 'ready'
            if condition.type.lower() != 'ready':
                continue

            # check that the readiness condition is True
            return condition.status.lower() == 'true'

        # Catchall
        return False

    def status(self):
        """Get the status of the Pod.

        Returns:
            client.V1PodStatus: The status of the Pod.
        """
        # first, refresh the pod state to ensure latest status
        self.refresh()

        # return the status of the pod
        return self.obj.status

    def get_containers(self):
        """Get the containers for the pod.

        TODO (etd) - will probably eventually want a Container wrapper
        for the return here

        Returns:
            list[client.V1Container]: A list of containers that
                belong to the Pod.
        """
        self.refresh()

        return self.obj.spec.containers


class Service(ApiObject):
    """Kubetest wrapper around a Kubernetes Service API Object.

    """

    obj_type = client.V1Service

    def __init__(self, api_object):
        super().__init__(api_object)

    def create(self, namespace=None):
        """"""

    def delete(self, options):
        """"""

    def refresh(self):
        """"""

    def is_ready(self):
        """"""
