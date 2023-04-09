#!/usr/bin/python

# simple.py
import gc

import praw
from reddit import *
import getpass

from crypt import AESCipher
import hashlib
# import os
# from os.path import basename
import base64

from Crypto.Cipher import AES
from Crypto import Random

from redditglobals import *
import wx
from pubsub import pub

from threading import Thread, Lock, Event
from time import sleep

# cleanup dist and build directory first (for new py2exe version) 
# if os.path.exists("dist/prog"):
#   shutil.rmtree("dist/prog")

# if os.path.exists("dist/lib"):
#   shutil.rmtree("dist/lib")

# if os.path.exists("build"):
#   shutil.rmtree("build")

wildcard = "All files (*.*)|*.*"


# noinspection PyAttributeOutsideInit
class RedditList(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Files Stored", size=(300, 400))
        self.panel = wx.Panel(self)
        pub.subscribe(self.subreddit_listener, "subredditListener")
        self._init_UI()

    def _init_UI(self):
        self.fileList = wx.ListCtrl(self.panel, size=(-1, 300), style=wx.LC_REPORT
                                                                      | wx.EXPAND)
        self.fileList.InsertColumn(0, "File Name", width=500)

        self.gs = wx.GridSizer(1, 2, 0, 0)

        submit_button = wx.Button(self.panel, label="Submit")
        submit_button.Bind(wx.EVT_BUTTON, self.onSubmit)
        close_button = wx.Button(self.panel, label="Close")
        close_button.Bind(wx.EVT_BUTTON, self.onClose)

        save_button = wx.Button(self.panel, label="Save Fields")

        generate_button = wx.Button(self.panel, label="Generate Subreddit")

        self.gs.Add(submit_button)
        self.gs.Add(close_button)

        sizer = wx.BoxSizer(wx.VERTICAL)
        flags = wx.ALL | wx.EXPAND
        sizer.Add(self.fileList, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.gs, flag=wx.ALIGN_BOTTOM | wx.EXPAND | wx.ALL, border=5)
        self.panel.SetSizer(sizer)

    # Used by onClickGetRedditList
    def subreddit_listener(self, subreddit_name, username, password):
        reddit = praw.Reddit("reddit storage bot")
        subreddit = reddit.subreddit(subreddit_name)
        global posts
        posts = subreddit.get_new(limit=1000)
        index = 0
        self.myRowDict = {}  # dictionary used for retrival later
        for x in posts:
            print(str(x))
            self.fileList.InsertStringItem(index, x.title)
            self.myRowDict[index] = x.title
            index += 1
        print("done")

    def onClose(self, event):
        self.Close()

    def onSubmit(self, event):
        pub.sendMessage("fileListener", fileName=self.myRowDict[get_selected_items(self.fileList)[0]])
        self.Close()


def get_selected_items(list_control):
    # Gets the selected items for the list control.
    # Selection is returned as a list of selected indices,
    # low to high.

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
    # Returns next selected item, or -1 when no more

    return list_control.GetNextItem(current,
                                    wx.LIST_NEXT_ALL,
                                    wx.LIST_STATE_SELECTED)


# noinspection PyPep8Naming,PyRedundantParentheses
class PostPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.InitUI()

    # noinspection PyAttributeOutsideInit
    def InitUI(self):
        ID_POST_BUTTON = wx.NewIdRef(count=1)
        ID_BROWSE_FILE_BUTTON = wx.NewIdRef(count=1)

        hit_box = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(5, 2, 9, 15)
        gs = wx.GridSizer(2, 2, 9, 10)

        global username
        # username = wx.StaticText(self, label="Username")
        # password = wx.StaticText(self, label="Password")
        # subreddit = wx.StaticText(self, label="Subreddit")
        KEY_PASS = wx.StaticText(self, label="Encryption key")
        filename = wx.StaticText(self, label="Filepath")
        post = wx.Button(self, ID_POST_BUTTON, "Post")
        browseFile = wx.Button(self, ID_BROWSE_FILE_BUTTON, "Browse File")
        global postMessage
        postMessage = wx.StaticText(self, label="")

        # self.usernameField = wx.TextCtrl(self)
        # self.passwordField = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        # self.subredditField = wx.TextCtrl(self)
        self.keypassField = wx.TextCtrl(self)
        self.filepathField = wx.TextCtrl(self)

        fgs.AddMany([  # (username), (self.usernameField, 1, wx.EXPAND), (password),(self.passwordField, 1, wx.EXPAND),
            # (subreddit, 1, wx.EXPAND), (self.subredditField, 1, wx.EXPAND),
            (KEY_PASS, 1, wx.EXPAND), (self.keypassField, 1, wx.EXPAND), (filename, 1, wx.EXPAND),
            (self.filepathField, 1, wx.EXPAND)])

        gs.AddMany([(post, 1, wx.EXPAND), (browseFile, 1, wx.EXPAND), (postMessage)])

        fgs.AddGrowableCol(1, 1)

        hit_box.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        hit_box.Add(gs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        # hit_box.Add(postMessage, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(hit_box)

        post.Bind(wx.EVT_BUTTON, self.onClickPostItem, post)
        browseFile.Bind(wx.EVT_BUTTON, self.onClickBrowseFile, browseFile)

    def onClickBrowseFile(self, e):
        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easily
        # be changed in your program. This is an 'open' dialog, and allows multiple
        # file selections as well.
        #
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
        )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # Use GetPaths() for multiple files
            paths = dlg.GetPaths()
            self.filepathField.SetValue(paths[0])

            # self.log.WriteText('You selected %d files:' % len(paths))

            # for path in paths:
            #   self.log.WriteText('           %s\n' % path)

        # Compare this with the debug above; did we change working dirs?
        # self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

    def onClickPostItem(self, e):
        # if (self.usernameField.IsEmpty()):
        #     postMessage.SetLabel("No Username Specified")
        # elif (self.passwordField.IsEmpty()):
        #     postMessage.SetLabel("No Password Entered")
        # elif (self.subredditField.IsEmpty()):
        #     postMessage.SetLabel("No Subreddit Specified")
        if (self.keypassField.IsEmpty()):
            postMessage.SetLabel("No Encryption Key Specified")
        elif (self.filepathField.IsEmpty()):
            postMessage.SetLabel("No Filepath Specified")
        else:
            postItem(  # self.usernameField.GetValue(), self.passwordField.GetValue(), self.subredditField.GetValue(),
                self.filepathField.GetValue(), self.keypassField.GetValue())


# noinspection PyPep8Naming,PyRedundantParentheses
class GetPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        pub.subscribe(self.fileListener, "fileListener")
        self.InitUI()

    def fileListener(self, fileName):
        self.fileToGetField.SetValue(fileName)

    # noinspection PyAttributeOutsideInit
    def InitUI(self):
        ID_GET_BUTTON = wx.NewIdRef(count=1)
        ID_SAVE_FILE_BUTTON = wx.NewIdRef(count=1)
        ID_GET_REDDIT_LIST_BUTTON = wx.NewIdRef(count=1)

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(6, 2, 9, 15)
        gs = wx.GridSizer(2, 2, 9, 10)

        global username
        # username = wx.StaticText(self, label="Username")
        # password = wx.StaticText(self, label="Password")
        # subreddit = wx.StaticText(self, label="Subreddit")
        file_to_get = wx.StaticText(self, label="File to get")
        KEYPASS = wx.StaticText(self, label="Encryption key")
        filename = wx.StaticText(self, label="Filepath")
        get = wx.Button(self, ID_GET_BUTTON, "Get")
        saveFile = wx.Button(self, ID_SAVE_FILE_BUTTON, "Save File As")
        getRedditList = wx.Button(self, ID_GET_REDDIT_LIST_BUTTON, "Retrieve List of Stored Files ")

        global postMessage1
        postMessage1 = wx.StaticText(self, label="")

        # self.usernameField = wx.TextCtrl(self)
        # self.passwordField = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        # self.subredditField = wx.TextCtrl(self)
        self.fileToGetField = wx.TextCtrl(self)
        self.keypassField = wx.TextCtrl(self)
        self.filepathField = wx.TextCtrl(self)

        fgs.AddMany([
            # (subreddit, 1, wx.EXPAND), (self.subredditField, 1, wx.EXPAND),
            (file_to_get, 1, wx.EXPAND), (self.fileToGetField, 1, wx.EXPAND), (KEYPASS, 1, wx.EXPAND),
            (self.keypassField, 1, wx.EXPAND), (filename, 1, wx.EXPAND), (self.filepathField, 1, wx.EXPAND)])

        gs.AddMany([(get, 1, wx.EXPAND), (saveFile, 1, wx.EXPAND), (getRedditList, 1, wx.EXPAND), (postMessage1)])

        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        hbox.Add(gs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

        self.SetSizer(hbox)

        get.Bind(wx.EVT_BUTTON, self.onClickGetItem)
        saveFile.Bind(wx.EVT_BUTTON, self.onClickSaveItem)
        getRedditList.Bind(wx.EVT_BUTTON, self.onClickGetRedditList)

    # noinspection PyUnusedLocal
    def onClickSaveItem(self, e):
        # self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'save' dialog.
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.FD_SAVE,
        )

        # For legacy support; files used to be uploaded with the whole pathname
        # (or did before I changed the upload names)
        temp_fn = os.path.basename(self.fileToGetField.GetValue())
        dlg.SetFilename(temp_fn)
        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.filepathField.SetValue(path)
        # todo: what does this comment block imply?
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
        # self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def onClickGetItem(self, e):
        # if (self.usernameField.IsEmpty()):
        #     postMessage1.SetLabel("No Username Specified")
        # elif (self.passwordField.IsEmpty()):
        #     postMessage1.SetLabel("No Password Entered")
        # elif (self.subredditField.IsEmpty()):
        #     postMessage1.SetLabel("No Subreddit Specified")
        if (self.fileToGetField.IsEmpty()):
            postMessage1.SetLabel("No File Specified")
        elif (self.keypassField.IsEmpty()):
            postMessage1.SetLabel("No Encryption Key Specified")
        elif (self.filepathField.IsEmpty()):
            postMessage1.SetLabel("No Filepath Specified")
        else:
            getItem(  # self.subredditField.GetValue(),
                self.filepathField.GetValue(), self.fileToGetField.GetValue(), self.keypassField.GetValue())

    # noinspection PyUnusedLocal
    def onClickGetRedditList(self, e):
        if self.subredditField.IsEmpty():
            postMessage1.SetLabel("No Subreddit Specified")
        else:
            print(self.subredditField.GetValue())
            frame = RedditList()
            pub.sendMessage("subredditListener", subredditName=self.subredditField.GetValue())
            frame.Show()


class MainNotebook(wx.Notebook):

    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
        wx.BK_DEFAULT
                             # wx.BK_TOP
                             # wx.BK_BOTTOM
                             # wx.BK_LEFT
                             # wx.BK_RIGHT
                             )

        self.InitUI()

    def InitUI(self):
        tab_one = PostPanel(self)
        self.AddPage(tab_one, "Post")

        tab_two = GetPanel(self)
        self.AddPage(tab_two, "Get")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()


class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(500, 375))

        panel = wx.Panel(self)

        notebook = MainNotebook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)

        self.Layout()
        self.Centre()
        self.Show()


# ------------------------------------------------------------------------------


# noinspection PyUnusedLocal,PyPep8Naming
def postItem(filename: str, KEYPASS: str):
    filepath = filename
    k = filename.rfind("/")
    filename = filename[k + 1:]
    del k
    gc.collect()
    # loginMod(username, password, subreddit)
    cipher = AESCipher(KEYPASS)
    encrypt_items = cipher.encrypt_file(filepath)
    b64ciphertext = b64encode(encrypt_items[0])
    b64mac = b64encode(encrypt_items[1])
    b64nonce = b64encode(encrypt_items[2])
    del encrypt_items
    gc.collect()
    post_encryption(filename, b64ciphertext, b64mac, cipher.salt, b64nonce, cipher.argon2params)
    postMessage.SetLabel("Done")    # Todo: these labels need to disappear after some time
    postMessage1.SetLabel("Done")


# noinspection PyUnusedLocal,PyPep8Naming
def getItem(save_location, file_to_get, ENCRYPT_KEY):
    filepath = save_location
    # k = filename.rfind("/")
    # filename = filename[k+1:]
    # filepath = filepath[:k+1]
    # temp_fp = filepath
    # filepath = filepath + file_to_get

    # loginMod(username, password, subreddit)
    cipher = AESCipher(ENCRYPT_KEY)
    encrypt_items = get_ciphertext(file_to_get)
    cipher.decrypt_to_file(encrypt_items, filepath)
    del encrypt_items
    gc.collect()
    postMessage1.SetLabel("Done")
    postMessage.SetLabel("Done")


def StartApp():
    app = wx.App()
    MainWindow(None, title='subreddit')
    app.MainLoop()


if __name__ == '__main__':
    StartApp()
