# kubetest

[![CircleCI](https://circleci.com/gh/vapor-ware/kubetest.svg?style=shield&circle-token=56a800b7205681b0543c145f4e168d08d3048433)](https://circleci.com/gh/vapor-ware/kubetest)
[![PyPI](https://img.shields.io/pypi/v/kubetest.svg)](https://pypi.org/project/kubetest/)
[![Documentation Status](https://readthedocs.org/projects/kubetest/badge/?version=latest)](https://kubetest.readthedocs.io/en/latest/?badge=latest)

Kubetest is a [pytest][pytest] plugin that makes it easier to manage a Kubernetes
cluster within your integration tests. While you can use the [Kubernetes Python client][k8s-py]
directly, this plugin provides some cluster and object management on top of that so you can
spend less time setting up and tearing down tests and more time actually writing your tests.
In particular, this plugin is useful for testing your Kubernetes infrastructure (e.g., ensure
it deploys and behaves correctly) and for testing disaster recovery scenarios (e.g. delete a
pod or deployment and inspect the aftermath).

**Features:**
* Simple API for common cluster interactions.
* Uses the Kubernetes Python client as the backend, so more complex custom
  actions are possible.
* Load Kubernetes manifest YAMLs into their Kubernetes models.
* Each test is run in its own namespace and the namespace is created and
  deleted automatically.
* Detailed logging to help debug error cases.
* Wait functions for object readiness and for object deletion.
* Get container logs and search for expected logging output.
* Plugin-managed RBAC permissions at test-case granularity using pytest markers.

For more information, see the [kubetest documentation][kubetest-docs].

## Installation
This plugin can be installed with `pip`

```
pip install kubetest
```

Note that the `kubetest` package has entrypoint hooks defined in its [`setup.py`](setup.py)
which allow it to be automatically made available to pytest. This means that it will run
whenever pytest is run. Since `kubetest` expects a cluster to be set up and to be given
configuration for that cluster, pytest will fail if those are not present. It is therefore
recommended to only install `kubetest` in a virtual environment or other managed environment,
such as a CI pipeline, where you can assure that cluster access and configuration are
available.

## Usage
Once installed, the following `pytest` command-line parameters become available:

```
pytest \
    [--kube-config <path-to-config>] \
    [--kube-error-log-lines <count>] \
    [--kube-log-level <level>] \
    [--kube-disable]
```

- **`--kube-config`**: The path to the config file to use for your cluster. If not specified,
  it defaults to the same config that `kubectl` uses at `~/.kube/config`
- **`--kube-error-log-lines`**: Set the number of lines to tail from the container logs for
  a test namespace when a test fails. By default this is set to 50. If you want to show all
  container logs, set this to -1. If you do not wish to show container logs, set this to 0.
- **`--kube-log-level`**: Set the logging level for kubetest. The default log level is *warning*.
  Setting the log level to *info* will provide logging for kubetest actions. Setting the log level
  to *debug* will log out the Kubernetes object state for various actions as well.
- **`--kube-disable`**: Disable kubetest from running initial cluster configuration.

Note that kubetest expects a cluster to be available and requires some form of configuration
in order to interface with that cluster.

## Pytest Integration
Below, a brief overview is given for the various components of kubetest exposed via pytest.
For more detailed information, see the [kubetest documentation][kubetest-docs].

### Fixtures

#### [`kube`](https://kubetest.readthedocs.io/en/latest/fixtures.html#kube)
The `kube` fixture is the "entrypoint" into using kubetest. It provides a basic API for
managing your cluster.

```python
def test_deployment(kube):
    """Example test case for creating and deleting a deployment."""
    
    d = kube.load_deployment('path/to/deployment.yaml')
    
    d.create()
    d.wait_until_ready(timeout=10)
    
    # test some deployment state
    
    d.delete()
    d.wait_until_deleted(timeout=10)
```

The above example shows a simplified test case using kubetest to load a deployment
from file, create it on the cluster, wait until it is in the ready state, delete the
deployment, and then wait until it is deleted.

The two final steps - `delete` and `wait_until_deleted` can be useful when testing
a failure scenario, but does not need to be specified at the end of a test case as
a means of cluster cleanup. Because each test will run in its own namespace, once the
test completes, the namespace will be deleted from the cluster, which will in turn
delete all objects in that namespace, cleaning out all test artifacts.

### Markers
To see all markers, run `pytest --kube-disable --markers` with kubetest installed.
This will list the kubetest-provided markers along with a detailed description of
what they do.

#### [`applymanifests`](https://kubetest.readthedocs.io/en/latest/markers.html#apply-manifests)
Allows you to specify manifest directories or files that should be used for the test
case. This will automatically load the manifest and create the API object on the cluster.

*Example:*
```python
@pytest.mark.applymanifests('manifests')
def test_something(kube):
    ...
```

#### [`clusterrolebinding`](https://kubetest.readthedocs.io/en/latest/markers.html#cluster-role-binding)
Allows you to specify different [cluster roles](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
that should be applied to the cluster for the test case.

*Example:*
```python
@pytest.mark.clusterrolebinding('cluster-admin')
def test_something(kube):
    ...
```

#### [`rolebinding`](https://kubetest.readthedocs.io/en/latest/markers.html#role-binding)
Allows you to specify different [roles](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
that should be applied to the cluster for the test namespace of the test case.

*Example:*
```python
@pytest.mark.rolebinding('custom-role')
def test_something(kube):
    ...
```

## Feedback
Feedback for kubetest is greatly appreciated! If you experience any issues, find the
documentation unclear, have feature requests, or just have questions about it, we'd
love to know. Feel free to open an issue for any feedback you may have.

## License
kubetest is released under the [GPL-3.0](LICENSE) license.



[pytest]: https://docs.pytest.org/en/latest/
[k8s-py]: https://github.com/kubernetes-client/python
[kubetest-docs]: https://kubetest.readthedocs.io/en/latest/
