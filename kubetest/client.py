"""Test client provided by kubetest for managing kubernetes objects."""

from kubernetes import client

from kubetest import objects


class TestClient:
    """Test client for managing kubernetes objects."""

    def __init__(self, namespace):
        self.namespace = namespace

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

    def load_configmap(self, path, set_namespace=True):
        """Load a ConfigMap manifest into a Configmap object.

        By default, this will augment the ConfigMap Api Object with
        the generated test case namespace. This behavior can be
        disabled with the `set_namespace` flag.

        Args:
            path (str): The path to the ConfigMap manifest.
            set_namespace (bool): Enable/disable the automatic
                augmentation of the ConfigMap namespace.

        Returns:
            Configmap: The ConfigMap for the specified manifest.
        """
        configmap = objects.Configmap.load(path)
        if set_namespace:
            configmap.namespace = self.namespace
        return configmap

    def load_deployment(self, path, set_namespace=True):
        """Load a Deployment manifest into a Deployment object.

        By default, this will augment the Deployment Api Object with
        the generated test case namespace. This behavior can be
        disabled with the `set_namespace` flag.

        Args:
            path (str): The path to the Deployment manifest.
            set_namespace (bool): Enable/disable the automatic
                augmentation of the Deployment namespace.

        Returns:
            Deployment: The Deployment for the specified manifest.
        """
        deployment = objects.Deployment.load(path)
        if set_namespace:
            deployment.namespace = self.namespace
        return deployment

    def load_pod(self, path, set_namespace=True):
        """Load a Pod manifest into a Pod object.

        By default, this will augment the Pod Api Object with
        the generated test case namespace. This behavior can be
        disabled with the `set_namespace` flag.

        Args:
            path (str): The path to the Pod manifest.
            set_namespace (bool): Enable/disable the automatic
                augmentation of the Pod namespace.

        Returns:
            Pod: The Pod for the specified manifest.
        """
        pod = objects.Pod.load(path)
        if set_namespace:
            pod.namespace = self.namespace
        return pod

    def load_service(self, path, set_namespace=True):
        """Load a Service manifest into a Service object.

        By default, this will augment the Service Api Object with
        the generated test case namespace. This behavior can be
        disabled with the `set_namespace` flag.

        Args:
            path (str): The path to the Service manifest.
            set_namespace (bool): Enable/disable the automatic
                augmentation of the Service namespace.

        Returns:
            Service: The Service for the specified manifest.
        """
        service = objects.Service.load(path)
        if set_namespace:
            service.namespace = self.namespace
        return service

    # ****** Namespace ******

    @staticmethod
    def create_namespace(name):
        """Create a namespace with the given name in the cluster.

        Args:
            name (str): The name of the namespace to create.
        """
        return client.CoreV1Api().create_namespace(client.V1Namespace(
            metadata=client.V1ObjectMeta(
                name=name
            )
        ))

    @staticmethod
    def delete_namespace(name):
        """Delete a namespace with the given name in the cluster.

        Args:
            name (str): The name of the namespace to delete.
        """
        return client.CoreV1Api().delete_namespace(
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
        if deployment.namespace is None:
            deployment.namespace = self.namespace
        deployment.create()

    def delete_deployment(self, deployment):
        """Delete the given deployment from the Kubernetes cluster under the
        namespace generated for the test case.
        """
        if deployment.namespace is None:
            deployment.namespace = self.namespace
        deployment.delete()

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
