import praw
import redditDownloader
import getpass

USERAGENT = ""
USERNAME = ""
PASSWORD = ""
SUBREDDIT = ""
#MAXPOSTS = 100 

r = praw.Reddit(USERAGENT) 

def _login():
    USERNAME = raw_input("Username: ")
    PASSWORD = getpass.getpass()
    r.login(USERNAME, PASSWORD)

def checkForMod(user, subreddit):
        
    subr = r.get_subreddit(subreddit)
    mods = subr.get_moderators()

    for mod in mods: 
        if mod.lower() == user.lower():
            return True
    return False


trying = True

while trying:
    try:
        _login()
        trying = False
    except praw.errors.InvalidUserPass:
        print "Invalid user/pass. Please try again."


SUBREDDIT = raw_input("Subreddit: ")
while not checkForMod(USERNAME, SUBREDDIT):
    print "Enter a different subreddit."
    SUBREDDIT = raw_input("Subreddit: ")

    
while True:
    selection = int(raw_input("> "))

    if selection == 1: 

        filename = raw_input("Enter filename(include file extension): ")
        filestring = searchForFile(filename)
        
        if filestring != "":
            encrypt(filestring)

