"""An example of using kubetest to manage a configmap."""

import os
import time


def test_configmap(kube):

    f = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'configs',
        'configmap.yaml'
    )

    cm = kube.load_configmap(f)
    print('---------- loaded -------------')
    print(vars(cm))

    kube.create(cm)
    print('---------- created -------------')
    print(vars(cm))

    print('---------- waiting ----------')
    start = time.time()
    cm.wait_until_ready(timeout=10)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    cm.refresh()
    print('---------- refreshed -------------')
    print(vars(cm))

    status = kube.delete(cm)
    print('---------- deleted -------------')
    print(vars(cm))

    print('---------- status -------------')
    print(status)

    print('---------- waiting ----------')
    start = time.time()
    cm.wait_until_deleted(timeout=20)
    end = time.time()
    print('---------- done ({}s) ----------'.format(end - start))

    # assert false to fail the test - this allows us to get the
    # captured stdout (e.g. the print statements above)
    assert False
