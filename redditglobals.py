import praw
from configparser import ConfigParser
global USERAGENT, SUBREDDIT, REDDIT
config = ConfigParser()
config.read('praw.ini')
USERAGENT = "reddit storage bot"
SUBREDDIT = config['reddit storage bot']['subreddit']
# MAXPOSTS = 100

REDDIT = praw.Reddit(USERAGENT)
