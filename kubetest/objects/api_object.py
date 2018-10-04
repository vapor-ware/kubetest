"""Kubetest base class for the Kubernetes API Object wrappers."""

import abc
import logging

from kubernetes.client.rest import ApiException

from kubetest import condition, utils
from kubetest.manifest import load_file

log = logging.getLogger('kubetest')


class ApiObject(abc.ABC):
    """ApiObject is the base class for many of the kubetest objects
    which wrap Kubernetes API objects.

    This base class provides common functionality and common object
    properties for all API wrappers. It also defines the following
    abstract methods which all subclasses must implement:

      - ``create``: create the resource on the cluster
      - ``delete``: remove the resource from the cluster
      - ``refresh``: refresh the underlying object model
      - ``is_ready``: check if the object is in the ready state

    Args:
         api_object: The underlying Kubernetes API object.

    Attributes:
        obj: The underlying Kubernetes API object.
    """

    # The Kubernetes API object type. Each subclass should
    # define its own obj_type.
    obj_type = None
    '''The default Kubernetes API object type for the class.
    Each subclass should define its own ``obj_type``.
    '''

    api_clients = None
    '''A mapping of all the supported api clients for the API
    object type. Various resources can have multiple versions,
    e.g. "apps/v1", "apps/v1beta1", etc. The preferred version
    for each resource type should be defined under the "preferred"
    key. The preferred API client will be used when the apiVersion
    is not specified for the resource.
    '''

    def __init__(self, api_object):
        # The underlying Kubernetes Api Object
        self.obj = api_object

        # The api client for the object. This will be determined
        # by the apiVersion of the object's manifest.
        self._api_client = None

    @property
    def version(self):
        """str: The API version of the Kubernetes object (`obj.apiVersion``)."""
        return self.obj.api_version

    @property
    def name(self):
        """str: The name of the Kubernetes object (``obj.metadata.name``)."""
        return self.obj.metadata.name

    @name.setter
    def name(self, name):
        """Set the name of the Kubernetes objects (``obj.metadata.name``)."""
        self.obj.metadata.name = name

    @property
    def namespace(self):
        """The namespace of the Kubernetes object (``obj.metadata.namespace``)."""
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
        by the ``apiVersion`` of the object configuration.

        Raises:
            ValueError: The API version is not supported.
        """
        if self._api_client is None:
            c = self.api_clients.get(self.version)
            # If we didn't find the client in the api_clients dict, use the
            # preferred version.
            if c is None:
                log.warning(
                    'unknown version ({}), falling back to preferred version'
                    .format(self.version)
                )
                c = self.api_clients.get('preferred')
                if c is None:
                    raise ValueError(
                        'unknown version specified and no preferred version '
                        'defined for resource ({})'.format(self.version)
                    )
            # If we did find it, initialize that client version.
            self._api_client = c()
        return self._api_client

    def wait_until_ready(self, timeout=None, interval=1, fail_on_api_error=False):
        """Wait until the resource is in the ready state.

        Args:
            timeout (int): The maximum time to wait, in seconds, for
                the resource to reach the ready state. If unspecified,
                this will wait indefinitely. If specified and the timeout
                is met or exceeded, a TimeoutError will be raised.
            interval (int|float): The time, in seconds, to wait before
                re-checking if the object is ready.
            fail_on_api_error (bool): Fail if an API error is raised. An
                API error can be raised for a number of reasons, such as
                'resource not found', which could be the case when a resource
                is just being started or restarted. When waiting for readiness
                we generally do not want to fail on these conditions.
                (default: False)

        Raises:
             TimeoutError: The specified timeout was exceeded.
        """
        ready_condition = condition.Condition(
            'api object ready',
            self.is_ready,
        )

        utils.wait_for_condition(
            condition=ready_condition,
            timeout=timeout,
            interval=interval,
            fail_on_api_error=fail_on_api_error,
        )

    def wait_until_deleted(self, timeout=None, interval=1):
        """Wait until the resource is deleted from the cluster.

        Args:
            timeout (int): The maximum time to wait, in seconds, for
                the resource to be deleted from the cluster. If
                unspecified, this will wait indefinitely. If specified
                and the timeout is met or exceeded, a TimeoutError will
                be raised.
            interval (int|float): The time, in seconds, to wait before
                re-checking if the object has been deleted.

        Raises:
            TimeoutError: The specified timeout was exceeded.
        """
        def deleted_fn():
            try:
                self.refresh()
            except ApiException as e:
                # If we can no longer find the deployment, it is deleted.
                # If we get any other exception, raise it.
                if e.status == 404 and e.reason == 'Not Found':
                    return True
                else:
                    log.error('error refreshing object state')
                    raise e
            else:
                # The object was still found, so it has not been deleted
                return False

        delete_condition = condition.Condition(
            'api object deleted',
            deleted_fn
        )

        utils.wait_for_condition(
            condition=delete_condition,
            timeout=timeout,
            interval=interval,
        )

    @classmethod
    def load(cls, path):
        """Load the Kubernetes resource from file.

        Generally, this is used to load the Kubernetes manifest files
        and parse them into their appropriate API Object type.

        Args:
            path (str): The path to the YAML config file (manifest)
                containing the configuration for the resource.

        Returns:
            ApiObject: The API object wrapper corresponding to the configuration
            loaded from manifest YAML file.
        """
        obj = load_file(path, cls.obj_type)
        return cls(obj)

    @abc.abstractmethod
    def create(self, namespace=None):
        """Create the underlying Kubernetes resource in the cluster
        under the given namespace.

        Args:
            namespace (str): The namespace to create the resource under.
                If no namespace is provided, it will use the instance's
                namespace member, which is set when the object is created
                via the kubetest client. (optional)
        """

    @abc.abstractmethod
    def delete(self, options):
        """Delete the underlying Kubernetes resource from the cluster.

        This method expects the resource to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for resource deletion.
        """

    @abc.abstractmethod
    def refresh(self):
        """Refresh the local state (``obj``) of the underlying Kubernetes resource."""

    @abc.abstractmethod
    def is_ready(self):
        """Check if the resource is in the ready state.

        It is up to the wrapper subclass to define what "ready" means for
        that particular resource.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
