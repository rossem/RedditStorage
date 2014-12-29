import praw

global USERAGENT,USERNAME,PASSWORD,SUBREDDIT,r

USERAGENT = "reddit storage bot"
USERNAME = ""
PASSWORD = ""
SUBREDDIT = "redditstoragetest"
#MAXPOSTS = 100 

r = praw.Reddit(USERAGENT) 
