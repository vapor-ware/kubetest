"""An example of using kubetest to manage a service."""

import os
import time


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
    print('---------- loaded svc -------------')
    print(vars(svc))

    dep = kube.load_deployment(d)

    kube.create(svc)
    print('---------- created -------------')
    print(vars(svc))

    kube.create(dep)

    print('---------- waiting ----------')
    start = time.time()
    svc.wait_until_ready(timeout=10)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    svc.refresh()
    print('---------- refreshed -------------')
    print(vars(svc))

    x = svc.status()
    print('---------- status -------------')
    print(x)

    endpoints = svc.get_endpoints()
    print('---------- endpoints -------------')
    print(endpoints)

    x = svc.status()
    print('---------- status -------------')
    print(x)

    status = kube.delete(svc)
    print('---------- deleted -------------')
    print(vars(svc))

    print('---------- status -------------')
    print(status)

    print('---------- waiting ----------')
    start = time.time()
    svc.wait_until_deleted(timeout=20)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    # assert false to fail the test - this allows us to get the
    # captured stdout (e.g. the print statements above)
    assert False
