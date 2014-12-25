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

    for submission in file_submissions:

        if submission.title.lower() == filename.lower():
            file_post = submission
            does_not_exist = False
            break


    if does_not_exist:
        file_post = r.submit(SUBREDDIT, filename, " ")

    while len(encryption) > 10000: 
        #to-do




        



        
            

    
