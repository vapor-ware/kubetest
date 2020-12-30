
https://github.com/vapor-ware/kubetest/issues/90

### Summary

Loading from pytest marker was failing and giving an unclear error message. The result
ended up being that it was attempting to load a ServiceAccount, which is not supported.


#### Expectations

The test should fail, with an error message clearly noting that the ServiceAccount is not
supported.
