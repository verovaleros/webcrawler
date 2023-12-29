import argparse
import os
import re
import logging


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

    logging.basicConfig(filename=log_filename, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=level)
    logging.info('Web crawler starting for %s', url)


def main():
    """
    Main function for the crawler program. Parses command line arguments and starts the crawling process.
    """
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose, args.debug, args.url)
    logging.debug('Debug mode is on')
    # Further implementation goes here


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
    parser.add_argument('-L', '--common-log-format', action='store_true', help='Generate log of the requests in CLF')
    parser.add_argument('-e', '--export-file-list', action='store_true', help='Creates a file with all the URLs to found files during crawling')
    parser.add_argument('-l', '--crawl-limit', type=int, help='Maximum links to crawl')
    parser.add_argument('-C', '--crawl-depth', type=int, help='Limit the crawling depth according to the value specified')
    parser.add_argument('-d', '--download-file', type=str, help='Specify the file type of the files to download')
    parser.add_argument('-i', '--interactive-download', action='store_true', help='Before downloading files allow user to specify manually the type of files to download')
    parser.add_argument('-U', '--usuario', type=str, help='User name for authentication')
    parser.add_argument('-P', '--password', type=str, help='Request password for authentication')
    return parser

if __name__ == "__main__":
    main()
