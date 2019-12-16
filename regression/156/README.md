
https://github.com/vapor-ware/kubetest/issues/156

### Summary

When the kubeconfig is provided by a pytest fixture and not via the `--kube-config` command line
flag, the `clusterinfo` fixture will fail, since it uses the kubeconfig value specified by the
command line flag and does not account for custom fixture.

#### Expectations

When run with a fixture-defined kubeconfig, a test using the `clusterinfo` fixture should
resolve the cluster info using the kubeconfig provided by the custom fixture.
