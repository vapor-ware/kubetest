def test_88(kube):
    d = kube.load_deployment("deployment.yaml")

    d.create()
    d.wait_until_ready(timeout=30)

    pods = d.get_pods()
    print(pods)
    print("hello")
