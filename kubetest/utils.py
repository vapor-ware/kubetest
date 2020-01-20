"""Utility functions for kubetest."""

import logging
import time
from typing import Dict, Mapping, Union

from kubernetes.client.rest import ApiException

from kubetest.condition import Condition

log = logging.getLogger('kubetest')


def new_namespace(test_name: str) -> str:
    """Create a new namespace for the given test name.

    Kubernetes namespace names follow a DNS-1123 label that consists of lower case
    alphanumeric characters or '-' and must start with an alphanumeric.

    The test name and current timestamp are formatted to comply to this spec and
    appended to the 'kubetest' prefix.

    Args:
        test_name: The name of the test case for the namespace.

    Returns:
        The namespace name.
    """
    prefix = 'kubetest'
    timestamp = str(int(time.time()))
    test_name = test_name.replace('_', '-').lower()
    test_name = test_name.replace('[', '-')
    test_name = test_name.replace(']', '-')

    # The length of a resource name in Kubernetes may not exceed 63
    # characters. Check the length of all components (+2 for the dashes
    # joining the components). If the total length exceeds 63, truncate
    # the test name.
    name_len = len(prefix) + len(timestamp) + len(test_name) + 2

    if name_len > 63:
        test_name = test_name[:-(name_len-63)]

    return '-'.join((prefix, test_name, timestamp))


def selector_string(selectors: Mapping[str, str]) -> str:
    """Create a selector string from the given dictionary of selectors.

    Args:
        selectors: The selectors to stringify.

    Returns:
        The selector string for the given dictionary.
    """
    return ','.join([f'{k}={v}' for k, v in selectors.items()])


def selector_kwargs(
        fields: Mapping[str, str] = None,
        labels: Mapping[str, str] = None,
) -> Dict[str, str]:
    """Create a dictionary of kwargs for Kubernetes object selectors.

    Args:
        fields: A mapping of fields used to restrict the returned collection of
            Objects to only those which match these field selectors. By default,
            no restricting is done.
        labels: A mapping of labels used to restrict the returned collection of
            Objects to only those which match these label selectors. By default,
            no restricting is done.

    Returns:
        A dictionary that can be used as kwargs for many Kubernetes API calls for
        label and field selectors.
    """
    kwargs = {}
    if fields is not None:
        kwargs['field_selector'] = selector_string(fields)
    if labels is not None:
        kwargs['label_selector'] = selector_string(labels)

    return kwargs


def wait_for_condition(
        condition: Condition,
        timeout: int = None,
        interval: Union[int, float] = 1,
        fail_on_api_error: bool = True,
) -> None:
    """Wait for a condition to be met.

    Args:
        condition: The Condition to wait for.
        timeout: The maximum time to wait, in seconds, for the condition to be met.
            If unspecified, this function will wait indefinitely. If specified and
            the timeout is met or exceeded, a TimeoutError will be raised.
        interval: The time, in seconds, to wait before re-checking the condition.
        fail_on_api_error: Fail the condition checks if a Kubernetes API error is
            incurred. An API error can be raised for a number of reasons, including
            a Pod being restarted and temporarily unavailable. Disabling this will
            cause those errors to be ignored, allowing the check to continue until
            timeout or resolution. (default: True).

    Raises:
        TimeoutError: The specified timeout was exceeded.
    """
    log.info(f'waiting for condition: {condition}')

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
                f'timed out ({timeout}s) while waiting for condition {condition}'
            )

        # check if the condition is met and break out if it is
        try:
            if condition.check():
                break
        except ApiException as e:
            log.warning(f'got api exception while waiting: {e}')
            if fail_on_api_error:
                raise

        # if the condition is not met, sleep for the interval
        # to re-check later
        time.sleep(interval)

    end = time.time()
    log.info(f'wait completed (total={end-start}s) {condition}')
