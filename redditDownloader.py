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
