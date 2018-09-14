"""
"""

import yaml
from kubernetes import client

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


class ApiObject:
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


class Configmap(ApiObject):
    """Kubetest wrapper around a Kubernetes ConfigMap API Object.

    """

    """
    * create
    * load
    * get
    * wait until ready?
    * delete
    * wait until deleted?
    """

    obj_type = client.V1ConfigMap

    def __init__(self, api_object):
        super().__init__(api_object)

    def create(self):
        """"""

    def delete(self):
        """"""

    def list(self):
        """"""

    def get(self):
        """"""


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
                namespace will already be set, so it is not needed. Otherwise,
                the namespace will need to be provided here.
        """
        if namespace is None:
            namespace = self.namespace

        self.obj = self.api_client.create_namespaced_deployment(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options=None):
        """Delete the Deployment.

        This method expects the Deployment to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for deployment deletion.

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
        """Refresh the underlying Kubernetes Api Deployment object.

        Raises:
            ValueError: No Deployment object was found with this Deployment's
                name and labels in the namespace.
        """
        # FIXME (etd) - it looks like once this is refreshed, we lose the
        # apiVersion and kind info? Investigate some more and add tests to verify.

        deployment_list = self.api_client.list_namespaced_deployment(
            namespace=self.namespace,
            field_selector='metadata.name={}'.format(self.name),
            label_selector=label_string(self.obj.metadata.labels),
        )

        if len(deployment_list.items) != 1:
            raise ValueError(
                'deployment "{}::{}" not found - unable to refresh'
                .format(self.namespace, self.name)
            )

        self.obj = deployment_list.items[0]

    def get_pods(self):
        """Get the pods for the deployment."""


class Node(ApiObject):
    """Kubetest wrapper around a Kubernetes Node API Object.

    """

    """
    * list
    * get state
    * wait for ready
    * delete?
    * wait for delete?
    """

    obj_type = client.V1Node

    def __init__(self, api_object):
        super().__init__(api_object)


class Pod(ApiObject):
    """Kubetest wrapper around a Kubernetes Pod API Object.

    """

    """
    * list
    * list from deployment
    * wait until ready
    * get logs
    * get state/status?
    * proxy get?
    """

    obj_type = client.V1Pod

    def __init__(self, api_object):
        super().__init__(api_object)

    def create(self):
        """"""

    def delete(self):
        """"""

    def list(self):
        """"""

    def get(self):
        """"""


class Service(ApiObject):
    """Kubetest wrapper around a Kubernetes Service API Object.

    """

    """
    * create
    * load
    * wait until ready
    * delete
    * wait until deleted
    """

    obj_type = client.V1Service

    def __init__(self, api_object):
        super().__init__(api_object)

    def create(self):
        """"""

    def delete(self):
        """"""

    def list(self):
        """"""

    def get(self):
        """"""
