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

class MainWindow(wx.Frame):
  
    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, 
            size=(300, 250))
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):
    
        ID_POST_BUTTON = wx.NewId()
        ID_GET_BUTTON = wx.NewId()

        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(4, 2, 9, 25)

        gs = wx.GridSizer(2,2,9,25)

        username = wx.StaticText(panel, label="Username")
        password = wx.StaticText(panel, label="Password")
        subreddit = wx.StaticText(panel, label="Subreddit")
        filename = wx.StaticText(panel, label="Filename")
        post = wx.Button(panel, ID_POST_BUTTON, "Post")
        get = wx.Button(panel, ID_GET_BUTTON, "Get")

        global postMessage 
        postMessage = wx.StaticText(panel, label = "")


        self.tc1 = wx.TextCtrl(panel)
        self.tc2 = wx.TextCtrl(panel, style = wx.TE_PASSWORD)
        self.tc3 = wx.TextCtrl(panel)
        self.tc4 = wx.TextCtrl(panel)

        fgs.AddMany([(username), (self.tc1, 1, wx.EXPAND), (password), 
            (self.tc2, 1, wx.EXPAND), (subreddit, 1, wx.EXPAND), (self.tc3, 1, wx.EXPAND), (filename, 1, wx.EXPAND),
            (self.tc4, 1, wx.EXPAND)])

        gs.AddMany([(post,1,wx.EXPAND), (get,1,wx.EXPAND), (postMessage)])

        
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        hbox.Add(gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        #hbox.Add(postMessage, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        panel.SetSizer(hbox)

        post.Bind(wx.EVT_BUTTON, self.onClickPostItem)
        get.Bind(wx.EVT_BUTTON, self.onClickGetItem)

    def onClickPostItem(self,e):
        postItem(self.tc1.GetValue(), self.tc2.GetValue(), self.tc3.GetValue(),
            self.tc4.GetValue())  
    
    def onClickGetItem(self, e):
        getItem(self.tc1.GetValue(), self.tc2.GetValue(), self.tc3.GetValue(),
            self.tc4.GetValue())  


def postItem(username, password, subreddit, filename):
    loginMod(username,password,subreddit)
    cipher = AESCipher(KEYPASS)
    comment = cipher.encrypt_file(filename)
    post_encryption(filename, comment)
    postMessage.SetLabel("Done")

def getItem(username, password, subreddit, filename):
    loginMod(username,password,subreddit)
    cipher=AESCipher(KEYPASS)
    comment = get_decryption(filename)
    cipher.decrypt_file(comment, filename)
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
        if mod == user:
            return True
    return False 



if __name__ == '__main__':
  
    app = wx.App()
    MainWindow(None, title='subreddit')
    app.MainLoop()
