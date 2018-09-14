# # UNCOMMENT TO TEST KUBETEST MANUALLY

import os
import time


def test_something(kube):

    f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deployment.yaml')
    d = kube.load_deployment(f)
    print('---------- loaded -------------')
    print(d)

    kube.create_deployment(d)
    print('---------- created -------------')
    print(d)

    time.sleep(5)

    status = kube.delete_deployment(d)
    print('---------- deleted -------------')
    print(d)

    print('---------- status -------------')
    print(status)

    assert False


def test_something2(kube):

    f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deployment.yaml')
    d = kube.load_deployment(f)
    dd = kube.create_deployment(d)

    print(dd)

    time.sleep(5)

    assert True
