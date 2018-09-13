"""Utility functions for kubetest."""

import datetime


def new_namespace(test_name):
    """Create a new namespace for the given test name.

    Kubernetes namespace names follow a DNS-1123 label that consists
    of lower case alphanumeric characters or '-' and must start with
    an alphanumeric.

    The test name and current timestamp are formatted to comply to
    this spec and appended to the 'kubetest' prefix.

    Args:
        test_name (str): The name of the test case for the namespace.

    Returns:
        str: The namespace name.
    """
    return 'kubetest-{}-{}'.format(
        test_name.replace('_', '-').lower(),
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
    )
