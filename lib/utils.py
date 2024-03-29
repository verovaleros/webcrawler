"""
Set of common util functions to supopr the
functionality of the web crawler
"""
import pickle
import argparse
from collections import deque
from urllib.parse import urlparse


def create_parser():
    """
    Creates and returns the argparse parser with all the defined command line options.
    """
    parser = argparse.ArgumentParser(description="Crawler program for extracting data from websites.")
    parser.add_argument('-V', '--version', action='version', version='Crawler 1.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
    parser.add_argument('-D', '--debug', action='store_true', help='Debug')
    parser.add_argument('-r', '--resume', action='store_true', help='Resume existing crawling session')
    parser.add_argument('-u', '--url', required=True, type=str, help='URL to start crawling')
    parser.add_argument('-w', '--write', action='store_true', help='Save crawl output to a local file')
    parser.add_argument('-L', '--common-log-format', default=False, action='store_true', help='Generate log of the requests in CLF')
    parser.add_argument('-e', '--export-file-list', default=False, action='store_true', help='Creates a file with all the URLs to found files during crawling')
    parser.add_argument('-l', '--crawl-limit', type=int, default=float('inf'), help='Maximum links to crawl')
    parser.add_argument('-C', '--crawl-depth', type=int, default=float('inf'), help='Limit the crawling depth according to the value specified')
    parser.add_argument('-d', '--download-file', type=str, default=False, help='Specify the file type of the files to download')
    parser.add_argument('-i', '--interactive-download', default=False, action='store_true', help='Before downloading files allow user to specify manually the type of files to download')
    parser.add_argument('-U', '--username', type=str, help='User name for authentication')
    parser.add_argument('-P', '--password', type=str, help='Request password for authentication')
    return parser


def is_valid_url(url):
    """
    Validates if the given URL has a valid format.

    :param url: URL to validate.
    :return: True if the URL is valid, False otherwise.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def add_url_to_queue(url, url_queue, url_seen_set):
    """
    Adds a URL to the queue after validating and normalizing it, and ensuring it's not a duplicate.

    :param url: URL to add.
    :param url_queue: Queue (deque) to add the URL to.
    """
    url = url.strip().lower()
    if is_valid_url(url):
        url_seen_set.add(url)
        url_queue.append(url)


def add_url_to_set(url, url_set):
    """
    Adds a URL to the set after validating and normalizing it.

    :param url: URL to add.
    :param url_set: Set to add the URL to.
    """
    url = url.strip().lower()
    if is_valid_url(url) and url not in url_set:
        url_set.add(url)


def store_set_to_file(set_to_save_to_disk, output_directory, file_name):
    """
    Writes the contents of a set to a file, with each element on a new line.

    :param set_to_save_to_disk: The set whose contents need to be written to the file.
    :param output_dir: The directory to store the files.
    :param file_name: The name of the file to write to.
    """

    output_filename = f"{output_directory}/{file_name}.log"
    with open(output_filename, "wb") as file:
        pickle.dump(set_to_save_to_disk, file)


def load_set_from_file(file_name, urls_seen_set):
    """
    Loads the contents of a file into a set.

    :param file_name: The name of the file to read from.
    :return: A set containing the lines of the file.
    """
    loaded_set = set()
    try:
        with open(file_name, "rb") as file:
            loaded_set = pickle.load(file)
    except FileNotFoundError:
        raise
    except pickle.UnpicklingError:
        raise

    urls_seen_set.update(loaded_set)
    return loaded_set


def load_queue_from_file(file_name, urls_seen_set):
    """
    Loads the contents of a file into a deque (queue).

    :param file_name: The name of the file to read from.
    :return: A deque containing the lines of the file.
    """
    loaded_queue = deque()
    try:
        with open(file_name, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return deque()  # Return an empty deque in case of an unpickling error
    except pickle.UnpicklingError:
        print(f"Error loading the queue from {file_name}. File may be corrupted.")
        return deque()  # Return an empty deque in case of an unpickling error

    for url in loaded_queue:
        urls_seen_set.add(url)
    return loaded_queue
