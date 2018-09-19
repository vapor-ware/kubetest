"""Kubetest wrappers for Kubernetes API Objects."""

import abc
import logging
import time

import yaml
from kubernetes import client
from kubernetes.client.rest import ApiException

from kubetest.manifest import new_object
from kubetest.utils import selector_string

log = logging.getLogger('kubetest')

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
        log.info('waiting until ready for "%s"', self.name)
        # define the maximum time at which we should stop waiting, if set
        max_time = None
        if timeout is not None:
            max_time = time.time() + timeout

        start = time.time()
        # wait until the Api Object is either in the ready state or times out
        while True:
            if max_time and time.time() >= max_time:
                log.error('timed out while waiting to be ready')
                raise TimeoutError(
                    'timed out ({}s) while waiting for {} to be ready'
                    .format(timeout, self.obj.kind)
                )

            # if the object is ready, return
            if self.is_ready():
                break

            # if the object is not ready, sleep for a bit and check again
            time.sleep(1)

        end = time.time()
        log.info('wait complete (total=%f)', end - start)

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
        log.info('waiting until deleted for "%s"', self.name)
        # define the maximum time at which we should stop waiting, if set
        max_time = None
        if timeout is not None:
            max_time = time.time() + timeout

        start = time.time()
        # wait until the Api Object is either removed from the cluster or
        # times out
        while True:
            if max_time and time.time() >= max_time:
                log.error('timed out while waiting to be deleted')
                raise TimeoutError(
                    'timed out ({}s) while waiting for {} to be deleted'
                    .format(timeout, self.obj.kind)
                )

            try:
                self.refresh()
            except ApiException as e:
                # If we can no longer find the deployment, it is deleted.
                # If we get any other exception, raise it.
                if e.status == 404 and e.reason == 'Not Found':
                    break
                else:
                    log.error('error refreshing object state')
                    raise e

            time.sleep(1)

        end = time.time()
        log.info('wait complete (total=%f)', end - start)

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

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

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

        log.info('creating configmap "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('configmap: %s', self.obj)
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

        log.info('deleting configmap "%s" with options "%s"', self.name, options)
        log.debug('configmap: %s', self.obj)
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
        """Check if the ConfigMap is in the ready state.

        ConfigMaps do not have a 'status' field to check, so we will
        measure their readiness status by whether or not they exist
        on the cluster.
        """
        try:
            self.refresh()
        except:  # noqa
            return False
        else:
            return True


class Container:
    """Kubetest wrapper around a Kubernetes Container API Object.

    The actual `kubernetes.client.V1Container` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the Container.

    This wrapper does NOT subclass the kubetest.ApiObject like other
    object wrappers, because it is not intended to be created or
    managed from manifest file. It is merely meant to wrap the
    Container spec for a Pod to make Container-targeted actions
    easier.
    """

    def __init__(self, api_object, pod):
        self.obj = api_object
        self.pod = pod

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def get_logs(self):
        """Get up-to-date stream logs of a given container.

        Returns:
            str: String of logs.
        """
        return client.CoreV1Api().read_namespaced_pod_log(
            name=self.pod.name,
            namespace=self.pod.namespace,
            container=self.obj.name,
        )

    def search_logs(self, keyword):
        """Search for a keyword in the logs.

        Args:
            keyword (str): Keyword to search.

        Returns:
            Bool: True if found. False otherwise.
        """
        logs = self.get_logs()

        if logs.find(keyword) == -1:
            return False
        return True

    # TODO:
    #   - container proxy (#6)


class Deployment(ApiObject):
    """Kubetest wrapper around a Kubernetes Deployment API Object.

    The actual `kubernetes.client.V1Deployment` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the Deployment.
    """

    obj_type = client.V1Deployment

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

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

        log.info('creating deployment "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('deployment: %s', self.obj)
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

        log.info('deleting deployment "%s" with options "%s"', self.name, options)
        log.debug('deployment: %s', self.obj)
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
        log.info('checking status of deployment "%s"', self.name)
        # first, refresh the deployment state to ensure the latest status
        self.refresh()

        # return the status from the deployment
        return self.obj.status

    def get_pods(self):
        """Get the pods for the deployment.

        Returns:
            list[Pod]: A list of pods that belong to the deployment.
        """
        log.info('getting pods for deployment "%s"', self.name)
        pods = client.CoreV1Api().list_namespaced_pod(
            namespace=self.namespace,
            label_selector=selector_string(self.obj.metadata.labels),
        )
        pods = [Pod(p) for p in pods.items]
        log.debug('pods: %s', pods)
        return pods


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


class Service(ApiObject):
    """Kubetest wrapper around a Kubernetes Service API Object.

    The actual `kubernetes.client.V1Service` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the Service.
    """

    obj_type = client.V1Service

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the Service under the given namespace.

        Args:
            namespace (str): The namespace to create the Service under.
                If the Service was loaded via the Kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info('creating service "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('service: %s', self.obj)
        self.obj = client.CoreV1Api().create_namespaced_service(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the Service.

        This method expects the Service to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for Service deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting service "%s" with options "%s"', self.name, options)
        log.debug('service: %s', self.obj)
        return client.CoreV1Api().delete_namespaced_service(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Api Service object."""
        self.obj = client.CoreV1Api().read_namespaced_service(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the Service is in the ready state.

        The readiness state is not clearly available from the Service
        status, so to check whether or not the Service is ready, this
        will check whether the endpoints of the Service are ready.

        This comes with the caveat that in order for a Service to
        have endpoints, there needs to be some backend hooked up to it.
        If there is no backend, the Service will never have endpoints,
        so this will never resolve to True.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        self.refresh()

        # check the status. if there is no status, the service is
        # definitely not ready.
        if self.obj.status is None:
            return False

        endpoints = self.get_endpoints()

        # if the Service has no endpoints, its not ready.
        if len(endpoints) == 0:
            return False

        # get the service endpoints and check that they are all ready.
        for endpoint in endpoints:
            # if we have an endpoint, but there are no subsets, we
            # consider the endpoint to be not ready.
            if endpoint.subsets is None:
                return False

            for subset in endpoint.subsets:
                # if the endpoint has no addresses setup yet, its not ready
                if subset.addresses is None or len(subset.addresses) == 0:
                    return False

                # if there are still addresses that are not ready, the
                # service is not ready
                not_ready = subset.not_ready_addresses
                if not_ready is not None and len(not_ready) > 0:
                    return False

        # if we got here, then all endpoints are ready, so the service
        # must also be ready
        return True

    def status(self):
        """Get the status of the Service.

        Returns:
            client.V1ServiceStatus: The status of the Service.
        """
        log.info('checking status of service "%s"', self.name)
        # first, refresh the service state to ensure the latest status
        self.refresh()

        # return the status from the service
        return self.obj.status

    def get_endpoints(self):
        """Get the endpoints for the Service.

        This can be useful for checking internal IP addresses used
        in containers, e.g. for container auto-discovery.

        Returns:
            list[client.V1Endpoints]: A list of endpoints associated
                with the Service.
        """
        log.info('getting endpoints for service "%s"', self.name)
        endpoints = client.CoreV1Api().list_namespaced_endpoints(
            namespace=self.namespace,
        )

        svc_endpoints = []
        for endpoint in endpoints.items:
            # filter to include only the endpoints with the same
            # name as the service.
            if endpoint.metadata.name == self.name:
                svc_endpoints.append(endpoint)

        log.debug('endpoints: %s', svc_endpoints)
        return svc_endpoints
