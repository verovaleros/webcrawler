import requests
from requests.auth import HTTPBasicAuth

def fetch_website(url, username=None, password=None):
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
        response = requests.get(url, auth=auth, allow_redirects=False)

        # Check if response is a redirection
        if 300 <= response.status_code < 400:
            return {
                'content': None,
                'status_code': response.status_code,
                'error': None,
                'redirect_url': response.headers.get('Location', None)
            }

        # Return the content, status code, and no redirection URL
        return {
            'content': response.content,
            'status_code': response.status_code,
            'error': None,
            'redirect_url': None
        }

    except requests.RequestException as e:
        # Catching any request-related errors
        return {
            'content': None,
            'status_code': None,
            'error': str(e),
            'redirect_url': None
        }
