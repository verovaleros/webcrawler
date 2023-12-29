import requests
from requests.models import Response
from requests.auth import HTTPBasicAuth

def fetch_website(req_session, url, username=None, password=None):
    """
    Connects to a website and retrieves its content.

    :param url: URL of the website to connect to.
    :param username: Optional username for basic authentication.
    :param password: Optional password for basic authentication.
    :return: A dictionary containing the response content, status code, and any redirection URL.
    """
    try:
        # Basic authentication if username and password are provided
        auth = HTTPBasicAuth(username, password) if username and password else None

        # Making a GET request to the website
        response = req_session.get(url, auth=auth, allow_redirects=False, timeout=5) # 5 seconds timeout

        return response
    except requests.RequestException as e:
        # Catching any request-related errors
        return Response()
