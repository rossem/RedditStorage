import gc
import os.path
from base64 import b64encode, b64decode
import praw
from typing import Tuple, List
from time import sleep
from secrets import SystemRandom
from redditglobals import *
from argon2 import Parameters  # For typehints


# Tuple containing [ciphertext, MAC, salt, time_cost, memory_cost, parallelism, hash_len, argon2type, argon2version]
def post_encryption(post_title, ciphertext: bytes, MAC: bytes, salt: str, nonce: bytes, argon2_params: Parameters):
    """
    Posts encrypted ciphertext to a subreddit defined in redditglobals.py
    :param post_title: The title of the post to make
    :param ciphertext: Encrypted text to post, encoded in base64
    :param MAC: Associated MAC for the ciphertext, encoded in base64
    :param salt: Salt used to hash the password, encoded in base64 utf-8
    :param nonce: Nonce used by the AES algorithm
    :param argon2_params: Argon2 parameters used to hash the password
    """
    subreddit = REDDIT.subreddit(SUBREDDIT)
    does_not_exist = True
    post_title = os.path.basename(post_title)
    file_submissions = subreddit.search(post_title, SUBREDDIT)

    # getting the submission of the file if it exists already
    count = 0
    filename_lower = post_title.lower()
    for submission in file_submissions:
        if filename_lower in submission.title.lower():  # Looks for submissions with filename inside it
            count += 1
            does_not_exist = False

    # create submission. Post text will be params necessary to recreate the hash in argon2
    # Format is MAC$salt$time cost$memory cost$parallelism$hash length$salt length$argon2 type$argon2 version$nonce
    # Ex: examplemac$examplesalt$20$45$4$32$16$Type.ID$19
    post_text = f'{MAC.decode("utf-8")}${salt}==${argon2_params.time_cost}${argon2_params.memory_cost}$' \
                f'{argon2_params.parallelism}${argon2_params.hash_len}${argon2_params.salt_len}${argon2_params.type}${argon2_params.version}${nonce.decode("utf-8")}'
    if does_not_exist:
        file_post = subreddit.submit(post_title, selftext=post_text)
    else:  # if file exists, then add a number to the end of the filename
        file_post = subreddit.submit(post_title + " (" + str(count) + ")", selftext=post_text)
    del post_text
    gc.collect()
    # going to be splitting the encryption since the comment limit is 10000 characters
    # this is the first-level comment

    print(f'\nNumber of comments to post: {len(ciphertext) / 10000 + 1}\n')
    rand_num = SystemRandom()
    current_comment = file_post.reply(ciphertext[:10000])
    cur_index = 10000
    ciphertext_len = len(ciphertext)
    num_comments = 1
    next_sleep = rand_num.randrange(10, 22)
    print(f'\nPosted {num_comments} comment\n')
    # Tries to reply with max chars for comments (10,000) until there isn't enough in the buffer
    while ciphertext_len - cur_index >= 10000:  # Keep replying with max chars until we can't
        current_comment = current_comment.reply(ciphertext[cur_index:cur_index + 10000])
        num_comments += 1
        print(f'Posted {num_comments} comment\n')
        if num_comments == next_sleep:
            print('Sleeping')
            next_sleep += rand_num.randrange(1, 10)  # Stop commenting after 1-10 comments
            sleep(float(rand_num.randrange(200, 450)) / 10.0)  # 20.0-45.0 second sleep
        cur_index += 10000
    if ciphertext_len > cur_index:
        current_comment.reply(ciphertext[cur_index:])
    del ciphertext
    gc.collect()


def get_ciphertext(post_title) -> Tuple[bytes, List[str]]:
    """
    Returns the ciphertext and MAC from given post title
    :param post_title: Name of the post to find
    :return: A tuple containing [ciphertext, argon2 parameters]. Only ciphertext is decoded from base64
    """
    ciphertext = ''

    subreddit = REDDIT.subreddit(SUBREDDIT)

    file_submissions = subreddit.search(post_title)
    subm = []
    submissions_found = 0
    # find the corresponding post for the file
    filename_lower = post_title.lower()
    for submission in file_submissions:
        if filename_lower in submission.title.lower():
            subm.append(submission)
            submissions_found += 1
    if not submissions_found:
        # todo: get an actual exception type
        raise Exception("Couldn't find file")
    if submissions_found == 1:  # Found only 1 file
        # level the comments
        subm[0].comments.replace_more(limit=None, threshold=0)
        comments = subm[0].comments.list()
        params: List[str] = subm[0].selftext.split('$')

        for comment in comments:
            ciphertext: str = ciphertext + comment.body

        return b64decode(ciphertext), params
    else:  # More than 1 similar file found;
        # todo: Need to show a dialog window so they can select which version to dl (or all)
        subm[0].comments.replace_more(limit=None, threshold=0)
        comments = subm[0].comments.list()
        params: List[str] = subm[0].selftext.split('$')
        for comment in comments:
            ciphertext: str = ciphertext + comment.body

        return b64decode(ciphertext), params
