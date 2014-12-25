import praw

def searchForFile(filenm):
    fileString = "" #this is the string that we want to return

    print "Fetching subreddit"
    subreddit = r.get_subreddit(SUBREDDIT)

    print "Fetching comments"
    comments = subreddit.get_comments()

    for comment in comments:
        cbody = comment.body.lower()

        if cbody == filenm.lower() and comment.is_root():
            creplies = comment.replies()
            
            for reply in creplies:
               rbody = reply.body
               fileString = fileString + rbody

            return fileString


def post_encryption(filename, encryption):
    print "fetching subreddit"
    subreddit = r.get_subreddit(SUBREDDIT)
    print "fetching comments"
    comments = subreddit.get_comments()

    does_not_exist = True 

    file_submissions = r.search(filename, SUBREDDIT)

    #getting the submission of the file if it exists already
    for submission in file_submissions:

        if submission.title.lower() == filename.lower():
            file_post = submission
            does_not_exist = False

            #overwrite the file: need to delete the previous comments in this submission
            forest_comments = submission.comments
            flat_comments = praw.helpers.flatten_tree(forest_comments)

            for comment in flat comments:
                comment.delete()

            #break out of the loop, found our submission
            break

    #create submission if does not exist
    if does_not_exist:
        file_post = r.submit(SUBREDDIT, filename, " ")
    
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

    if len(encryption) != 0:
        current_comment.reply(encryption)






        



        
            

    
