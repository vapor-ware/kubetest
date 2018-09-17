"""An example of using kubetest to manage a deployment."""

import os
import time


def test_something(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'configs',
        'deployment.yaml'
    )

    d = kube.load_deployment(f)
    print('---------- loaded -------------')
    print(vars(d))

    kube.create(d)
    print('---------- created -------------')
    print(vars(d))

    print('---------- waiting ----------')
    start = time.time()
    d.wait_until_ready(timeout=10)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    d.refresh()
    print('---------- refreshed -------------')
    print(vars(d))

    x = d.status()
    print('---------- status -------------')
    print(x)

    pods = d.get_pods()
    print('---------- pods -------------')
    # print(pods)
    p = pods[0]

    print('---------- waiting ----------')
    start = time.time()
    p.wait_until_ready(timeout=10)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    status = kube.delete(d)
    print('---------- deleted -------------')
    print(vars(d))

    print('---------- status -------------')
    print(status)

    print('---------- waiting ----------')
    start = time.time()
    d.wait_until_deleted(timeout=20)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    # assert false to fail the test - this allows us to get the
    # captured stdout (e.g. the print statements above)
    assert False
