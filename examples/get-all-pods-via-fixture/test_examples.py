
import pytest
import time
import os


@pytest.mark.applymanifest(os.path.join(os.path.dirname(__file__), 'manifests/deployment-redis.yaml'))
def test_pods_from_deployment_loaded_from_marker(kube):
    """Get the Pods for a Deployment which is loaded via the kubetest
    'applymanifest' marker.

    When kubetest loads manifest files via markers, it does not pass
    a reference to those objects to the test case (as one would get
    if using a fixture). In order to get the pods for the deployment,
    you will need to get the deployment from the test namespace and
    use that deployment object to get its pods.
    """

    # Wait for the objects registered via marker to be ready.
    kube.wait_for_registered(timeout=30)
    time.sleep(10)

    deployments = kube.get_deployments()

    # Get the redis-master deployment. The `deployments` response is a
    # dict where the key is the name for the object (e.g. as defined in
    # the manifest), and the value is the corresponding Deployment object.
    assert 'redis-master' in deployments
    redis_master = deployments['redis-master']

    # Get the pods for the deployment. Since the deployment is defined
    # as having one replica, we expect to only get back one pod.
    pods = redis_master.get_pods()
    assert len(pods) == 1


def test_pods_from_deployment_loaded_in_test_case(kube):
    """Get the Pods for a Deployment which is loaded within the test
    case itself.

    The Deployment is loaded directly in the test case, so you have
    direct access to the its corresponding deployment object. You can
    use that to get the pods for the deployment.
    """

    deployment = kube.load_deployment(os.path.join(os.path.dirname(__file__), 'manifests/deployment-redis.yaml'))
    deployment.create()
    deployment.wait_until_ready(timeout=30)

    # We already have a reference to the deployment object, so just get
    # its pods. Since the deployment is defined as having one replica,
    # we expect to only get back one pod.
    pods = deployment.get_pods()
    assert len(pods) == 1


@pytest.mark.applymanifests('manifests', files=[
    'deployment-redis.yaml',
    'deployment-frontend.yaml',
])
def test_all_pods_for_test_namespace(kube):
    """Get all of the Pods within the test namespace.

    In some cases, you may not care about the deployment itself or
    just want an overview of what is running. In this case, traversing
    all of the deployments for their pods, while doable, is an extra
    step and adds complexity to a test case. This test provides an
    example of how to get all Pods, agnostic of their Deployment,
    within the namespace of the test case.
    """

    # Wait for the objects registered via marker to be ready.
    kube.wait_for_registered(timeout=30)

    # Get all pods in the test namespace (default behavior). The redis-master
    # deployment is configured with one replica, and the frontend deployment
    # has 3 replicas. We should expect to have a total of 4 pods.
    pods = kube.get_pods()
    assert len(pods) == 4


def test_all_pods_for_other_namespace(kube):
    """Get all of the Pods within some other namespace.

    This is generally not recommended, as each test gets its own
    namespace to keep it isolated from anything else which may be
    using the cluster (including other test cases). While not
    recommended, it can still be done if desired.
    """

    # Get the pods belonging to the kube-system namespace. Since this
    # is running on a Kubernetes cluster, there should be some pods in
    # this namespace.
    pods = kube.get_pods(namespace='kube-system')
    assert len(pods) > 0


@pytest.mark.applymanifests('manifests', files=[
    'deployment-redis.yaml',
    'deployment-frontend.yaml',
])
def test_all_pods_via_custom_fixture(kube, custom_pods):
    """Get all of the Pods with a custom fixture.

    This example uses a custom fixture (defined in conftest.py) to
    get all Pods. Since this only serves as an example, the custom
    fixture does not do anything special - it merely returns a list
    of the Pod names. Using a custom fixture can be useful if you
    need to do any pre-processing, aggregation, filtering, etc. on
    the collection of Pods.
    """

    # Wait for the objects registered via marker to be ready.
    kube.wait_for_registered(timeout=30)

    # Sleep for a bit to ensure everything has time to come up.
    time.sleep(10)

    # Get all pods in the test namespace (default behavior). The redis-master
    # deployment is configured with one replica, and the frontend deployment
    # has 3 replicas. We should expect to have a total of 4 pods.
    assert len(custom_pods) == 4

    count_frontend = 0
    count_master = 0

    for pod_name in custom_pods:
        if 'frontend' in pod_name:
            count_frontend += 1
        if 'redis-master' in pod_name:
            count_master += 1

    assert count_frontend == 3
    assert count_master == 1

