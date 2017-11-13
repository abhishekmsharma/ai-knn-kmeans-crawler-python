**About Program**
==================================
The program scrapes through the pages of Indeed, IEEE Job Search, and ACM Job Search and displays the most relevant jobs
based on the keywords provided.\
It also performas K-Means clustering on the obtained results.\
The job results and clustering results are displayed as a HTML output.

**Setting up Python environment:**
==================================

The program uses a 3rd party library known as beautifulsoup4. Run the below command to install.\
pip install beautifulsoup4

**How to run:**
===============
Kindly execute the program using the following steps:\
\
1\. Open terminal and navigate to the path containing the 3 Python (.py)
files mentioned in the previous section.\
\
2\. Execute the following command:\
**python job\_search\_cli.py -keywords \<keywords\> -k
\<value\_of\_k\>**\
\
*-keywords: Specifies the keywords for job search, separate each keyword
by a space.\
-k: Specifies the value of k*\
\
Example commands: **python job\_search\_cli.py -keywords python
"machine learning" -k 3**\
\
**python job\_search\_cli.py -keywords sql san jose -k 3**\
\
You may also run the following command to get more information about the
command line arguments:\
*python job\_search\_cli.py --help*\
\
**Note:** After displaying the results, the program gives option to do a
new search, repeat the search, cluster the previous search, or exit.
Kindly choose the desired option accordingly.\
