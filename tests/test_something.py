# # UNCOMMENT TO TEST KUBETEST MANUALLY

# import os
# import time
#
#
# def test_something(kube):
#
#     f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deployment.yaml')
#     d = kube.load_deployment(f)
#     print('---------- loaded -------------')
#     print(vars(d))
#
#     kube.create_deployment(d)
#     print('---------- created -------------')
#     print(vars(d))
#
#     time.sleep(5)
#
#     d.refresh()
#     print('---------- refreshed -------------')
#     print(vars(d))
#
#     status = kube.delete_deployment(d)
#     print('---------- deleted -------------')
#     print(vars(d))
#
#     print('---------- status -------------')
#     print(status)
#
#     # assert false to fail the test - this allows us to get the
#     # captured stdout (e.g. the print statements above)
#     assert False
#
#
# def test_something2(kube):
#
#     f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deployment.yaml')
#     d = kube.load_deployment(f)
#     dd = kube.create_deployment(d)
#
#     print(dd)
#
#     time.sleep(5)
#
#     assert True
