

class KubetestError(Exception):
    """Base class for all kubetest exceptions."""


class SetupError(KubetestError):
    """Failed to perform test setup actions."""
