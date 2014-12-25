import praw

global USERAGENT,USERNAME,PASSWORD,SUBREDDIT,r

USERAGENT = "/u/wltrs testing reddit bot"
USERNAME = ""
PASSWORD = ""
SUBREDDIT = "redditstoragetest"
#MAXPOSTS = 100 

r = praw.Reddit(USERAGENT) 
