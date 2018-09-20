"""Kubetest base class for the Kubernetes API Object wrappers."""

import abc
import logging
import time

import yaml
from kubernetes import client
from kubernetes.client.rest import ApiException

from kubetest.manifest import new_object

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
