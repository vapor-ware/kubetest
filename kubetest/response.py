"""Response wrapper object for proxied requests to Kubernetes resources."""

import ast
import json
import logging
from typing import Any, Dict

import urllib3

log = logging.getLogger('kubetest')


class Response:
    """Response is a wrapper around the Kubernetes API's response data when a
    request is proxied to a Kubernetes resource, like a Pod or Service.

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

    def json(self) -> Dict[str, Any]:
        """Convert the response data to JSON.

        If the response data is not valid JSON, an error will be raised.

        Returns:
            The JSON data loaded into a Python dictionary.
        """
        # This should generally be the case, since the primary source of Response
        # instances are the HTTP methods on Pods (e.g. http_proxy_get), where
        # `_preload_content=False`. Should that be set to True, it will not return
        # the HTTPResponse but will instead return the response data formatted as
        # the type specified in the `response_type` param. By default, kubetest sets
        # the _preload_content field to True, so this should generally not be hit.
        if isinstance(self.data, urllib3.HTTPResponse):
            return json.loads(self.data.data)

        # The response data comes back as a string. This could be a JSON string,
        # or something else (text body, error string, etc). Since we've preloaded
        # the content as a string (see comment above), we can not simply load the
        # string as JSON as the preloading essentially serializes the Python dict
        # out to a string, so various values will not parse into JSON (None vs null,
        # " vs ', etc). To remedy this, we attempt to load the response as an ast
        # literal - if it fails for any reason, fall back to trying to load JSON.
        # At the very least the JSON loading will fail with a familiar error which
        # one would expect from a .json() function.
        try:
            data = ast.literal_eval(self.data)
        except Exception as e:
            log.debug(f'failed literal eval of data {self.data} ({e})')
            data = json.loads(self.data)

        return data
