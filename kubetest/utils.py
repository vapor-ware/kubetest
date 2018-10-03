"""Utility functions for kubetest."""

import logging
import time

from kubernetes.client.rest import ApiException

log = logging.getLogger('kubetest')


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


def wait_for_condition(condition, timeout=None, interval=1, fail_on_api_error=True):
    """Wait for a condition to be met.

    Args:
        condition (condition.Condition): The Condition to wait for.
        timeout (int): The maximum time to wait, in seconds, for the
            condition to be met. If unspecified, this function will
            wait indefinitely. If specified and the timeout is met
            or exceeded, a TimeoutError will be raised.
        interval (int|float): The time, in seconds, to wait before
            re-checking the condition.
        fail_on_api_error (bool): Fail the condition checks if a Kubernetes
            API error is incurred. An API error can be raised for a number
            of reasons, including a Pod being restarted and temporarily
            unavailable. Disabling this will cause those errors to be
            ignored, allowing the check to continue until timeout or
            resolution. (default: True).

    Raises:
        TimeoutError: The specified timeout was exceeded.
    """
    log.info('waiting for condition: %s', condition)

    # define the maximum time to wait. once this is met, we should
    # stop waiting.
    max_time = None
    if timeout is not None:
        max_time = time.time() + timeout

    # start the wait block
    start = time.time()
    while True:
        if max_time and time.time() >= max_time:
            raise TimeoutError(
                'timed out ({}s) while waiting for condition {}'
                .format(timeout, condition)
            )

        # check if the condition is met and break out if it is
        try:
            if condition.check():
                break
        except ApiException as e:
            log.warning('got api exception while waiting: {}'.format(e))
            if fail_on_api_error:
                raise

        # if the condition is not met, sleep for the interval
        # to re-check later
        time.sleep(interval)

    end = time.time()
    log.info('wait completed (total=%fs) %s', end - start, condition)
