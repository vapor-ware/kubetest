
https://github.com/vapor-ware/kubetest/issues/156

### Summary

This is a baseline (bl) test case for issue #156. It verifies that the `clusterinfo` fixture
will use the value specified by the `--kube-config` command line arg when specified. See
[regression/156](../156) for more details.

#### Expectations

When run with a command-line defined kubeconfig, a test using the `clusterinfo` fixture should
resolve the cluster info using the kubeconfig specified by the command line flag.
