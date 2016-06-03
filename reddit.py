import praw

from redditglobals import *


def post_encryption(filename, encryption):
    subreddit = r.get_subreddit(SUBREDDIT)
    does_not_exist = True 
    file_submissions = r.search(filename, SUBREDDIT)

    # getting the submission of the file if it exists already
    count = 0
    for submission in file_submissions:
        if filename.lower() in submission.title.lower():
            count += 1
            does_not_exist = False

    # create submission if does not exist
    if does_not_exist:
        file_post = r.submit(SUBREDDIT, filename, " ")
    else: 
        file_post = r.submit(SUBREDDIT, filename + " (" + str(count) + ")", " ")

    # going to be splitting the encryption since the comment limit is 10000 characters
    # this is the first-level comment

    current_comment = file_post.add_comment(encryption[:10000])
    encryption = encryption[10000:]

    #if it does not fit, then we will add a child comment to it and repeat
    if len(encryption) != 0:

        while len(encryption) > 10000: 
            #to-do
            current_comment = current_comment.reply(encryption[:10000])
            encryption = encryption[10000:]

    if len(encryption) > 0:
        current_comment.reply(encryption)


def get_decryption(filename):
    decryption = ''
    
    subreddit = r.get_subreddit(SUBREDDIT)
    comments = subreddit.get_comments()

    file_submissions = r.search(filename, SUBREDDIT)

    # find the corresponding post for the file
    for submission in file_submissions:

        if submission.title.lower() == filename.lower():
            subm = submission
            break

    # level the comments
    subm.replace_more_comments(limit=None, threshold=0)
    comments = praw.helpers.flatten_tree(subm.comments)

    for comment in comments:
        decryption = decryption + comment.body

    return decryption

