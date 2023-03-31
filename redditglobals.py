import praw

global USERAGENT, SUBREDDIT, REDDIT

USERAGENT = "reddit storage bot"
SUBREDDIT = "subredditname"
# MAXPOSTS = 100

REDDIT = praw.Reddit(USERAGENT)
