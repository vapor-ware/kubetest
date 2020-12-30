"""An example of using kubetest to manage a configmap."""

import os


def test_configmap(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "configs", "configmap.yaml"
    )

    cm = kube.load_configmap(f)

    kube.create(cm)

    cm.wait_until_ready(timeout=10)
    cm.refresh()

    kube.delete(cm)

    cm.wait_until_deleted(timeout=20)
