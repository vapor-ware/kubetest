"""An example of using kubetest to manage a cluster role binding."""

import os


def test_cluster_role_binding(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "configs",
        "clusterrolebinding.yaml",
    )

    cm = kube.load_clusterrolebinding(f)

    kube.create(cm)

    cm.wait_until_ready(timeout=10)
    cm.refresh()

    kube.delete(cm)

    cm.wait_until_deleted(timeout=20)
