'''
Developer: Abhishek Manoj Sharma
Date: September 27, 2017
Class: Environment
'''

from job_search_agent import Agent
from random import randint
from operator import itemgetter
import webbrowser

class Environment:

    #initializing the all_jobs variable to load all the retrieved jobss
    all_jobs = []

    #envFirstRun() method is invoked when the program is run and fetches jobs according to the command line inputs
    def envFirstRun(self, keyword_input, k):
        a = Agent()
        self.all_jobs = a.searchJobs(keyword_input, k)
        self.printMenu(keyword_input, k)

    #printMenu() method contains the options for the menu-driven logic allowing user to make choices
    def printMenu(self,keyword_input,k):

        print "\n--------------------\nType the corresponding number and press enter"
        print "1. Start a new search"
        print "2. Run previous search again - ", "Keywords:", keyword_input, ", Value of k:",k
        print "3. Cluster previous search - ", "Keywords:", keyword_input, ", Value of k:",k
        print "4. Quit"
        option = raw_input("Enter the number: ")
        try:
            option = int(option)
            if option==1:
                keyword_input_new = raw_input("\n---------------\nEnter search keywords: ")
                k_new = raw_input("Enter the value of k: ")

                #checking if k is an integer
                if k_new.isdigit():
                    a = Agent()
                    self.all_jobs = a.searchJobs(keyword_input_new, k_new)

                    #replacing the history variables with the new values
                    self.printMenu(keyword_input_new,k_new)
                else:
                    print "Invalid value of k, try again"
                    self.printMenu(keyword_input,k)
            elif option==2:
                a = Agent()
                self.all_jobs = a.searchJobs(keyword_input, k)
                self.printMenu(keyword_input, k)
            elif option==3:
                print "Clustering"
                self.clusterJobs(k)
                self.printMenu(keyword_input, k)
            elif option==4:
                print "Quitting program"
                exit(0)
            else:
                print "Invalid option selected.\nTry again"
                self.printMenu(keyword_input,k)
        #throws an error if the input is not an integer
        except ValueError:
            print "Invalid option selected.\nTry again"
            self. printMenu(keyword_input,k)

    #clusterJobs() method is used for clustering 15 jobs based on the value of k
    def clusterJobs(self,k):
        centroid_jobs = []
        for i in range(0,int(k)):
            r = randint(0,len(self.all_jobs)-1)
            centroid_jobs.append(self.all_jobs[r])
            self.all_jobs.pop(r)

        for row in self.all_jobs:
            job_words = (row[0] + " " + row[1] + " " + row[2] + " " + row[3]).lower()
            job_words = job_words.split(" ")
            row.append(self.getClosestCentroid(centroid_jobs,job_words))

        self.printHTMLTable(self.all_jobs,centroid_jobs,k)

    #getClosestCentroid() method is is used to find the nearest of the k centroids for a given job record
    def getClosestCentroid(self,centroid_jobs,jobs_words):
        jaccard_distances = []
        for item in centroid_jobs:
            centroid_words = ""
            centroid_words = (item[0] + " " + item[1] + " " + item[2] + " " + item[3]).lower()
            centroid_words = centroid_words.split(" ")
            jaccard_distances.append(self.jaccardDistance(jobs_words,centroid_words))
        return min(enumerate(jaccard_distances), key=itemgetter(1))[0]

    #jaccardDistance() method calculates the distance for clustering
    def jaccardDistance(self,keywords, job_details):
        for i in range(0, len(keywords)):
            keywords[i] = keywords[i].lower()
        for i in range(0, len(job_details)):
            job_details[i] = job_details[i].lower()
        intersection = len(set.intersection(*[set(keywords), set(job_details)]))
        union = len(set.union(*[set(keywords), set(job_details)]))
        return 1 - intersection / float(union)

    #printHTMLTable() method writes clustering tables in a HTML file and then loads that file in the system's browser
    def printHTMLTable(self, all_jobs, centroid_jobs,k):

        #storing the html code to write in a string
        table_1 = """<html>
        <head>
        <title>Cluster Results</title>
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
        <h3>Lloyd's Clustering</h3>
        <h4>K: """ + str(k) + "</h4>"

        f = open("cluster.html", "w")
        f.write(table_1)

        #generating table code
        for i in range(0,len(centroid_jobs)):
            table_text = """<table class="GeneratedTable">
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
            f.write(table_text)
            cluster_jobs = []
            cluster_jobs.append(centroid_jobs[i])
            for item in all_jobs:
                if item[7] == i:
                    cluster_jobs.append(item)
            for item in cluster_jobs:
                f.write("<tr>")
                for j in range(0,5):
                    f.write("<td>")
                    #checking the value of j as the last column in the table must be a clickable URL
                    if j == 4:
                        f.write('<a target="_blank" href="')
                        f.write(item[j])
                        f.write('">')
                        f.write(item[j])
                        f.write("</a>")
                    else:
                        f.write(item[j])
                    f.write("</td>")
                f.write("</tr>")
            f.write("</tbody></table><br>")

        f.write("</body></html>")

        f.close()

        #opening the browser to load cluster.html file
        webbrowser.open("cluster.html")

        print "Cluster result opened as webpage in browser"