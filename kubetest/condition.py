"""Test conditions for kubetest."""


class Condition:
    """A Condition is a convenience wrapper around a function and its arguments
    which allows the function to be called at a later time.

    The function is called in the `check` method, which resolves the result to
    a boolean value, thus the condition function should return a boolean or
    something that ultimately resolves to a Truthy or Falsey value.

    Args:
        fn: The condition function that will be checked.
        *args: Any arguments for the condition function.
        **kwargs: Any keyword arguments for the condition function.
    """

    def __init__(self, fn, *args, **kwargs):
        if not callable(fn):
            raise ValueError('The Condition function must be callable')

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def check(self):
        """Check that the condition was met.

        Returns:
            bool: True if the condition was met; False otherwise.
        """
        return bool(self.fn(*self.args, **self.kwargs))


def check_all(*args):
    """Check all the given Conditions.

    Args:
        *args (Condition): The Conditions to check.

    Returns:
        bool: True if all checks pass; False otherwise.
    """
    return all([cond.check() for cond in args])
