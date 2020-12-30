
Writing Tests
=============

kubetest is designed to interface with a Kubernetes cluster, so before you
begin writing tests with kubetest, be sure that you have access to a cluster,
whether on Google Container Engine, via minikube, or through your own custom
cluster. Generally, where the cluster runs shouldn't be an issue, as long as
you can access it from wherever the tests are being run.

Cluster Configuration
---------------------

By default, kubetest will look for a config file at ``~/.kube/config`` and the
current context -- this is the same behavior that ``kubectl`` utilizes for the
resolving cluster config. Generally, if you can reach your cluster via.
``kubectl``, you should be able to use it with kubetest.

If you wish to specify a different config file and/or context, you can pass it
in via the ``--kube-config`` and ``--kube-context`` flags.
See :ref:`command_line_usage` for more details.

You can also write a ``kubeconfig`` fixture which provides the path to the
config file and/or a ``kubecontext`` fixture which provides the name of the
context to be used.  This may be useful in case your cluster is generated as
part of the tests or you wish to use specific contexts in different parts of
the suite.

.. code-block:: python

    import pytest
    import subprocess
    from typing import Optional


    @pytest.fixture
    def kubeconfig() -> str:
        # Here, Terraform creates a cluster and outputs a kubeconfig
        # at somepath
        subprocess.check_call(['terraform', 'apply'])
        return 'somepath/kubeconfig'


    @pytest.fixture
    def kubecontext() -> Optional[str]:
        # Return None to use the current context as set in the kubeconfig
        # Or return the name of a specific context in the kubeconfig
        return 'kubetest-cluster'


     def test_my_terraformed_cluster(kube):
         # Use your cluster!
         pass



Loading Manifests
-----------------

It is recommended, though not required, to test against pre-defined manifest
files. These files can be kept anywhere relative to your tests and can be
organized however you like. Each test can have its own directory of manifests,
or you can pick and choose individual manifest files for the test case.

While you can generate your own manifests within the tests themselves (e.g.
by initializing a Kubernetes API object), this can become tedious and clutter
up the tests. If you do choose to go this route, you can still use all of the
kubetest functionality by wrapping supported objects with their equivalent
kubetest wrapper. For example,

.. code-block:: python

    from kubernetes import client
    from kubetest.objects import Deployment


    # Create a Kubernetes API Object
    raw_deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name='test-deployment'
        ),
        spec=client.V1DeploymentSpec(
            replicas=2,
            template=client.V1PodTemplateSpec(
                ...
            )
        )
    )

    # Wrap it in the kubetest wrapper
    wrapped_deployment = Deployment(raw_deployment)

If you use manifest files, you can load them directly into wrapped API objects
easily via the kubetest :ref:`kubetest_client`, which is provided to a test
case via the :ref:`kube_fixture` fixture.

.. code-block:: python

    def test_something(kube):

        f = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'manifests',
            'deployment.yaml'
        )

       deployment = kube.load_deployment(f)


Often, tests will multiple resources that need to be loaded from manifest YAMLs.
It can be tedious to construct all of the paths, load them, and create them at
the start of a test. kubetest provides the :ref:`applymanifests_marker` marker
that allows you to specify an entire directory to load, or specific files from
a directory. The example below loads the same file as the previous example using
the ``applymanifests`` marker.

.. code-block:: python

    @pytest.mark.applymanifests('manifests', files=[
        'deployment.yaml'
    ])
    def test_something(kube):
        ...

Once a manifest is loaded, you will have (or be able to get) a reference to the
created API Objects which offer more functionality.

Creating Resources
------------------

If you use the :ref:`applymanifests_marker`, as described in the previous section,
the manifest will be loaded and created for you in the test case namespace of your
cluster (test case namespaces are automatically managed via the :ref:`kube_fixture`).

You may want to load resources manually, or load and create some at a later time
in the test. This can be done via the ``kube`` client

.. code-block:: python

    def test_something(kube):

        # ...
        # do something first
        # ...

        deployment = kube.load_deployment('path/to/deployment.yaml')
        kube.create(deployment)


It can also be done through the resource reference itself

.. code-block:: python

    def test_something(kube):

        # ...
        # do something first
        # ...

        deployment = kube.load_deployment('path/to/deployment.yaml')
        deployment.create()

Deleting Resources
------------------

It is not necessary to delete resources at the end of a test case. kubetest
automatically manages the namespace for the test case. When the test completes,
it will delete the namespace from the cluster which will also delete any remaining
resources in that namespace.

It can still be useful to delete things while testing, e.g. to simulate a service
failure and to test the subsequent disaster recovery process. Similar to resource
creation, resource deletion can be done either through the object reference or
through the ``kube`` client

.. code-block:: python

    def test_something(kube):

        # ...
        # created resource, did some testing, now need to remove
        # the resource
        # ...

        # Method #1 - delete via the kube client
        kube.delete(deployment)

        # Method #2 - delete via the object reference
        deployment.delete()

Test Namespaces
---------------

By default, ``kubetest`` will automatically generate a new Namespace for each test case,
using the test name and a timestamp for the namespace name to ensure uniqueness. This behavior
may not be desired in all cases, such as when users may not have permissions to create a new
namespace on the cluster, or the tests are written against an already-running deployment in
an existing namespace. In such cases, the :ref:`_namespace_marker` may be used.

Waiting
-------

The time it takes for a resource to start, stop, or become ready can vary across
numerous factors. It is not always reliable to just ``time.sleep(10)`` and hope that
the desired state is met (nor is it efficient). To help with this, there are a number
of *wait* functions provided by kubetest. For a full accounting of all wait functions,
see the :ref:`reference`.

Below are some simple examples of select wait function usage.

Ready Nodes
~~~~~~~~~~~

If you are running on a cluster that can scale automatically, you may need to wait
for the correct number of nodes to be available and ready before the test can run.

.. code-block:: python

    @pytest.mark.applymanifests('manifests')
    def test_something(kube):
        # wait for 3 nodes to be available and ready
        kube.wait_for_ready_nodes(3, timeout=5 * 60)


Created Object
~~~~~~~~~~~~~~

Wait until an object has been created on the cluster.

.. code-block:: python

    def test_something(kube):
        deployment = kube.load_deployment('path/to/deployment.yaml')
        kube.create(deployment)
        kube.wait_until_created(deployment, timeout=30)


Pod Containers Start
~~~~~~~~~~~~~~~~~~~~

Wait until a Pod's containers have all started.

.. code-block:: python

    @pytest.mark.applymanifests('manifests')
    def test_something(kube):
        pods = kube.get_pods()
        for pod in pods.values():
            pod.wait_until_containers_start(timeout=60)
