#RedditStorage
<<<<<<< HEAD
<<<<<<< HEAD
######a cloud storage that uses Reddit as a backend. 
=======
=============

=======
>>>>>>> f6b387c528e2c3de8e8fb515d874b53d5caeb02b
######a cloud storage that uses Reddit as a backend
>>>>>>> 2b549bb3a8d6a14640d5b3d54b8e7be605d347a1

=============

RedditStorage is an application which allows you to store on reddit subreddits via raw bytes. The file is encoded into characters and ecrypted using AES encryption, after which it can be stored on a subreddit of choice. To restore the file, the process is simply reversed. Unfortunately, reddit comments have a character limit of 10000. If your file exceeds that amount, it will be split up among comments in the same thread which form links by replying to each other. 

=============

What you need to use it:
* reddit account (preferabely with over 1 link karma on it)
* private subreddit in which your reddit account is a moderator (make sure to set the spam filter strength of self posts and comments to "low")

=============

How to use it:

1. RedditStorage uses an AES encryption algorithm which requires you to choose a password(e.g. "bunny). So choose one, and replace our default password (which is "hello") in key.py
2. Run the program
3. Enter your username, password and subreddit
4. When posting the file, make sure to enter the **full** path of the file. E.g. /Users/ross/Desktop/hello.txt
5. When getting the file, choose where you want to save the file (/Users/ross/Desktop/folder) and add the file's name (hello.txt), so your full entry would be /Users/ross/Desktop/folder/hello.txt
