import pytest


@pytest.fixture
def kubeconfig(request):
    return "~/.kube/config"


def test_156(kube, clusterinfo):
    kube.wait_for_ready_nodes(1, timeout=3 * 60)
    print(f"cluster info: {vars(clusterinfo)}")
