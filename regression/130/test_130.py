
import pytest
import os


@pytest.fixture
def kubeconfig(request):
    x = os.path.join(os.path.dirname(__file__), 'test.kubeconfig')
    return x


def test_nginx(kube):
    """An example test against an Nginx deployment."""

    kube.wait_for_ready_nodes(3, timeout=5 * 60)
