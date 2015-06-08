#!/usr/bin/python

# simple.py

import praw
from reddit import *
import getpass

from crypt import AESCipher
import hashlib
import os
import base64

from Crypto.Cipher import AES
from Crypto import Random

from redditglobals import * 
import wx
from wx.lib.pubsub import pub 

# cleanup dist and build directory first (for new py2exe version) 
#if os.path.exists("dist/prog"): 
 #   shutil.rmtree("dist/prog") 

#if os.path.exists("dist/lib"): 
 #   shutil.rmtree("dist/lib") 

#if os.path.exists("build"): 
 #   shutil.rmtree("build") 

wildcard = "All files (*.*)|*.*"
    
class RedditList(wx.Frame):
    

    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY,"Files Stored", size = (300, 400))
        self.panel = wx.Panel(self)
        pub.subscribe(self.subredditListener, "subredditListener")
        self.InitUI()

    def InitUI(self):

        self.fileList = wx.ListCtrl(self.panel, size=(-1,300), style = wx.LC_REPORT
            |wx.EXPAND)
        self.fileList.InsertColumn(0,"File Name", width = 500)

        self.gs = wx.GridSizer(1,2,0,0)

        submitButton = wx.Button(self.panel, label = "Submit")
        submitButton.Bind(wx.EVT_BUTTON, self.onSubmit)
        closeButton = wx.Button(self.panel, label= "Close")
        closeButton.Bind(wx.EVT_BUTTON, self.onClose)

        saveButton = wx.Button(self.panel, label="Save Fields")

        generateButton = wx.Button(self.panel, label = "Generate Subreddit")

        self.gs.Add(submitButton)
        self.gs.Add(closeButton)

        sizer = wx.BoxSizer(wx.VERTICAL)
        flags = wx.ALL|wx.EXPAND
        sizer.Add(self.fileList, 0, wx.ALL|wx.EXPAND, 5)
        
        sizer.Add(self.gs, flag=wx.ALIGN_BOTTOM|wx.EXPAND|wx.ALL, border=5)
        self.panel.SetSizer(sizer)

    def subredditListener(self, subredditName, username, password):
        r = praw.Reddit("reddit storage bot " + username)
        r.login(username, password)
        subreddit = r.get_subreddit(subredditName)
        global posts
        posts = subreddit.get_new(limit=1000)
        index = 0
        self.myRowDict = {} #dictionary used for retrival later
        for x in posts:
            print str(x)
            self.fileList.InsertStringItem(index, x.title)
            self.myRowDict[index] = x.title
            index+=1
        print "done"



    def onClose(self, event):
        self.Close()

    def onSubmit(self, event):
        pub.sendMessage("fileListener", fileName = self.myRowDict[get_selected_items(self.fileList)[0]])
        self.Close()


def get_selected_items(list_control):
    
    #Gets the selected items for the list control.
    #Selection is returned as a list of selected indices,
    #low to high.
    
    selection = []

    # start at -1 to get the first selected item
    current = -1
    while True:
        next = GetNextSelected(list_control, current)
        if next == -1:
            return selection

        selection.append(next)
        current = next

def GetNextSelected(list_control, current):
    #Returns next selected item, or -1 when no more

    return list_control.GetNextItem(current,
                            wx.LIST_NEXT_ALL,
                            wx.LIST_STATE_SELECTED)


class PostPanel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent,id=wx.ID_ANY)

        self.InitUI()

    def InitUI(self):
        ID_POST_BUTTON = wx.NewId()
        ID_BROWSE_FILE_BUTTON = wx.NewId()

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(5,2,9,15)        
        gs = wx.GridSizer(2,2,9,10)

        global username
        username = wx.StaticText(self, label="Username")
        password = wx.StaticText(self, label="Password")
        subreddit = wx.StaticText(self, label="Subreddit")
        KEYPASS = wx.StaticText(self, label = "Encryption key")
        filename = wx.StaticText(self, label="Filepath")
        post = wx.Button(self, ID_POST_BUTTON, "Post")        
        browseFile=wx.Button(self, ID_BROWSE_FILE_BUTTON, "Browse File")
        global postMessage
        postMessage = wx.StaticText(self,label = "")

        self.usernameField = wx.TextCtrl(self)
        self.passwordField = wx.TextCtrl(self, style = wx.TE_PASSWORD)
        self.subredditField = wx.TextCtrl(self)
        self.keypassField = wx.TextCtrl(self)   
        self.filepathField = wx.TextCtrl(self)
        

        fgs.AddMany([(username), (self.usernameField, 1, wx.EXPAND), (password), 
            (self.passwordField, 1, wx.EXPAND), (subreddit, 1, wx.EXPAND), (self.subredditField, 1, wx.EXPAND),
            (KEYPASS, 1, wx.EXPAND), (self.keypassField, 1, wx.EXPAND), (filename, 1, wx.EXPAND),
            (self.filepathField, 1, wx.EXPAND)])

        gs.AddMany([(post,1,wx.EXPAND),(browseFile,1,wx.EXPAND), (postMessage)])

        
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        hbox.Add(gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        #hbox.Add(postMessage, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(hbox)

        post.Bind(wx.EVT_BUTTON, self.onClickPostItem, post)
        browseFile.Bind(wx.EVT_BUTTON, self.onClickBrowseFile, browseFile)
    
    def onClickBrowseFile(self,e):
        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'open' dialog, and allows multitple
        # file selections as well.
        #
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            #Use GetPaths() for multiple files
            paths = dlg.GetPath()
            self.filepathField.SetValue(paths)

            #self.log.WriteText('You selected %d files:' % len(paths))

            #for path in paths:
            #   self.log.WriteText('           %s\n' % path)

        # Compare this with the debug above; did we change working dirs?
        #self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()


    def onClickPostItem(self,e):
        if (self.usernameField.IsEmpty()):
            postMessage.SetLabel("No Username Specified")
        elif (self.passwordField.IsEmpty()):
            postMessage.SetLabel("No Password Entered")
        elif (self.subredditField.IsEmpty()):
            postMessage.SetLabel("No Subreddit Specified")
        elif (self.keypassField.IsEmpty()):
            postMessage.SetLabel("No Encryption Key Specified")
        elif (self.filepathField.IsEmpty()):
            postMessage.SetLabel("No Filepath Specified")
        else:
            postItem(self.usernameField.GetValue(), self.passwordField.GetValue(), self.subredditField.GetValue(),
            self.filepathField.GetValue(), self.keypassField.GetValue())  

class GetPanel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent,id=wx.ID_ANY)
        pub.subscribe(self.fileListener, "fileListener")
        self.InitUI()

    def fileListener(self, fileName):
        self.fileToGetField.SetValue(fileName)

    def InitUI(self):
        ID_GET_BUTTON = wx.NewId()
        ID_SAVE_FILE_BUTTON = wx.NewId()
        ID_GET_REDDIT_LIST_BUTTON = wx.NewId()

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(6,2,9,15)        
        gs = wx.GridSizer(2,2,9,10)
        

        global username
        username = wx.StaticText(self, label="Username")
        password = wx.StaticText(self, label="Password")
        subreddit = wx.StaticText(self, label="Subreddit")
        file_to_get = wx.StaticText(self, label="File to get")
        KEYPASS = wx.StaticText(self, label="Encryption key")
        filename = wx.StaticText(self, label="Filepath")
        get = wx.Button(self, ID_GET_BUTTON, "Get")        
        saveFile = wx.Button(self,ID_SAVE_FILE_BUTTON, "Save File As")
        getRedditList = wx.Button(self, ID_GET_REDDIT_LIST_BUTTON, "Retrieve List of Stored Files ")

        global postMessage1
        postMessage1 = wx.StaticText(self,label = "")

        self.usernameField = wx.TextCtrl(self)
        self.passwordField = wx.TextCtrl(self, style = wx.TE_PASSWORD)
        self.subredditField = wx.TextCtrl(self)
        self.fileToGetField = wx.TextCtrl(self)
        self.keypassField = wx.TextCtrl(self)
        self.filepathField = wx.TextCtrl(self)


        fgs.AddMany([(username), (self.usernameField, 1, wx.EXPAND), (password), 
            (self.passwordField, 1, wx.EXPAND), (subreddit, 1, wx.EXPAND), (self.subredditField, 1, wx.EXPAND), 
            (file_to_get, 1, wx.EXPAND), (self.fileToGetField, 1, wx.EXPAND), (KEYPASS, 1, wx.EXPAND),
            (self.keypassField, 1, wx.EXPAND), (filename, 1, wx.EXPAND), (self.filepathField, 1, wx.EXPAND)])

        gs.AddMany([(get,1,wx.EXPAND),(saveFile,1,wx.EXPAND), (getRedditList,1,wx.EXPAND), (postMessage1)])


        
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        hbox.Add(gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        
        
        self.SetSizer(hbox)

        get.Bind(wx.EVT_BUTTON, self.onClickGetItem)
        saveFile.Bind(wx.EVT_BUTTON,self.onClickSaveItem)
        getRedditList.Bind(wx.EVT_BUTTON, self.onClickGetRedditList)

    def onClickSaveItem(self,e):
        #self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'save' dialog.
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=wildcard, style=wx.SAVE,
            )
        dlg.SetFilename(self.fileToGetField.GetValue())
        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.filepathField.SetValue(path)

            # Normally, at this point you would save your data using the file and path
            # data that the user provided to you, but since we didn't actually start
            # with any data to work with, that would be difficult.
            # 
            # The code to do so would be similar to this, assuming 'data' contains
            # the data you want to save:
            #
            # fp = file(path, 'w') # Create file anew
            # fp.write(data)
            # fp.close()
            #
            # You might want to add some error checking

        # Note that the current working dir didn't change. This is good since
        # that's the way we set it up.
        #self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()


    def onClickGetItem(self, e):
        if (self.usernameField.IsEmpty()):
            postMessage1.SetLabel("No Username Specified")
        elif (self.passwordField.IsEmpty()):
            postMessage1.SetLabel("No Password Entered")
        elif (self.subredditField.IsEmpty()):
            postMessage1.SetLabel("No Subreddit Specified")
        elif (self.fileToGetField.IsEmpty()):
            postMessage1.SetLabel("No File Specified")
        elif (self.keypassField.IsEmpty()):
            postMessage1.SetLabel("No Encryption Key Specified")
        elif (self.filepathField.IsEmpty()):
            postMessage1.SetLabel("No Filepath Specified")
        else:
            getItem(self.usernameField.GetValue(), self.passwordField.GetValue(), self.subredditField.GetValue(),
            self.filepathField.GetValue(), self.fileToGetField.GetValue(), self.keypassField.GetValue()) 
    def onClickGetRedditList(self, e):
        if(self.subredditField.IsEmpty() is False):
            print self.subredditField.GetValue()
            frame = RedditList()
            pub.sendMessage("subredditListener", subredditName = self.subredditField.GetValue()
            , username = self.usernameField.GetValue(), password = self.passwordField.GetValue())
            frame.Show()
        else:
            postMessage1.SetLabel("No Subreddit Specified")

class MainNotebook(wx.Notebook):

    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )

        self.InitUI()

    def InitUI(self):
        tabOne = PostPanel(self)
        self.AddPage(tabOne, "Post")

        tabTwo = GetPanel(self)
        self.AddPage(tabTwo, "Get")
 
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
        
class MainWindow(wx.Frame):

    def __init__(self,parent,title):
        super(MainWindow, self).__init__(parent, title=title, size=(500, 375))
        
        panel = wx.Panel(self)

        notebook = MainNotebook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        self.Layout()
        self.Centre() 
        self.Show()
            
#------------------------------------------------------------------------------


def postItem(username, password, subreddit, filename, KEYPASS):
    filepath = filename
    k = filename.rfind("/")
    filename = filename[k+1:]

    loginMod(username,password,subreddit)
    cipher = AESCipher(KEYPASS)
    comment = cipher.encrypt_file(filepath)
    post_encryption(filename, comment)
    postMessage.SetLabel("Done")
    postMessage1.SetLabel("Done")

def getItem(username, password, subreddit, filename, file_to_get, KEYPASS):

    filepath = filename
    #k = filename.rfind("/")
    #filename = filename[k+1:]
    #filepath = filepath[:k+1]
    #temp_fp = filepath
    #filepath = filepath + file_to_get

    loginMod(username,password,subreddit)
    cipher=AESCipher(KEYPASS)
    comment = get_decryption(file_to_get)
    
    """
    if filename[-1] == ")":
        j = filename.rfind("(") - 1
        n = len(filename) - j
        filepath = filepath[:-n]
    """

    cipher.decrypt_file(comment, filepath)
    postMessage1.SetLabel("Done")
    postMessage.SetLabel("Done")
    
def loginMod(username, password, subreddit):
    trying = True
    while trying:
        try:
            _login(username,password)
            trying = False
        except praw.errors.InvalidUserPass:
            postMessage.SetLabel("Wrong Password")
            postMessage1.SetLabel("Wrong Password")
    while checkForMod(username, subreddit):
        postMessage.SetLabel("Not a Moderator of the Subreddit")
        postMessage1.SetLabel("Not a Moderator of the Subreddit")

def _login(username, password):
    r.login(username,password)

def checkForMod(user, subreddit):
        
    subr = r.get_subreddit(subreddit)
    mods = subr.get_moderators()

    for mod in mods: 
        if mod == user.lower():
            return True
    return False 



if __name__ == '__main__':
  
    app = wx.App()
    MainWindow(None, title='subreddit')
    app.MainLoop()
