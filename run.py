#!/usr/bin/python

# simple.py

import praw
from reddit import *
import getpass

from crypt import AESCipher
import hashlib
import os
from key import *
import base64

from Crypto.Cipher import AES
from Crypto import Random

from redditglobals import * 
import wx

# cleanup dist and build directory first (for new py2exe version) 
if os.path.exists("dist/prog"): 
    shutil.rmtree("dist/prog") 

if os.path.exists("dist/lib"): 
    shutil.rmtree("dist/lib") 

if os.path.exists("build"): 
    shutil.rmtree("build") 


    
class PostPanel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent,id=wx.ID_ANY)

        self.InitUI()

    def InitUI(self):
        ID_POST_BUTTON = wx.NewId()

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(4,2,9,25)        
        gs = wx.GridSizer(2,2,9,25)

        global username
        username = wx.StaticText(self, label="Username")
        password = wx.StaticText(self, label="Password")
        subreddit = wx.StaticText(self, label="Subreddit")
        filename = wx.StaticText(self, label="Filepath")
        post = wx.Button(self, ID_POST_BUTTON, "Post")        

        global postMessage
        postMessage = wx.StaticText(self,label = "")

        self.tc1 = wx.TextCtrl(self)
        self.tc2 = wx.TextCtrl(self, style = wx.TE_PASSWORD)
        self.tc3 = wx.TextCtrl(self)
        self.tc4 = wx.TextCtrl(self)


        fgs.AddMany([(username), (self.tc1, 1, wx.EXPAND), (password), 
            (self.tc2, 1, wx.EXPAND), (subreddit, 1, wx.EXPAND), (self.tc3, 1, wx.EXPAND), (filename, 1, wx.EXPAND),
          (self.tc4, 1, wx.EXPAND)])

        gs.AddMany([(post,1,wx.EXPAND), (postMessage)])

        
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        hbox.Add(gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        #hbox.Add(postMessage, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(hbox)

        post.Bind(wx.EVT_BUTTON, self.onClickPostItem)

    

    def onClickPostItem(self,e):
        postItem(self.tc1.GetValue(), self.tc2.GetValue(), self.tc3.GetValue(),
            self.tc4.GetValue())  

class GetPanel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent,id=wx.ID_ANY)

        self.InitUI()

    def InitUI(self):
        ID_GET_BUTTON = wx.NewId()

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(4,2,9,25)        
        gs = wx.GridSizer(2,2,9,25)

        global username
        username = wx.StaticText(self, label="Username")
        password = wx.StaticText(self, label="Password")
        subreddit = wx.StaticText(self, label="Subreddit")
        filename = wx.StaticText(self, label="Filepath")
        get = wx.Button(self, ID_GET_BUTTON, "Get")        

        global postMessage
        postMessage = wx.StaticText(self,label = "")

        self.tc1 = wx.TextCtrl(self)
        self.tc2 = wx.TextCtrl(self, style = wx.TE_PASSWORD)
        self.tc3 = wx.TextCtrl(self)
        self.tc4 = wx.TextCtrl(self)


        fgs.AddMany([(username), (self.tc1, 1, wx.EXPAND), (password), 
            (self.tc2, 1, wx.EXPAND), (subreddit, 1, wx.EXPAND), (self.tc3, 1, wx.EXPAND), (filename, 1, wx.EXPAND),
          (self.tc4, 1, wx.EXPAND)])

        gs.AddMany([(get,1,wx.EXPAND), (postMessage)])

        
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        hbox.Add(gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        #hbox.Add(postMessage, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(hbox)

        get.Bind(wx.EVT_BUTTON, self.onClickGetItem)

    def onClickGetItem(self, e):
        getItem(self.tc1.GetValue(), self.tc2.GetValue(), self.tc3.GetValue(),
            self.tc4.GetValue()) 


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
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
        
class MainWindow(wx.Frame):

    def __init__(self,parent,title):
        super(MainWindow, self).__init__(parent, title=title, size=(300, 275))
        
        panel = wx.Panel(self)

        notebook = MainNotebook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        self.Layout()
        self.Centre() 
        self.Show()
            
#------------------------------------------------------------------------------


def postItem(username, password, subreddit, filename):
    filepath = filename
    k = filename.rfind("/")
    filename = filename[k+1:]

    loginMod(username,password,subreddit)
    cipher = AESCipher(KEYPASS)
    comment = cipher.encrypt_file(filepath)
    post_encryption(filename, comment)
    postMessage.SetLabel("Done")

def getItem(username, password, subreddit, filename):
    filepath = filename
    k = filename.rfind("/")
    filename = filename[k+1:]

    loginMod(username,password,subreddit)
    cipher=AESCipher(KEYPASS)
    comment = get_decryption(filename)
    
    if filename[-1] == ")":
        j = filename.rfind("(") - 1
        n = len(filename) - j
        filepath = filepath[:-n]

    cipher.decrypt_file(comment, filepath)
    postMessage.SetLabel("Done")
    
def loginMod(username, password, subreddit):
    trying = True
    while trying:
        try:
            _login(username,password)
            trying = False
        except praw.errors.InvalidUserPass:
            postMessage.SetLabel("Wrong Password")
    while checkForMod(username, subreddit):
        postMessage.SetLabel("Not a Moderator of the Subreddit")

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
