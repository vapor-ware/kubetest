def test_156_baseline(kube, clusterinfo):
    kube.wait_for_ready_nodes(1, timeout=3 * 60)
    print(f"cluster info: {vars(clusterinfo)}")
