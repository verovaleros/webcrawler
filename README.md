Web Crawler Security Tool
=========================

The Web Crawler Security Tool is a python based tool to automatically crawl a web site. It is a web crawler oriented to help in penetration testing tasks. The main task of this tool is to search and list all the links (pages and files) in a web site. 

The crawler has been completely rewritten in v1.0 bringing a lot of improvements: improved the data visualization, interactive option to download files, increased speed in crawling, exports list of found files into a separated file (useful to crawl a site once, then download files and analyse them with FOCA), generate an output log in Common Log Format (CLF), manage basic authentication and more! 

Many of the old features has been reimplemented and the most interesting one is the capability of the crawler to search for directory indexing.

Features
========
* Crawl http and https web sites (even web sites not using common ports).
* It allows to determine the depth of the crawling (-C <depth> option)
* Generates a summary at the end of the crawling with statistics about the crawl results
* Implemented HEAD method for analysing file types before crawling. This feature improves the speed of the crawler significantly.
* Uses regular expressions to find 'href', 'src' and 'content' links.
* Identifies relative links.
* Identifies non-html files and shows them.
* Not crawl non-html files.
* Identifies directory indexing.
* Crawl directories with indexing (not yet implemented in v1.0)
* Uses CTRL-C to stop current crawler stages and continue working.
* Identifies all kind of files by reading the content-type header field of the response.
* Exports (-e option) in a separated file a list of all files URLs found during crawling.
* Select type of files to download (-d option). Ex.: png,pdf,jpeg,gif or png,jpeg.
* Select in an interactive way which type of files to download (-i option).
* Save the downloaded files into a directory. It only creates the output directory if there is at least one file to download.
* Generates a output log in CLF (Common Log Format) of all the request done during crawling.
* (beta) Login with basic authentication. Feedback is welcome!
* Tries to detect if the website uses a CMS (like wordpress, joomla, etc) (not yet implemented in v1.0)
* It looks for '.bk' or '.bak' files of php, asp, aspx, jps pages. (not yet implemented in v1.0)
* It identifies and calculates the number of unique web pages crawled. (not yet implemented in v1.0)
* It identifies and calculates the number of unique web pages crawled that contains parameters in URL. (not yet implemented in v1.0)
* It works in Windows, but don't save results.


The original project was on sourceforge: http://sourceforge.net/projects/webcrawler-py.
