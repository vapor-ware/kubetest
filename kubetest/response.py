"""Response wrapper object for proxied requests to Kubernetes resources."""

import json

import urllib3


class Response:
    """Response is a wrapper around the Kubernetes API's response data
    when a request is proxied to a Kubernetes resource, like a Pod or
    Service.

    A proxied request will return:
    - The response data
    - The response headers
    - The response HTTP code

    All of these are wrapped by this class. Additional helpers are provided,
    such as casting the response data to JSON.

    Args:
        data: The response data from the proxied request.
        status: The response status code.
        headers: The response headers.
    """

    def __init__(self, data, status, headers):
        self.data = data
        self.status = status
        self.headers = headers

    def json(self):
        """Convert the response data to JSON.

        If the response data is not valid JSON, an error will be raised.

        Returns:
            dict: The JSON data.
        """
        # This should generally be the case, since the primary source of Response
        # instances are the HTTP methods on Pods (e.g. http_proxy_get), where
        # `_preload_content=False`. Should that be set to True, it will not return
        # the HTTPResponse but will instead return the response data formatted as
        # the type specified in the `response_type` param.
        #
        # Note that I have found setting _preload_content to True (the default value
        # for the Kubernetes client) to be difficult to deal with from a generic interface
        # because it requires you to know the expected output ("str", "dict", ...)
        # and pass that in as a param, where that could really be abstracted away from
        # the user. For that reason, it is currently set to False -- this may change
        # in the future if desired.
        if isinstance(self.data, urllib3.HTTPResponse):
            return json.loads(self.data.data)

        # the response data comes back as a string formatted as a python
        # dictionary might be, where the inner quotes are single quotes
        # (') instead of the double quotes (") expected by JSON standard.
        # to remedy this, we just replace single quotes with double quotes.
        data = self.data.replace("'", '"')
        return json.loads(data)
