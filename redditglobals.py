import praw
from configparser import ConfigParser
global USERAGENT, SUBREDDIT, REDDIT
config = ConfigParser()
config.read('praw.ini')
USERAGENT = "reddit storage bot"
"""The useragent of the bot. See https://en.wikipedia.org/wiki/User_agent for more details"""
SUBREDDIT = config['reddit storage bot']['subreddit']
"""The name of the subreddit files are posted to."""

REDDIT = praw.Reddit(USERAGENT)
"""Praw instance for accessing Reddit."""
