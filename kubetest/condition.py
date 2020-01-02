"""Define test conditions for kubetest."""

import enum
from typing import Callable, List, Tuple


class Policy(enum.Enum):
    """Condition checking policies.

    A Policy defines the behavior of how Conditions are checked.

      - **ONCE**: A condition only needs to be met once and the check will
        consider it met regardless of the state of any other conditions that
        may be checked alongside it. This is the default behavior.
      - **SIMULTANEOUS**: A condition needs to be met simultaneous to all other
        conditions that are being checked alongside it for the check to be
        successful.
    """

    ONCE = 1
    SIMULTANEOUS = 2


class Condition:
    """A Condition is a convenience wrapper around a function and its arguments
    which allows the function to be called at a later time.

    The function is called in the ``check`` method, which resolves the result to
    a boolean value, thus the condition function should return a boolean or
    something that ultimately resolves to a Truthy or Falsey value.

    Args:
        name: The name of the condition to make it easier to identify.
        fn: The condition function that will be checked.
        *args: Any arguments for the condition function.
        **kwargs: Any keyword arguments for the condition function.

    Attributes:
        name (str): The name of the Condition.
        fn (callable): The condition function that will be checked.
        args (tuple): Arguments for the checking function.
        kwargs (dict): Keyword arguments for the checking function.
        last_check (bool): Holds the state of the last condition check.

    Raises:
        ValueError: The given ``fn`` is not callable.
    """

    def __init__(self, name: str, fn: Callable, *args, **kwargs) -> None:
        if not callable(fn):
            raise ValueError('The Condition function must be callable')

        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        # last check holds the state of the last check.
        self.last_check = False

    def __str__(self) -> str:
        return f'<Condition (name: {self.name}, met: {self.last_check})>'

    def __repr__(self) -> str:
        return self.__str__()

    def check(self) -> bool:
        """Check that the condition was met.

        Returns:
            True if the condition was met; False otherwise.
        """
        self.last_check = bool(self.fn(*self.args, **self.kwargs))
        return self.last_check


def check_all(*args: Condition) -> bool:
    """Check all the given Conditions.

    Args:
        *args: The Conditions to check.

    Returns:
        True if all checks pass; False otherwise.
    """
    return all([cond.check() for cond in args])


def check_and_sort(*args: Condition) -> Tuple[List[Condition], List[Condition]]:
    """Check all the given Conditions and sort them into 'met' and 'unmet' buckets.

    Args:
        *args: The Conditions to check.

    Returns:
        The met and unmet condition buckets (in that order).
    """
    met, unmet = [], []

    for c in args:
        if c.check():
            met.append(c)
        else:
            unmet.append(c)

    return met, unmet
