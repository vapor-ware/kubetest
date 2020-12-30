"""An example of using kubetest to manage a serviceaccount."""

import os
from time import sleep


def test_serviceaccount(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "configs", "serviceaccount.yaml"
    )

    sa = kube.load_serviceaccount(f)

    kube.create(sa)

    sa.wait_until_ready(timeout=10)
    sa.refresh()

    kube.delete(sa)

    sa.wait_until_deleted(timeout=20)
