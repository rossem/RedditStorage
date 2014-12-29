import praw
from redditglobals import *

def post_encryption(filename, encryption):
    subreddit = r.get_subreddit(SUBREDDIT)
    #print "fetching comments"
    #comments = subreddit.get_comments()

    does_not_exist = True 
    file_submissions = r.search(filename, SUBREDDIT)

    #getting the submission of the file if it exists already
    count = 0
    for submission in file_submissions:

        if filename.lower() in submission.title.lower():
            count += 1
            does_not_exist = False

            #overwrite the file: need to delete the previous comments in this submission
            forest_comments = submission.comments
            flat_comments = praw.helpers.flatten_tree(forest_comments)

            #for comment in flat_comments:
            #    comment.delete()

            #break out of the loop, found our submission
            break

    #create submission if does not exist
    if does_not_exist:
        file_post = r.submit(SUBREDDIT, filename, " ", raise_captcha_exception=True)
    else: 
        file_post = r.submit(SUBREDDIT, filename + " (" + str(count) + ")", " ",raise_captcha_exception = True)

    
    #going to be splitting the encryption since the comment limit is 10000 characters
    #this is the first-level comment

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



#When writing the function to fetch the comments and turn it into file, remember to use flat_comments: they come sorted already => just need to concatenate them

def get_decryption(filename):

    decryption = '' #what we want to return
    
    subreddit = r.get_subreddit(SUBREDDIT)
    comments = subreddit.get_comments()

    file_submissions = r.search(filename, SUBREDDIT)

    #find our file's post
    for submission in file_submissions:

        if submission.title.lower() == filename.lower():
            subm = submission
            break
    #make all of the comments same-level 
    comments = praw.helpers.flatten_tree(subm.comments)

    for comment in comments:
        decryption = decryption + comment.body

    return decryption

            


