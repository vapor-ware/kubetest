import pytest


@pytest.fixture()
def custom_pods(kube):
    """A custom fixture used as an example of how to extend the kube
    fixture for common actions, such as pre-processing data.

    See the pytest documentation for details on how fixtures work,
    and how they can be loaded from conftest files.
    """

    # Get resources via kubetest
    pods = kube.get_pods()

    # Perform any other processing
    return pods.keys()
