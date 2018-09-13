"""
"""

import kubernetes
import yaml

from kubetest.manifest import new_object

# TODO (etd): Everything here is just a stub and needs to be filled out
# and thought out some more.


class ApiObject:
    """ApiObject is the base class for all Kubernetes API objects."""

    obj_type = None

    def __init__(self, api_object):
        self.obj = api_object

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

        Raises:

        """
        with open(path, 'r') as f:
            manifest = yaml.load(f)

        obj = new_object(cls.obj_type, manifest)
        return cls(obj)


class Configmap(ApiObject):
    """"""

    """
    * create
    * load
    * get
    * wait until ready?
    * delete
    * wait until deleted?
    """

    obj_type = kubernetes.client.V1ConfigMap

    def __init__(self, api_object):
        super().__init__(api_object)


class Deployment(ApiObject):
    """"""

    """
    * Create
    * Load
    * Get
    * Wait for ready
    * Delete
    * Wait for delete
    """

    obj_type = kubernetes.client.V1Deployment

    def __init__(self, api_object):
        super().__init__(api_object)


class Node(ApiObject):
    """"""

    """
    * list
    * get state
    * wait for ready
    * delete?
    * wait for delete?
    """

    obj_type = kubernetes.client.V1Node

    def __init__(self, api_object):
        super().__init__(api_object)


class Pod(ApiObject):
    """"""

    """
    * list
    * list from deployment
    * wait until ready
    * get logs
    * get state/status?
    * proxy get?
    """

    obj_type = kubernetes.client.V1Pod

    def __init__(self, api_object):
        super().__init__(api_object)


class Service(ApiObject):
    """"""

    """
    * create
    * load
    * wait until ready
    * delete
    * wait until deleted
    """

    obj_type = kubernetes.client.V1Service

    def __init__(self, api_object):
        super().__init__(api_object)
