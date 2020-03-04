
.. _command_line_usage:

Command Line Usage
==================

Once installed (see :ref:`installation`), the following pytest command-line options become available:

.. code-block:: none

    pytest \
        [--kube-error-log-lines <COUNT>] \
        [--suppress-insecure-request] \
        [--kube-log-level <LEVEL>] \
        [--kube-context <CONTEXT>] \
        [--kube-config <PATH>] \
        [--kube-disable] \
        [--in-cluster]



kubernetes integration test support:
  --kube-config=path    the kubernetes config for kubetest; this is required
                        for resources to be installed on the cluster
  --kube-context=context
                        the name of the kubernetes config context to use
  --kube-disable        [DEPRECATED] disable automatic configuration with the
                        kubeconfig file
  --in-cluster          use the kubernetes in-cluster config
  --kube-log-level=KUBE_LOG_LEVEL
                        log level for the kubetest logger
  --kube-error-log-lines=KUBE_ERROR_LOG_LINES
                        set the number of lines to tail from container logs on
                        error. to show all lines, set this to -1.
  --suppress-insecure-request=SUPPRESS_INSECURE_REQUEST
                        suppress the urllib3 InsecureRequestWarning. This is
                        useful if testing against a cluster without HTTPS set
                        up.


- ``--kube-config <PATH>``

    Specifies the path to the config file to use for connecting to your cluster.
    If this option is not specified, ``kubetest`` will not install resources onto
    the cluster, which may cause test failure.

- ``--kube-context <CONTEXT>``

    Specifies the context to use in the kubeconfig. If not specified, it will use
    the current context, as set in the kubeconfig.

- ``--kube-disable`` **DEPRECATED**

    .. note::
       *v0.2.0*: This flag no longer does anything. It will be removed in the next
       major release.

    Disable kubetest from running. This can be useful when running pytest when no
    backing cluster is needed (e.g. to view the registered markers via ``pytest --markers``).

- ``--kube-error-log-lines <COUNT>``

    Set the number of lines to tail from the container logs for a test namespace when
    a test fails. By default, this is set to 50. If you want to show all container logs,
    set this to -1. If you do not wish to display any container logs in the pytest
    results, set this to 0.

- ``--kube-log-level <LEVEL>``

    Sets the logging level for kubetest. The default log level is *warining*. Setting
    the log level to *info* will provide logging for kubetest actions. Setting the log
    level to *debug* will log out the Kubernetes object state for various actions as well.

- ``--in-cluster``

    Use the Kubernetes in cluster config. With this specified, you do not need to supply
    a kube-config via the ``--kube-config`` option.

- ``--suppress-insecure-request``

    Suppress the urllib3 InsecureRequestWarning. This is useful if testing against a
    cluster without HTTPS set up.
