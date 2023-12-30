"""
Connects to a website and retrieves its content.
"""
import requests
from requests.models import Response
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError


def fetch_website(req_session, url, username=None, password=None):
    """
    Connects to a website and retrieves its content.

    :param req_session: A requests Session object.
    :param url: URL of the website to connect to.
    :param username: Optional username for basic authentication.
    :param password: Optional password for basic authentication.
    :return: A response object.
    """
    try:
        # Basic authentication if username and password are provided
        auth = HTTPBasicAuth(username, password) if username and password else None

        # Making a HEAD request to check content type
        head_response = req_session.head(url, auth=auth, allow_redirects=False, timeout=5)

        # Check if the content type is HTML
        if 'text/html' in head_response.headers.get('Content-Type', ''):
            # If it's a redirection, return the head response
            if head_response.headers.get('Location', None) is not None:
                return head_response
            else:
                # Making a GET request if content is HTML
                response = req_session.get(url, auth=auth, allow_redirects=False, timeout=5)
                return response
        else:
            # Return the HEAD response if not HTML
            return head_response

    except ConnectionError:
        # Propagate the exception if there's a connection error
        raise
    except requests.RequestException:
        # Return an empty Response object in case of error
        return Response()
