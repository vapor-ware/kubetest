"""Response wrapper object for proxied requests to Kubernetes resources."""

import json


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
        # the response data comes back as a string formatted as a python
        # dictionary might be, where the inner quotes are single quotes
        # (') instead of the double quotes (") expected by JSON standard.
        # to remedy this, we just replace single quotes with double quotes.
        data = self.data.replace("'", '"')
        return json.loads(data)
