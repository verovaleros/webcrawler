from urllib.parse import urljoin
from bs4 import BeautifulSoup

def find_all_links(html_content, base_schema, base_url):
    """
    Parses HTML content to find all links, reconstructs full URLs for relative links,
    and returns a set of these URLs.

    :param html_content: The HTML content as a string.
    :param base_schema: The base schema (e.g., 'http', 'https') for forming URLs.
    :param base_url: The base URL to resolve relative URLs against.
    :return: A set of full-path URLs.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    urls = set()
    base_full_url = f"{base_schema}://{base_url}"

    for tag in soup.find_all('a', href=True):  # Find all <a> tags with an href attribute
        href = tag['href']
        # Check if the href is a relative URL
        if not href.startswith(('http://', 'https://', 'ftp://')):
            href = urljoin(base_full_url, href)  # Convert relative URL to absolute
        urls.add(href)

    return urls
