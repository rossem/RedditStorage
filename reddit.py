import os.path

import praw

from redditglobals import *


def post_encryption(filename, encrypt_items):
    subreddit = REDDIT.subreddit(SUBREDDIT)
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

    # create submission. Post text will be the MAC
    if does_not_exist:
        file_post = subreddit.submit(filename, selftext=encrypt_items[1])
    else:   # if file exists, then add a number to the end of the filename
        file_post = subreddit.submit(filename + " (" + str(count) + ")", selftext=encrypt_items[1])

    # going to be splitting the encryption since the comment limit is 10000 characters
    # this is the first-level comment

    current_comment = file_post.reply(encrypt_items[0][:10000])
    cur_index = 10000
    ciphertext_len = len(encrypt_items[0])

    # Tries to reply with max chars for comments (10,000) until there isn't enough in the buffer
    while ciphertext_len - cur_index >= 10000:  # Keep replying with max chars until we can't
        current_comment = current_comment.reply(encrypt_items[0][cur_index:cur_index+10000])
        cur_index += 10000
    if ciphertext_len > cur_index:
        current_comment.reply(encrypt_items[0][cur_index:])


def get_ciphertext(filename):
    ciphertext = ''
    
    subreddit = REDDIT.subreddit(SUBREDDIT)

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
        comments = subm[0].comments.list()
        mac: str = subm[0].selftext
        for comment in comments:
            ciphertext: str = ciphertext + comment.body

        return [ciphertext, mac]
    else:   # More than 1 similar file found; todo: Need to show a dialog window so they can select which version to dl (or all)
        subm[0].comments.replace_more(limit=None, threshold=0)
        mac: str = subm[0].selftext
        comments = subm[0].comments.list()

        for comment in comments:
            ciphertext: str = ciphertext + comment.body

        return [ciphertext, mac]

