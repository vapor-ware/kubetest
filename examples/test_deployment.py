"""An example of using kubetest to manage a deployment."""

import os


def test_deployment(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'configs',
        'deployment.yaml'
    )

    d = kube.load_deployment(f)

    kube.create(d)

    d.wait_until_ready(timeout=20)
    d.refresh()

    pods = d.get_pods()
    assert len(pods) == 1

    p = pods[0]
    p.wait_until_ready(timeout=10)

    kube.delete(d)
    d.wait_until_deleted(timeout=20)
