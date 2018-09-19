"""Test conditions for kubetest."""

import datetime


class Condition:
    """A Condition is a convenience wrapper around a function and its arguments
    which allows the function to be called at a later time.

    The function is called in the `check` method, which resolves the result to
    a boolean value, thus the condition function should return a boolean or
    something that ultimately resolves to a Truthy or Falsey value.

    Args:
        name: The name of the condition to make it easier to identify.
        fn: The condition function that will be checked.
        *args: Any arguments for the condition function.
        **kwargs: Any keyword arguments for the condition function.
    """

    def __init__(self, name, fn, *args, **kwargs):
        if not callable(fn):
            raise ValueError('The Condition function must be callable')

        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        # last check holds the state of the last check.
        self.last_check = False

    def __str__(self):
        return '<Condition (name: {}, met: {})>'.format(
            self.name, self.last_check
        )

    def __repr__(self):
        return self.__str__()

    def check(self):
        """Check that the condition was met.

        Returns:
            bool: True if the condition was met; False otherwise.
        """
        self.last_check = bool(self.fn(*self.args, **self.kwargs))
        print('[{}] condition "{}" - check status: {}'.format(datetime.datetime.now(), self.name, self.last_check))
        return self.last_check


def check_all(*args):
    """Check all the given Conditions.

    Args:
        *args (Condition): The Conditions to check.

    Returns:
        bool: True if all checks pass; False otherwise.
    """
    return all([cond.check() for cond in args])
