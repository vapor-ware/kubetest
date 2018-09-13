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

    def create_namespace(self, name):
        """Create a namespace with the given name in the cluster.

        Args:
            name (str): The name of the namespace to create.
        """
        return client.CoreV1Api(api_client=self.api_client).create_namespace(client.V1Namespace(
            metadata=client.V1ObjectMeta(
                name=name
            )
        ))

    def delete_namespace(self, name):
        """Delete a namespace with the given name in the cluster.

        Args:
            name (str): The name of the namespace to delete.
        """
        return client.CoreV1Api(api_client=self.api_client).delete_namespace(
            name=name, body=client.V1DeleteOptions()
        )

    # FIXME (etd): below is temporary for testing, it may change.

    @staticmethod
    def load_deployment(path):
        """"""
        return objects.Deployment.load(path)

    def create_deployment(self, deployment):
        """"""
        return client.AppsV1beta2Api(api_client=self.api_client).create_namespaced_deployment(
            self.namespace, deployment.obj
        )
