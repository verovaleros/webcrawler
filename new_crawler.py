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
from lib.fetch_website import fetch_website


def create_parser():
    """
    Creates and returns the argparse parser with all the defined command line options.
    """
    parser = argparse.ArgumentParser(description="Crawler program for extracting data from websites.")
    parser.add_argument('-V', '--version', action='version', version='Crawler 1.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
    parser.add_argument('-D', '--debug', action='store_true', help='Debug')
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
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for logging to stdout
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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

    setup_logging(args.verbose, args.debug, args.url)
    logging.debug('Debug mode is on')

    # Process the root URL
    urls_queued.append(args.url)
    logging.info('Web crawling starting on base URL %s', args.url)


    # Limit the URLs processed according to the input limit
    while len(urls_parsed) <= args.crawl_limit and len(urls_queued) > 0:
        with requests.Session() as session:

            current_url = urls_queued.popleft()

            response = fetch_website(session, current_url, args.username, args.password)

            logging.info('CRAWLED - %s - %s - %.2f Kb', current_url, response.status_code, len(response.content)/1024)

            # Parse the response status codes
            if response.ok:
                urls_parsed.add(current_url)
                if response.headers.get('Location', None) is not None:
                    urls_queued.append(response.headers.get('Location', None))
            else:
                urls_failed.add(current_url)

            # Parse the response content

    # Log summary of the results
    logging.info('SUMMARY - Crawled: %i, Queued: %i, Failed: %i ',
                 len(urls_parsed),
                 len(urls_queued),
                 len(urls_failed)
                 )

if __name__ == "__main__":
    main()
