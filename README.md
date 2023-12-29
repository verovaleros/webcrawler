Web Crawler Security Tool
=========================

The Web Crawler Security Tool is a Python-based tool that automatically crawls a website. It is a web crawler oriented to help in penetration testing tasks. The main task of this tool is to search and list all the links (pages and files) in a website. The crawler has been completely rewritten in v2.0. The current version is still a work in progress, and the features shown below are still not fully ported.


Ported Features
========
* Implements a `--resume` option where you can resume a crawling activity.
* Crawl HTTP and HTTPS websites (even those not using common ports).
* It allows to determine the depth of the crawling (-C <depth> option).
* Generates a summary at the end of the crawling with statistics about the crawl results, including the number of crawled URLs, external URLs, files, errors, failed requests, and total transferred data.
* Uses CTRL-C to stop current crawler stages and save the status.
* Export the files identified in separate files and the errors and failed requests.
* Uses beautifulsoup4 for finding absolute and relative links.
  
Unported features
========
* Implemented HEAD method for analyzing file types before crawling. This feature improves the speed of the crawler significantly.
* Identifies non-html files and shows them.
* Does not crawl non-html files.
* Identifies directory indexing.
* Crawl directories with indexing (not yet implemented in v1.0)
* Identifies all kinds of files by reading the content-type header field of the response.
* Select the type of files to download (-d option). Ex.: png, pdf, jpeg, gif or png, jpeg.
* Select in an interactive way which type of files to download (-i option).
* Save the downloaded files into a directory. It only creates the output directory if at least one file is downloaded.
* Generates an output log in CLF (Common Log Format) of all the requests done during crawling.
* (beta) Login with basic authentication. Feedback is welcome!
* Tries to detect if the website uses a CMS (like WordPress, Joomla, etc) (not yet implemented in v1.0)
* It looks for '.bk' or '.bak' files of php, asp, aspx, jps pages. (not yet implemented in v1.0)
* It works in Windows but doesn't save results.


The original project was on SourceForge: http://sourceforge.net/projects/webcrawler-py.
