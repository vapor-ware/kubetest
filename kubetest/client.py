"""Test client provided by kubetest for managing kubernetes objects."""

from kubernetes import client

from kubetest import objects


class TestClient:
    """Test client for managing kubernetes objects."""

    def __init__(self, namespace):
        self.namespace = namespace
        self.api_client = client.ApiClient()

    def setup(self):
        """Setup the test client.

        This performs all actions needed in order for the client to be
        ready to use by a test case. This is called in the k8s fixture
        so the client is only initialized when the test actually requests
        it.
        """
        self.create_namespace(self.namespace)

    def teardown(self):
        """Teardown the test client.

        This performs all actions needed in order for the client to be
        cleaned up after a test case has been run. This is called in the
        pytest runtest teardown hook.
        """
        self.delete_namespace(self.namespace)

    # ****** Manifest Loaders ******

    @staticmethod
    def load_configmap(path):
        """Load a ConfigMap manifest into a Configmap object.

        Args:
            path (str): The path to the ConfigMap manifest.

        Returns:
            Configmap: The ConfigMap for the specified manifest.
        """
        return objects.Configmap.load(path)

    @staticmethod
    def load_deployment(path):
        """Load a Deployment manifest into a Deployment object.

        Args:
            path (str): The path to the Deployment manifest.

        Returns:
            Deployment: The Deployment for the specified manifest.
        """
        return objects.Deployment.load(path)

    @staticmethod
    def load_pod(path):
        """Load a Pod manifest into a Pod object.

        Args:
            path (str): The path to the Pod manifest.

        Returns:
            Pod: The Pod for the specified manifest.
        """
        return objects.Pod.load(path)

    @staticmethod
    def load_service(path):
        """Load a Service manifest into a Service object.

        Args:
            path (str): The path to the Service manifest.

        Returns:
            Service: The Service for the specified manifest.
        """
        return objects.Deployment.load(path)

    # ****** Namespace ******

    def create_namespace(self, name):
        """Create a namespace with the given name in the cluster.

        Args:
            name (str): The name of the namespace to create.
        """
        api = client.CoreV1Api(api_client=self.api_client)
        return api.create_namespace(client.V1Namespace(
            metadata=client.V1ObjectMeta(
                name=name
            )
        ))

    def delete_namespace(self, name):
        """Delete a namespace with the given name in the cluster.

        Args:
            name (str): The name of the namespace to delete.
        """
        api = client.CoreV1Api(api_client=self.api_client)
        return api.delete_namespace(
            name=name, body=client.V1DeleteOptions()
        )

    # ****** Deployment ******

    # TODO (etd): If we standardize on all objects having a create/delete fn, we could
    # just have a `create` and `delete` here, with no need to have object-specific
    # create/delete methods.

    def create_deployment(self, deployment):
        """Create the given deployment on the Kubernetes cluster under the
        namespace generated for the test case.
        """
        deployment.create(self.namespace)

    def delete_deployment(self, deployment):
        """Delete the given deployment from the Kubernetes cluster under the
        namespace generated for the test case.
        """
        deployment.delete(self.namespace)

    def get_deployments(self):
        """Get all of the deployments under the test case namespace.

        Returns:
            dict: The deployments, where the key is the deployment name
                and the value is the Deployment.
        """
        deployment_list = client.AppsV1Api().list_namespaced_deployment(self.namespace)

        deployments = {}
        for item in deployment_list.items:
            d = objects.Deployment(item)
            deployments[d.name] = d

        return deployments
