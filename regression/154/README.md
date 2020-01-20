
https://github.com/vapor-ware/kubetest/issues/154

### Summary

When the kubeconfig is provided by a pytest fixture and not via the `--kube-config` command line
flag, the kubetest test manager does not run its teardown functionality due to an explicit
check for the `--kube-config` flag, which is a remnant from before the introduction of the
`kubeconfig` fixture.

```python
if item.config.getoption('kube_config'):
    manager.teardown(item.nodeid)
```

#### Expectations

When run with a fixture-defined kubeconfig, the test should run (and pass) and the
test namespace should be cleaned up afterwards.

```console
$ pytest -s .
============================= test session starts =============================
platform darwin -- Python 3.6.7, pytest-4.4.0, py-1.8.0, pluggy-0.9.0
kubetest config file: default
kubetest context: current context
rootdir: /Users/edaniszewski/dev/vaporio/kubetest
plugins: requests-mock-1.6.0, grpc-0.7.0, asyncio-0.10.0, kubetest-0.5.0
collected 1 item                                                              

test_154.py .

========================== 1 passed in 0.07 seconds ===========================
$
$ kubectl get ns
NAME                                 STATUS   AGE
default                              Active   36m
docker                               Active   35m
kube-node-lease                      Active   36m
kube-public                          Active   36m
kube-system                          Active   36m
```
