
https://github.com/vapor-ware/kubetest/issues/130

### Summary

A change to how the `--kube-config` flag was used internally broke previous capabilities
to allow using a kubeconfig fixture override.

#### Expectations

When run with a valid `--kube-config` flag, the test should still fail because the kubeconfig
fixture should override, using the `test.kubeconfig` file.

```
pytest -s --kube-config=~/.kube/config .
```
