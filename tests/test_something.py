# # UNCOMMENT TO TEST KUBETEST MANUALLY

# import os
# import time
#
#
# def test_something(k8s):
#
#     f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deployment.yaml')
#     d = k8s.load_deployment(f)
#     dd = k8s.create_deployment(d)
#
#     print(dd)
#
#     time.sleep(5)
#
#     assert True
#
#
# def test_something2(k8s):
#
#     f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deployment.yaml')
#     d = k8s.load_deployment(f)
#     dd = k8s.create_deployment(d)
#
#     print(dd)
#
#     time.sleep(5)
#
#     assert False
