"""
Web Crawler Security Tool v2.0.0

A simple Python web crawler that can follow links and
obtain all the structure of a website, including files.
"""
# pylint: disable=line-too-long

import argparse
import os
import re
import logging
import requests
from collections import deque
from urllib.parse import urlparse
from lib.fetch_website import fetch_website
from lib.parse_website import find_all_links
from lib.utils import store_set_to_file
from lib.utils import load_set_from_file
from lib.utils import load_queue_from_file
from lib.utils import add_url_to_set
from lib.utils import add_url_to_queue


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


def setup_logging(verbose, debug, url):
    """
    Set up the logging configuration. Verbose and debug flags adjust the logging level.
    URL is used to create a unique log file for each URL.
    """
    log_directory = "logs"
    level = logging.DEBUG if debug else (logging.INFO if verbose or not debug and not verbose else logging.WARNING)

    # Replace non-alphanumeric characters with underscore
    sanitized_url = re.sub(r'[^\w\-_\. ]', '_', url)
    # Create the logs directory if it doesn't exist
    os.makedirs(log_directory, exist_ok=True)
    log_filename = f"{log_directory}/{sanitized_url}.log"

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # File handler for logging to a file
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_formatter = logging.Formatter('%(asctime)s.%(msecs)05d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for logging to stdout
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s.%(msecs)05d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

def main():
    """
    Main function for the crawler program. Parses command line arguments and starts the crawling process.
    """
    parser = create_parser()
    args = parser.parse_args()

    urls_parsed = set()
    urls_queued = deque()
    urls_failed = set()
    urls_extern = set()
    urls_errors = set()
    urls_files = set()

    total_content_size = 0

    # Parse the URL to get the base url and scheme
    # which will be used to store data and reconstruct
    # relative URLs found in the HTML content.
    base_url = urlparse(args.url).netloc
    base_scheme = urlparse(args.url).scheme

    setup_logging(args.verbose, args.debug, base_url)

    # Check if the session needs to be resumed or else start from scratch
    if args.resume:
        urls_parsed = load_set_from_file(f"logs/{base_url}_urls_parsed.log")
        urls_failed = load_set_from_file(f"logs/{base_url}_urls_failed.log")
        urls_extern = load_set_from_file(f"logs/{base_url}_urls_extern.log")
        urls_errors = load_set_from_file(f"logs/{base_url}_urls_errors.log")
        urls_files = load_set_from_file(f"logs/{base_url}_urls_files.log")
        urls_queued = load_queue_from_file(f"logs/{base_url}_urls_queued.log")
        logging.info('Resuming web crawling session: Crawled: %i, Queued: %i, Failed: %i, Files: %i, External: %i, Errors: %i',
                     len(urls_parsed),
                     len(urls_queued),
                     len(urls_failed),
                     len(urls_files),
                     len(urls_extern),
                     len(urls_errors)
                     )
    else:
        # Process the root URL
        add_url_to_queue(args.url, urls_queued)
        logging.info('Web crawling starting on base URL %s (%s)', args.url, base_url)


    # Limit the URLs processed according to the input limit
    while len(urls_parsed) <= args.crawl_limit and len(urls_queued) > 0:
        # Create one session to run all the HTTP requests through it
        with requests.Session() as session:
            try:
                current_url = urls_queued.popleft()

                response = fetch_website(session, current_url, args.username, args.password)

                # Attempt to calculate the content size
                if response and response.content:
                    total_content_size += len(response.content)
                    content_size_kb = len(response.content) / 1024
                else:
                    content_size_kb = 0  # Default size if there's no content

                logging.info('CRAWLED - %s - %s - %.2f Kb', current_url, response.status_code, len(response.content)/1024)

                # Depending on the response status,
                # store the URL in the correct set.
                if response.ok:
                    urls_parsed.add(current_url)
                    if response.headers.get('Location', None) is not None:
                        redirection = response.headers.get('Location', None)
                        if redirection not in urls_parsed and redirection not in urls_queued:
                            add_url_to_queue(response.headers.get('Location', None), urls_queued)
                else:
                    add_url_to_set(current_url, urls_failed)

                # Parse the response content to find
                # all outlinks from the HTML reponse
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type:
                    found_urls = find_all_links(response.content, base_scheme, base_url)
                    logging.debug('Found %i new URLs', len(found_urls))

                    for new_url in found_urls:
                        if new_url not in urls_parsed:
                            found_base_url = urlparse(new_url).netloc
                            if base_url in found_base_url and new_url not in urls_queued:
                                add_url_to_queue(new_url, urls_queued)
                                logging.debug('FETCHED - %s', new_url)
                            if base_url not in found_base_url and new_url not in urls_extern:
                                add_url_to_set(new_url, urls_extern)
                                logging.debug('EXTERNAL - %s', new_url)
                elif current_url not in urls_files:
                    add_url_to_set(current_url, urls_files)
                    logging.debug('FILES - %s', new_url)
            except KeyboardInterrupt:
                add_url_to_queue(current_url, urls_queued)
                break
            except Exception as err:
                logging.error('Error processing URL: %s (%s)', current_url, err)
                urls_errors.add(current_url)
                continue


    # Log summary of the results
    logging.info('SUMMARY - Crawled: %i, Queued: %i, Failed: %i, Files: %i, External: %i, Errors: %i, Total downloaded: %.2f Kb',
                 len(urls_parsed),
                 len(urls_queued),
                 len(urls_failed),
                 len(urls_files),
                 len(urls_extern),
                 len(urls_errors),
                 total_content_size/1024
                 )

    # Store sets to disk
    store_set_to_file(urls_queued, 'logs', f'{base_url}_urls_queued')
    store_set_to_file(urls_parsed, 'logs', f'{base_url}_urls_parsed')
    store_set_to_file(urls_failed, 'logs', f'{base_url}_urls_failed')
    store_set_to_file(urls_errors, 'logs', f'{base_url}_urls_errors')
    store_set_to_file(urls_extern, 'logs', f'{base_url}_urls_extern')
    store_set_to_file(urls_files, 'logs', f'{base_url}_urls_files')


if __name__ == "__main__":
    main()
