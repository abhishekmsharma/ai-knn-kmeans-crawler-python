'''
Developer: Abhishek Manoj Sharma
Date: September 27, 2017
Class: Agent
'''

import urllib2
from bs4 import BeautifulSoup
import csv
import shlex
from operator import itemgetter
import os
import time
import webbrowser

class Agent:

    LIMIT_OF_SEARCH_PAGES=2 #each page contains 50 jobs

    #ploading the lookup table on first run based on few selected keywords
    popular_keyword_sequences=[
        "java","sql","machine learning","technician","artificial intelligence san jose","python",
        "machine learning san jose","database management","assistant professor san jose","professor san jose",
        "python san jose", "artificial intelligence engineer", "artificial intelligence virtual reality",
        "database administrator", "java san jose"
    ]

    #checkLookupTableHistory() method is used to check if the current keyword sequence is already present in lookup table or not
    def checkLookupTableHistory(self,keywords):
        jobs_file="job_data.csv"
        mtime=0
        if os.path.isfile(jobs_file):
            mtime = os.path.getmtime(jobs_file)
            current_time =  time.time()
            #checks if the job search is more than 36 hours old or not. If yes, then reloads all the jobs.
            if (float(current_time - mtime)/3600)>36:
                print "Lookup table was created more than 36 hours ago.\nRecreating lookup table.\nThis may take up to 4-5 minutes."
                os.remove("job_data.csv")
                self.loadTables(keywords)
            else:
                keyword_sequence = self.getFormmatedKeywordSequence(keywords)
                keyword_history = set()

                with open("job_data.csv") as f:
                    readCSV = csv.reader(f, delimiter=',')
                    for row in readCSV:
                        keyword_history.add(row[5].lower())
                if keyword_sequence.lower() in keyword_history:
                    print "Keyword sequence found in lookup table"
                else:
                    self.loadTables(keywords)
        else:
            self.loadTables(keywords)

    #searchJobs() method searches for the jobs in the lookup table, and if not present, retrieves job from the Internet by calling the loadTables() method
    def searchJobs(self, keywords, k):
        if os.path.isfile("job_data.csv"):
            try:
                open("job_data.csv", "r+")
            except IOError:
                print "Please close the job_data.csv file for the program to proceed"
                return

            #checking if keyword sequence alrady present in job_data.csv
            self.checkLookupTableHistory(keywords)

            keywords = keywords.replace('"', "")
            keywords = keywords.split()
            jaccard_distances = []
            with open("job_data.csv") as f:
                readCSV = csv.reader(f, delimiter=',')
                for row in readCSV:
                    job_words = (row[0] + " " + row[1] + " " + row[2] + " " + row[3]).lower()
                    job_words = job_words.split(" ")
                    jaccard_distances.append(self.jaccardDistance(keywords,job_words))

            jobs_distances= self.calculateKNN(jaccard_distances)
            jobs_distances = sorted(jobs_distances, key=itemgetter(6))
            top_jobs = jobs_distances[:15]
            self.printHTMLTable(top_jobs,keywords,k)
            return top_jobs
        else:
            #if first run of program machine, load the lookup table with selected keywords
            print "First run of program\nNo jobs file found\nCreating file for the first time and loading data.\nThis may take up to 4-5 minutes"

            for i in range(0,len(self.popular_keyword_sequences)):
                self.loadTables(self.popular_keyword_sequences[i])
                percent_complete = "{0:.2f}".format(float(i+1)/len(self.popular_keyword_sequences)*100)
                print "-----------\n"+percent_complete+"% completed\n-----------"

            self.checkLookupTableHistory(keywords)

            keywords = keywords.replace('"', "")
            keywords = keywords.split()
            jaccard_distances = []
            with open("job_data.csv") as f:
                readCSV = csv.reader(f, delimiter=',')
                for row in readCSV:
                    job_words = (row[0] + " " + row[1] + " " + row[2] + " " + row[3]).lower()
                    job_words = job_words.split(" ")
                    jaccard_distances.append(self.jaccardDistance(keywords, job_words))

            jobs_distances = self.calculateKNN(jaccard_distances)
            jobs_distances = sorted(jobs_distances, key=itemgetter(6))
            top_jobs = jobs_distances[:15]
            self.printHTMLTable(top_jobs, keywords, k)
            return top_jobs

    #jaccardDistance() method accepts a list of words, converts them to sets and returns the Jaccard distance
    def jaccardDistance(self,keywords, job_details):
        for i in range(0, len(keywords)):
            keywords[i] = keywords[i].lower()
        for i in range(0, len(job_details)):
            job_details[i] = job_details[i].lower()
        intersection = len(set.intersection(*[set(keywords), set(job_details)]))
        union = len(set.union(*[set(keywords), set(job_details)]))
        return 1 - intersection / float(union)


    #calculateKNN() matches the calculated distances with every entry to eventually find the k nearest neighbors
    def calculateKNN(self,distances):
        jobs_distances = []
        with open("job_data.csv") as f:
            readCSV = csv.reader(f, delimiter=',')
            distance_count=0
            for row in readCSV:
                row.append(distances[distance_count])
                jobs_distances.append(row)
                distance_count+=1
        return jobs_distances

    #loadTables() method calls the methods for Indeed, ACM, and IEEE to retrieve jobs and writes them to the job_data.csv file
    def loadTables(self,keywords):
        all_jobs_indeed = self.loadIndeed(keywords)

        all_jobs_ACM = self.loadACMIEEE(keywords,"acm")

        all_jobs_IEEE = self.loadACMIEEE(keywords,"ieee")

        all_jobs = all_jobs_indeed + all_jobs_ACM + all_jobs_IEEE

        all_jobs = set(map(tuple, all_jobs))

        print "\nTotal loaded", len(all_jobs), "unique jobs from 3 sites"

        with open(r'job_data.csv','ab') as f:
            writer = csv.writer(f)
            writer.writerows(all_jobs)
        print "\nLookup table written successfully"

    #website's source code is converted from unicode to UTF
    def encodetoUTF(self,s):
        s = s.get_text().strip()
        s = u''.join(s).encode('utf-8').strip()
        return s

    #website's source code is converted from unicode to UTF for two paremters (job type + job description)
    def encode2toUTF(self,s, s2):
        s = s.get_text().strip() + " " + s2.get_text().strip()
        s = u''.join(s).encode('utf-8').strip()
        return s

    #returs the list of keywords in a sequence appropriate to use in the URL for web scrapping
    def getFormmatedKeywordSequence(self,keyword_list):
        keyword_list = shlex.split(keyword_list)
        keyword_sequence = ""
        for i in range(0, len(keyword_list)):
            if " " in keyword_list[i]:
                keyword_list[i] = '"' + keyword_list[i].replace(" ", "+") + '"'
            if i == len(keyword_list) - 1:
                keyword_sequence = keyword_sequence + keyword_list[ i]
            else:
                keyword_sequence = keyword_sequence + keyword_list[i] + "+"
        return keyword_sequence

    #loadIndeed() method loads jobs from Indeed.com
    def loadIndeed(self,keywords):
        print "Loading jobs from Indeed.com, please wait."
        keyword_sequence = self.getFormmatedKeywordSequence(keywords)

        all_jobs = []
        for page_position in range(1, self.LIMIT_OF_SEARCH_PAGES*50, 50):
            URL = "https://www.indeed.com/jobs?q="+keyword_sequence+"&l=United+States&limit=50&start="+ str(page_position)
            url_code = urllib2.urlopen(URL).read()
            soup = BeautifulSoup(url_code, 'html.parser')

            results = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})
            for x in results:
                current_job = []

                company = x.find('span', attrs={"itemprop": "name"})
                current_job.append(self.encodetoUTF(company))

                job = x.find('a', attrs={'data-tn-element': "jobTitle"})
                current_job.append(self.encodetoUTF(job))

                location = x.find('span', attrs={"itemprop": "addressLocality"})
                current_job.append(self.encodetoUTF(location))

                description = x.find('span', attrs={"itemprop": "description"})
                current_job.append(self.encodetoUTF(description))

                j_link = x.find('a')['href']
                current_job.append("http://indeed.com" + j_link.strip())

                current_job.append(keyword_sequence)

                all_jobs.append(current_job)

        #print "Loaded",len(all_jobs),"jobs from Indeed.com"
        return all_jobs

    #loadACMIEEE() methods loads the jobs from ACM or IEEE depending on the site parameter given as its input
    def loadACMIEEE(self,keywords,site):
        print "\nLoading jobs from " + site.upper() + ".ORG, please wait"
        keyword_sequence = self.getFormmatedKeywordSequence(keywords)

        all_jobs = []

        for page_num in range(1,self.LIMIT_OF_SEARCH_PAGES+1):
            URL = "http://jobs.ieee.org/jobs/results/keyword/"+keyword_sequence+"/United+States?rows=50&radius=150&page=" + str(page_num)
            if site=='acm':
                URL = "http://jobs.acm.org/jobs/results/keyword/"+keyword_sequence+"/United+States?rows=50&radius=150&NormalizedCountry=US&page=" + str(page_num)
            url_code = urllib2.urlopen(URL).read()
            soup = BeautifulSoup(url_code, 'html.parser')

            results = soup.find_all('div', attrs={'id': 'aiDevHighlightBoldFontSection'})

            for x in results:
                current_job = []
                company = x.find('li', attrs={"class": "aiResultsCompanyName"})
                current_job.append(self.encodetoUTF(company))

                job = x.find('a', attrs={'onclick': "return false;"})
                current_job.append(self.encodetoUTF(job))

                location = x.find('span', attrs={"class": "aiResultsLocationSpan"})
                current_job.append(self.encodetoUTF(location))

                category = x.find('li', attrs={"id": "searchResultsCategoryDisplay"})
                description = x.find('div', attrs={"class": "aiResultsDescription"})
                if description is None:
                    description = x.find('div', attrs={"class": "aiResultsDescriptionNoAdvert"})
                if category is None:
                    current_job.append(self.encodetoUTF(description))
                else:
                    current_job.append(self.encode2toUTF(category, description))

                j_link = x.find('a')['href']
                j_link = u''.join(j_link).encode('utf-8').strip()
                current_job.append("http://jobs."+site+".org" + j_link.strip())

                current_job.append(keyword_sequence)

                all_jobs.append(current_job)
        #print "Loaded "+str(len(all_jobs))+" jobs from",site.upper()+".ORG"
        return all_jobs

    # printHTMLTable() method writes job search results in a HTML file and then loads that file in the system's browser
    def printHTMLTable(self,all_jobs,keywords,k):
        top_jobs = all_jobs[:int(k)]
        keyword_sequence = ""
        for item in keywords:
            keyword_sequence = keyword_sequence + item +" "

        table_1 = """<html>
        <head>
        <title>Job Results</title>
        <style>
        table.GeneratedTable {
          width: 100%;
          background-color: #ffffff;
          border-collapse: collapse;
          border-width: 2px;
          border-color: #ffcc00;
          border-style: solid;
          color: #000000;
        }
        
        table.GeneratedTable td, table.GeneratedTable th {
          border-width: 2px;
          border-color: #ffcc00;
          border-style: solid;
          padding: 3px;
        }
        
        table.GeneratedTable thead {
          background-color: #ffcc00;
        }
        </style>
        </head>
        <body>
        <h3>Job results</h3>
		<h4>Keyword Sequence:<br>"""

        table_1 = table_1 + keyword_sequence + "<br><br>K: " + str(k) + """</h4><table class="GeneratedTable">
          <thead>
            <tr>
              <th>Company Name</th>
              <th>Position</th>
              <th>Location</th>
              <th>Description</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>"""

        f = open("job_search.html","w")
        f.write(table_1)
        for item in top_jobs:
            f.write("<tr>")
            for j in range(0,5):
                f.write("<td>")
                if j==4:
                    f.write('<a target="_blank" href="')
                    f.write(item[j])
                    f.write('">')
                    f.write(item[j])
                    f.write("</a>")
                else:
                    f.write(item[j])
                f.write("</td>")
            f.write("</tr>")

        table_2 = """</tbody>
                    </table>
                    </body>
                    </html>"""

        f.write(table_2)
        f.close()
        webbrowser.open("job_search.html")

        print "Job results opened as webpage in browser"