
https://github.com/vapor-ware/kubetest/issues/88

### Summary

There was an assumption that a deployment and its pods have the same labels, which
may not be true. This assumption caused an exception to be raised when it was not
the case, and would prevent a deployment from getting its pods.

#### Expectations

The test should pass.
