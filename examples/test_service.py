"""An example of using kubetest to manage a service."""

import os


def test_service(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'configs',
        'service.yaml'
    )

    d = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'configs',
        'deployment.yaml'
    )

    svc = kube.load_service(f)
    dep = kube.load_deployment(d)

    kube.create(svc)
    kube.create(dep)

    svc.wait_until_ready(timeout=10)
    svc.refresh()

    endpoints = svc.get_endpoints()
    assert len(endpoints) == 1

    kube.delete(svc)
    kube.delete(dep)

    svc.wait_until_deleted(timeout=20)
    svc.wait_until_deleted(timeout=20)
