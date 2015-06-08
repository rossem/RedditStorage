#RedditStorage
######a cloud storage that uses Reddit as a backend. 

=============

RedditStorage is an application which allows you to store on reddit subreddits via raw bytes. The file is encoded into characters and encrypted using AES encryption, after which it can be stored on a subreddit of choice. To restore the file, the process is simply reversed. Unfortunately, reddit comments have a character limit of 10000. If your file exceeds that amount, it will be split up among comments in the same thread which form links by replying to each other. 

=============

What you need to use it:
* reddit account (preferabely with over 1 link karma on it)
* private subreddit in which your reddit account is a moderator (make sure to set the spam filter strength of self posts and comments to "low")
* Python 2.7
* Crypt.py
* wxPython 3.0+
* praw

=============

How to use it:

1. RedditStorage uses an AES encryption algorithm which requires you to choose a password(e.g. "bunny).
2. Run python RedditStorage.py
3. Enter your username, password, subreddit and desired encryption key
4. Choose the file you want to upload
5. When getting the file, choose the file you want to get and how/where you want to save it


Screenshots


===========

![ss1](screenshot1.png "Post")
![ss2](screenshot2.png "Get")
![ss3](screenshot3.png "See which files are uploaded")
![ss4](screenshot4.png "README.md uploaded")
![ss5](screenshot5.png "Big file made up of linked comments")


To Do

==============

* Save username/password between sessions
* Upload as webapp
* Auto generate subreddits
