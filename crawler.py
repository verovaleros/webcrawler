"""
Web Crawler Security Tool v2.0.0

A simple Python web crawler that can follow links and
obtain all the structure of a website, including files.
"""
# pylint: disable=line-too-long

import os
import re
import pickle
import logging
from collections import deque
from urllib.parse import urlparse
import requests
from requests.exceptions import ConnectionError
from lib.fetch_website import fetch_website
from lib.parse_website import find_all_links
from lib.utils import store_set_to_file
from lib.utils import load_set_from_file
from lib.utils import load_queue_from_file
from lib.utils import add_url_to_set
from lib.utils import add_url_to_queue
from lib.utils import create_parser


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
    urls_seen = set()

    total_content_size = 0

    # Parse the URL to get the base url and scheme
    # which will be used to store data and reconstruct
    # relative URLs found in the HTML content.
    base_url = urlparse(args.url).netloc
    base_scheme = urlparse(args.url).scheme

    setup_logging(args.verbose, args.debug, base_url)

    # Check if the session needs to be resumed or else start from scratch
    if args.resume:
        urls_parsed = load_set_from_file(f"logs/{base_url}_urls_parsed.log", urls_seen)
        urls_failed = load_set_from_file(f"logs/{base_url}_urls_failed.log", urls_seen)
        urls_extern = load_set_from_file(f"logs/{base_url}_urls_extern.log", urls_seen)
        urls_errors = load_set_from_file(f"logs/{base_url}_urls_errors.log", urls_seen)
        urls_files = load_set_from_file(f"logs/{base_url}_urls_files.log", urls_seen)
        urls_queued = load_queue_from_file(f"logs/{base_url}_urls_queued.log", urls_seen)
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
        add_url_to_queue(args.url, urls_queued, urls_seen)
        logging.info('Web crawling starting on base URL %s (%s)', args.url, base_url)


    # Limit the URLs processed according to the input limit
    while len(urls_parsed) <= args.crawl_limit and len(urls_queued) > 0:
        # Create one session to run all the HTTP requests through it
        with requests.Session() as session:
            try:
                # Breadth-first search
                current_url = urls_queued.popleft()
                add_url_to_set(current_url, urls_seen)

                # Default size if there's no content
                content_size_kb = 0

                try:
                    # Crawl URL
                    response = fetch_website(session, current_url, args.username, args.password)
                except ConnectionError:
                    add_url_to_queue(current_url, urls_queued, urls_seen)
                    logging.error('Error fetching the website. Connectivity issues. Stopping. Resume with --resume')
                    break

                if not response or not response.ok:
                    # If response is not ok, mark URL as failed
                    add_url_to_set(current_url, urls_failed)
                    continue

                # Depending on the response status, store the URL in the correct set.
                # We are here if response is ok
                add_url_to_set(current_url, urls_parsed)

                try:
                    total_content_size += len(response.content)
                    content_size_kb = len(response.content) / 1024
                except:
                    # If we cannot calculate the size, do nothing.
                    pass

                logging.info('CRAWLED - %s - %s - %.2f Kb', current_url, response.status_code, content_size_kb)

                if response.headers.get('Location', None) is not None:
                    redirection_url = response.headers.get('Location', None)
                    if redirection_url not in urls_seen:
                        add_url_to_queue(redirection_url, urls_queued, urls_seen)
                        continue

                # Only parse the HTML responses, ignore the rest.
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    add_url_to_set(current_url, urls_files)
                    logging.debug('FILES - %s', current_url)
                    continue

                # Parse the response content to find all outlinks from the HTML reponse
                try:
                    found_urls = find_all_links(response.content, base_scheme, base_url)
                    logging.debug('Found %i new URLs', len(found_urls))
                except Exception as err:
                    logging.error('Exception found in find_all_links(): %s', err)
                    continue

                for new_url in found_urls:
                    # Only process those URLs that have not been parsed
                    if new_url not in urls_seen:
                        found_base_url = urlparse(new_url).netloc
                        if base_url in found_base_url:
                            add_url_to_queue(new_url, urls_queued, urls_seen)
                            logging.debug('FETCHED - %s', new_url)
                            continue

                        # Other links are external
                        add_url_to_set(new_url, urls_extern)
                        logging.debug('EXTERNAL - %s', new_url)

            except KeyboardInterrupt:
                add_url_to_queue(current_url, urls_queued, urls_seen)
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
    try:
        main()
    except FileNotFoundError:
        logging.error('No session to resume from. Exiting.')
    except pickle.UnpicklingError:
        logging.error('Session cannot be restored. Pickle file seems corrupt.')
