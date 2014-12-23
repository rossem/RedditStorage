import praw
import getpass

USERAGENT = ""
USERNAME = ""
PASSWORD = ""
SUBREDDIT = ""
#MAXPOSTS = 100 

continueloop = True

r = praw.Reddit(USERAGENT) 
r.login(USERNAME,PASSWORD)


def main():
    print "Welcome to RedditStorage. What would you like to do?"
    print "1 - retrieve a file"

    while continueloop:
        selection = int(raw_input("> "))

        if selection == 1: 
    
            filename = raw_input("Enter filename(include file extension): ")
            filestring = searchForFile(filename)
            
            if filestring != "":
                encrypt(filestring)

                

