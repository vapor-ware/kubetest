# Use Case: Getting all pods in the test namespace using the kubetest fixture

> Ref: https://github.com/vapor-ware/kubetest/issues/104

This directory contains examples for getting pods for test cases. There are a number
of ways to do this, depending on the end goal. Each test case's docstring provides
more detail on the method for getting pods.

### Contents:

* `manifests`: A directory containing the Kubernetes manifest files that are used
  in the test examples. Note: these example manifests are largely taken from the
  [official kubernetes examples](https://github.com/kubernetes/examples).
* `test_examples.py`: The file containing the test cases, showcasing different
  methods to get pods for the test.
* `conftest.py`: Custom fixture definitions for [pytest](https://docs.pytest.org/en/latest/writing_plugins.html#conftest-py-plugins).

### Running
With `pytest` and `kubetest` installed, and a kubeconfig file (`config` -- you will need
to supply the path to your own kubeconfig file) for the test cluster:

```console
pytest --kube-config=./config --suppress-insecure-request .
================================================== test session starts ===================================================
platform darwin -- Python 3.6.7, pytest-4.4.0, py-1.8.0, pluggy-0.9.0
kubetest config file: ./config
kubetest context: current context
rootdir: /Users/edaniszewski/dev/vaporio/kubetest
plugins: asyncio-0.10.0, kubetest-0.1.0
collected 5 items                                                                                                        

test_examples.py .....                                                                                             [100%]

=============================================== 5 passed in 42.88 seconds ================================================

```

> Note: The `--suppress-insecure-request` seen above is to suppress warnings generated
> when running tests on a cluster without SSL enabled (e.g. a local cluster).