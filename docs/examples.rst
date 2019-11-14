
.. _examples:

Examples
========

Deploy Nginx
------------

In this example test, we define a simple Nginx deployment and test that when
we deploy it, it has the expected number of replicas and each pod returns the
default *"welcome to nginx"* text when we ``HTTP GET "/"``.

The file structure for this example would look like:

.. code-block:: none

    configs/
        nginx.yaml
    test_nginx.py


Where the files listed above have the following contents:

.. code-block:: yaml
   :caption: configs/nginx.yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx-deployment
      labels:
        app: nginx
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: nginx
      template:
        metadata:
          labels:
            app: nginx
        spec:
          containers:
          - name: nginx
            image: nginx:1.7.9
            ports:
            - containerPort: 80


.. code-block:: python
   :caption: test_nginx.py

    import pytest


    @pytest.mark.applymanifests('configs', files=[
        'nginx.yaml'
    ])
    def test_nginx(kube):
        """An example test against an Nginx deployment."""

        # wait for the manifests loaded by the 'applymanifests' marker
        # to be ready on the cluster
        kube.wait_for_registered(timeout=30)

        deployments = kube.get_deployments()
        nginx_deploy = deployments.get('nginx-deployment')
        assert nginx_deploy is not None

        pods = nginx_deploy.get_pods()
        assert len(pods) == 3, 'nginx should deploy with three replicas'

        for pod in pods:
            containers = pod.get_containers()
            assert len(containers) == 1, 'nginx pod should have one container'

            resp = pod.http_proxy_get('/')
            assert '<h1>Welcome to nginx!</h1>' in resp


With ``kubetest`` installed and a cluster available and configurations at ``~/.kube/config``,
we can run the test

.. code-block:: console

    $ pytest -s .
    =================================== test session starts ===================================
    platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
    kubetest config file: default
    rootdir: /Users/edaniszewski/dev/examples, inifile:
    plugins: kubetest-0.0.1
    collected 1 item

    test_nginx.py .

    ================================ 1 passed in 5.35 seconds =================================
    _________________________________________ summary _________________________________________
      examples: commands succeeded
      congratulations :)


Test in error
-------------

Looking at the same setup as the previous example, we can modify the test to fail in order to examine
what a failure response would look like. We'll change ``test_nginx.py`` to instead expect 1 replica, when
it will actually have three.

.. code-block:: python
   :caption: test_nginx.py
   :emphasize-lines: 19

    import pytest


    @pytest.mark.applymanifests('configs', files=[
        'nginx.yaml'
    ])
    def test_nginx(kube):
        """An example test against an Nginx deployment."""

        # wait for the manifests loaded by the 'applymanifests' marker
        # to be ready on the cluster
        kube.wait_for_registered(timeout=30)

        deployments = kube.get_deployments()
        nginx_deploy = deployments.get('nginx-deployment')
        assert nginx_deploy is not None

        pods = nginx_deploy.get_pods()
        assert len(pods) == 1, 'nginx should deploy with three replicas'

        for pod in pods:
            containers = pod.get_containers()
            assert len(containers) == 1, 'nginx pod should have one container'

            resp = pod.http_proxy_get('/')
            assert '<h1>Welcome to nginx!</h1>' in resp


Now, when we run the tests, we should expect to see an error.

.. code-block:: console

    $ pytest -s .
    =================================== test session starts ===================================
    platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
    kubetest config file: default
    rootdir: /Users/edaniszewski/dev/examples, inifile:
    plugins: kubetest-0.0.1
    collected 1 item

    test_nginx.py F

    ======================================== FAILURES =========================================
    _______________________________________ test_nginx ________________________________________

    kube = <kubetest.client.TestClient object at 0x105d7cdd8>

        @pytest.mark.applymanifests('configs', files=[
            'nginx.yaml'
        ])
        def test_nginx(kube):
            """An example test against an Nginx deployment."""

            # wait for the manifests loaded by the 'applymanifests' marker
            # to be ready on the cluster
            kube.wait_for_registered(timeout=30)

            deployments = kube.get_deployments()
            nginx_deploy = deployments.get('nginx-deployment')
            assert nginx_deploy is not None

            pods = nginx_deploy.get_pods()
    >       assert len(pods) == 1, 'nginx should deploy with three replicas'
    E       AssertionError: nginx should deploy with three replicas
    E       assert 3 == 1
    E        +  where 3 = len([{'api_version': None,\n 'kind': None,\n 'metadata': {'annotations': None,\n
                'cluster_name': None,\n         ...ort',\n            'reason': None,\n
                'start_time': datetime.datetime(2018, 9, 28, 22, 9, 2, tzinfo=tzutc())}}])

    examples/test_nginx.py:20: AssertionError
    ================================= 1 failed in 4.36 seconds ================================
    ERROR: InvocationError: 'pytest -s .'
    _________________________________________ summary _________________________________________
    ERROR:   examples: commands failed


In this case, the error message isn't too bad, but if we wanted more context, we could
run tests with kubetest at log level "info" (or, for lots of context at log level "debug".
Debug output is omitted here for brevity).

.. code-block:: console

    $ pytest -s . --kube-log-level=info
    ================================================================= test session starts =================================================================
    platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
    kubetest config file: default
    rootdir: /Users/edaniszewski/dev/examples, inifile:
    plugins: kubetest-0.0.1
    collected 1 item

    test_nginx.py F

    ====================================================================== FAILURES =======================================================================
    _____________________________________________________________________ test_nginx ______________________________________________________________________

    kube = <kubetest.client.TestClient object at 0x103e012e8>

        @pytest.mark.applymanifests('configs', files=[
            'nginx.yaml'
        ])
        def test_nginx(kube):
            """An example test against an Nginx deployment."""

            # wait for the manifests loaded by the 'applymanifests' marker
            # to be ready on the cluster
            kube.wait_for_registered(timeout=30)

            deployments = kube.get_deployments()
            nginx_deploy = deployments.get('nginx-deployment')
            assert nginx_deploy is not None

            pods = nginx_deploy.get_pods()
    >       assert len(pods) == 1, 'nginx should deploy with three replicas'
    E       AssertionError: nginx should deploy with three replicas
    E       assert 3 == 1
    E        +  where 3 = len([{'api_version': None,\n 'kind': None,\n 'metadata': {'annotations': None,\n              'cluster_name': None,\n         ...t',\n
                 'reason': None,\n            'start_time': datetime.datetime(2018, 9, 28, 22, 10, 21, tzinfo=tzutc())}}])

    examples/test_nginx.py:20: AssertionError
    ----------------------------------------------------------------- Captured log setup ------------------------------------------------------------------
    manager.py                 308 INFO     creating test meta for examples/test_nginx.py::test_nginx
    namespace.py                61 INFO     creating namespace "kubetest-test-nginx-1538172620"
    deployment.py               48 INFO     creating deployment "nginx-deployment" in namespace "kubetest-test-nginx-1538172620"
    utils.py                    90 INFO     waiting for condition: <Condition (name: wait for <class 'kubetest.objects.deployment.Deployment'>:nginx-deployment to be created, met: False)>
    utils.py                   121 INFO     wait completed (total=0.063870) <Condition (name: wait for <class 'kubetest.objects.deployment.Deployment'>:nginx-deployment to be created, met: True)>
    ------------------------------------------------------------------ Captured log call ------------------------------------------------------------------
    utils.py                    90 INFO     waiting for condition: <Condition (name: wait for pre-registered objects to be ready, met: False)>
    utils.py                   121 INFO     wait completed (total=2.169333) <Condition (name: wait for pre-registered objects to be ready, met: True)>
    deployment.py              131 INFO     getting pods for deployment "nginx-deployment"
    ---------------------------------------------------------------- Captured log teardown ----------------------------------------------------------------
    namespace.py                79 INFO     deleting namespace "kubetest-test-nginx-1538172620"
    ============================================================== 1 failed in 5.07 seconds ===============================================================
    ERROR: InvocationError: 'pytest -s . --kube-log-level=info'
    _______________________________________________________________________ summary _______________________________________________________________________
    ERROR:   examples: commands failed


Container logs on test error
----------------------------

In the above example, you got to see different log output that kubetest could provide. In
addition to logging out the actions that kubetest performs (and at the "debug" level, the
Kubernetes objects themselves), kubetest can also get logs out of the running contianers
for the test.

The caveat here is that it will only get logs for containers that are running. In the example
above, we don't see any of the container logs because the failure occurred before the containers
were fully up. If we introduce an error later on, like changing the ``<h1>`` tags in the expected
nginx response to ``<h2>``, the test should fail while some containers are up, so the error
output should contain some of the container logs. Below is a snippet of what that would look like.

.. code-block:: console

    ---------------------------------------- Captured kubernetes container logs call ----------------------------------------
    ======================================================================================
    === examples/test_nginx.py::test_nginx -> nginx-deployment-75675f5897-9fp8n::nginx ===
    ======================================================================================
    10.60.58.1 - - [28/Sep/2018:22:20:09 +0000] "GET /foobar HTTP/1.1" 404 168 "-" "Swagger-Codegen/7.0.0/python" "68.162.240.6"
    2018/09/28 22:20:09 [error] 6#0: *1 open() "/usr/share/nginx/html/foobar" failed (2: No such file or directory), client: 10.60.58.1,
    server: localhost, request: "GET /foobar HTTP/1.1", host: "35.232.2.153"
