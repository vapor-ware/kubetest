"""
"""

from kubernetes import client
import yaml

from kubetest.manifest import new_object


# A global map that matches the Api Client class to its corresponding
# apiVersion so we can get the correct client for the manifest version.
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

    # A reference to an ApiClient that can be used by all
    # ApiObjects to construct the necessary ApiClient.
    _client = client.ApiClient()

    def __init__(self, api_object):
        self.obj = api_object
        self.version = api_object.api_version
        self.name = api_object.metadata.name
        self._api_client = None

    @property
    def api_client(self):
        """"""
        if self._api_client is None:
            c = api_clients.get(self.version)
            # If we didn't find the client in the api_clients dict, raise
            # an error - missing clients will need to be added manually.
            if c is None:
                raise ValueError(
                    'Unsupported Api Client version: {}'.format(self.version)
                )
            # If we did find it, initialize that client version.
            self._api_client = c(self._client)
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

    def create(self, namespace):
        """Create the Deployment under the given namespace.

        This is called by a Kubetest client's `create_deployment` method.
        This is the preferred way of calling this method, as the generated
        namespace for the test case will be provided automatically.

        Args:
            namespace (str): The namespace to create the Deployment under.
        """
        self.obj = self.api_client.create_namespaced_deployment(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, namespace, options=None):
        """Delete the Deployment under the given namespace.

        This is called by a Kubetest client's `create_deployment` method.
        This is the preferred way of calling this method, as the generated
        namespace for the test case will be provided automatically.

        Args:
            namespace (str): The namespace to create the Deployment under.
            options (client.V1DeleteOptions): Options for deployment deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        return self.api_client.delete_namespaced_deployment(
            name=self.name,
            namespace=namespace,
            body=options,
        )

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
