"""Utility functions for kubetest."""

import time


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
        int(time.time())
    )


def selector_string(selectors):
    """Create a selector string from the given dictionary of selectors.

    Args:
        selectors (dict): The selectors to stringify.

    Returns:
        str: The selector string for the given dictionary.
    """
    return ','.join(['{}={}'.format(k, v) for k, v in selectors.items()])


def selector_kwargs(fields=None, labels=None):
    """Create a dictionary of kwargs for Kubernetes object selectors.

    Args:
        fields (dict[str, str]): A dictionary of fields used to restrict
            the returned collection of Objects to only those which match
            these field selectors. By default, no restricting is done.
        labels (dict[str, str]): A dictionary of labels used to restrict
            the returned collection of Objects to only those which match
            these label selectors. By default, no restricting is done.

    Returns:
        dict[str, str]: A dictionary that can be used as kwargs for
            many Kubernetes API calls for label and field selectors.
    """
    kwargs = {}
    if fields is not None:
        kwargs['field_selector'] = selector_string(fields)
    if labels is not None:
        kwargs['label_selector'] = selector_string(labels)

    return kwargs
