'''
Developer: Abhishek Manoj Sharma
Date: September 27, 2017
Input: Two arguments
1. Keywords
2. Value of k
'''

from argparse import ArgumentParser
from job_search_environment import Environment

#Implementing argparse for command line interface
help_description="The program accepts two command line inputs, keywords and k. The program displays k jobs closest to the input keywords, calculated using Jaccard's algorithm. The user can also choose to view the cluster by choosing option 3 in the menu that follows.\nPlease Note: The program builds a lookup table for the first time it runs on a new machine, and hence the first run may take up to 4-5 minutes to complete."

parser = ArgumentParser(description=help_description)

parser.add_argument("-keywords", nargs='+',
                    help='Specificy the keywords to search jobs. Separate each keyword with a space. Use double quotes for exact matches, eg: "Machine Learning"',
                        required=True)

parser.add_argument("-k", help='Specify an integery value for k (max 15)', type=int,required=True)

args = parser.parse_args()

#checking if the value of k is between 0 and 15
if args.k<=0 or args.k>15:
    print "Invalid k.\nValue of K should be greater than 0 and less than or equal to 15.\nExiting program."
else:
    e = Environment()

    #checking if the keywords contain any quoted sequence, eg: "Mahcine Learning"
    if isinstance(args.keywords,str):

        #envFirstRun() method is invoked when the program is run and fetches jobs according to the command line inputs
        e.envFirstRun(args.keywords, args.k)
    else:
        keywords = '+'.join(args.keywords)
        keywords = keywords.split("+")
        for i in range (0,len(keywords)):
            if " " in keywords[i]:
                keywords[i] = '"' + keywords[i] + '"'
                keywords[i] = keywords[i].replace(" ","+")
        s = keywords[0]
        for i in range(1,len(keywords)):
            s = s + " " + keywords[i]
        e.envFirstRun(s,args.k)
