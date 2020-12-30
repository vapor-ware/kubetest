import pytest


@pytest.fixture
def kubeconfig(request):
    return "~/.kube/config"


def test_154(kube):
    kube.wait_for_ready_nodes(1, timeout=3 * 60)
