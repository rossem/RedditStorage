import os.path

import praw

from redditglobals import *


def post_encryption(filename, encryption):
    subreddit = r.subreddit(SUBREDDIT)
    does_not_exist = True
    filename = os.path.basename(filename)
    file_submissions = subreddit.search(filename, SUBREDDIT)

    # getting the submission of the file if it exists already
    count = 0
    filename_lower = filename.lower()
    for submission in file_submissions:
        if filename_lower in submission.title.lower():  # Looks for submissions with filename inside it
            count += 1
            does_not_exist = False

    # create submission
    if does_not_exist:
        file_post = subreddit.submit(filename, selftext='')
    else:   # if file exists, then add a number to the end of the filename
        file_post = subreddit.submit(filename + " (" + str(count) + ")",selftext='')

    # going to be splitting the encryption since the comment limit is 10000 characters
    # this is the first-level comment

    current_comment = file_post.reply(encryption[:10000])
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
    
    subreddit = r.subreddit(SUBREDDIT)

    file_submissions = subreddit.search(filename)
    subm = []
    submissions_found = 0
    # find the corresponding post for the file
    filename_lower = filename.lower()
    for submission in file_submissions:
        if filename_lower in submission.title.lower():
            subm.append(submission)
            submissions_found += 1
    if not submissions_found:
        # todo: get an actual exception type
        raise Exception("Couldn't find file")
    if submissions_found == 1:  # Found only 1 file
        # level the comments
        subm[0].replace_more(limit=None, threshold=0)
        comments = praw.helpers.flatten_tree(subm[0].comments)

        for comment in comments:
            decryption = decryption + comment.body

        return decryption
    else:   # More than 1 similar file found; todo: Need to show a dialog window so they can select which version to dl (or all)
        subm[0].comments.replace_more(limit=None, threshold=0)
        comments = subm[0].comments.list()

        for comment in comments:
            decryption = decryption + comment.body

        return decryption

