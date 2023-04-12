#!/usr/bin/python

from typing import Union

from reddit import *

from crypt import AESCipher

from redditglobals import *
import wx
from pubsub import pub

from threading import Thread, Lock, Event
from time import sleep

wildcard = "All files (*.*)|*.*"


# noinspection PyAttributeOutsideInit
class RedditList(wx.Frame):
    """
    A window showing the list of files posted to Reddit. Listens to the subredditListener pub.
    """

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Files Stored", size=(300, 400))
        self.panel = wx.Panel(self)
        pub.subscribe(self.subreddit_listener, "subredditListener")
        self._init_UI()

    def _init_UI(self):
        """
        Initializes the UI of the window
        """
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

        sizer.Add(self.gs, flag=wx.EXPAND | wx.ALL, border=5)
        self.panel.SetSizer(sizer)

    # Used by onClickGetRedditList
    def subreddit_listener(self, subreddit_name: str):
        """
        Subscribed to subredditListener event. Fetches posts on the subreddit
        :param subreddit_name:
        """
        print("Fetching posts...\n")
        sub = REDDIT.subreddit(subreddit_name)
        global posts
        posts = sub.new(limit=1000)
        self.myRowDict = {}  # dictionary used for retrival later
        for x in posts:
            print(str(x))
            index = self.fileList.InsertItem(x.title)
            self.myRowDict[index] = x.title
        print("Done fetching list of posts\n")

    # Closes window
    def onClose(self, event):
        self.Close()

    # When user presses submit button in the new window
    def onSubmit(self, event):
        pub.sendMessage("fileListener", fileName=self.myRowDict[get_selected_items(self.fileList)[0]])
        self.Close()


def get_selected_items(list_control: wx.ListCtrl):
    """
    Gets the selected items for the list control.
    Selection is returned as a list of selected indices,
    low to high.
    :param list_control: The list control to retrieve all selected items from
    """

    selection = []

    # start at index -1 to get the first selected item
    current = -1
    while True:
        selectedItem = GetNextSelected(list_control, current)
        if selectedItem == -1:
            return selection

        selection.append(selectedItem)
        current = selectedItem


def GetNextSelected(list_control: wx.ListCtrl, current_index: int):
    """
    Retrieves the next selected item in the list control
    :param list_control: The list control to retrieve an item from
    :param current_index: Current index to retrieve on. -1 retrieves the first item
    :return: The first selected item after current_index, or -1 if no item is found
    """

    return list_control.GetNextItem(current_index,
                                    wx.LIST_NEXT_ALL,
                                    wx.LIST_STATE_SELECTED)


# noinspection PyPep8Naming,PyRedundantParentheses
class PostPanel(wx.Panel):
    """
    This is the panel where files can be posted.
    The window switches to this panel when pressing the "Post" tab.
    """

    def __init__(self, parent: Union[wx.Window, None] = None):
        """
        Initializes the 'Post' panel
        :param parent: The parent process of the panel; optional
        """
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.InitUI()

    # noinspection PyAttributeOutsideInit
    def InitUI(self):
        """
        Initializes the panel elements
        """
        ID_POST_BUTTON = wx.NewIdRef(count=1)
        ID_BROWSE_FILE_BUTTON = wx.NewIdRef(count=1)

        hit_box = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(5, 2, 9, 15)
        gs = wx.GridSizer(2, 2, 9, 10)

        KEY_PASS = wx.StaticText(self, label="Encryption key")
        filename = wx.StaticText(self, label="Filepath")
        post = wx.Button(self, ID_POST_BUTTON, "Post")
        browseFile = wx.Button(self, ID_BROWSE_FILE_BUTTON, "Browse File")

        global postMessage
        """Refers to the message to say posting is done."""
        postMessage = wx.StaticText(self, label="")

        self.passwordField = wx.TextCtrl(self)
        self.filepathField = wx.TextCtrl(self)

        fgs.AddMany([(KEY_PASS, 1, wx.EXPAND), (self.passwordField, 1, wx.EXPAND), (filename, 1, wx.EXPAND),
                     (self.filepathField, 1, wx.EXPAND)])

        gs.AddMany([(post, 1, wx.EXPAND), (browseFile, 1, wx.EXPAND), (postMessage)])

        fgs.AddGrowableCol(1, 1)

        hit_box.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        hit_box.Add(gs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.SetSizer(hit_box)

        post.Bind(wx.EVT_BUTTON, self.onClickPostItem, post)
        browseFile.Bind(wx.EVT_BUTTON, self.onClickBrowseFile, browseFile)

    def onClickBrowseFile(self, e):
        """Create the dialog. In this case the current directory is forced as the starting
        directory for the dialog, and no default file name is forced. This can easily
        be changed in your program. This is an 'open' dialog, and allows multiple
        file selections as well.

        Finally, if the directory is changed in the process of getting files, this
        dialog is set up to change the current working directory to the path chosen.
        """
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
            paths = dlg.GetPaths()  # Todo: allow user to select and post multiple files
            self.filepathField.SetValue(paths[0])

        dlg.Destroy()

    def onClickPostItem(self, e):
        """Executes when user clicks the 'Post' button"""
        if (self.passwordField.IsEmpty()):
            postMessage.SetLabel("No Encryption Key Specified")
        elif (self.filepathField.IsEmpty()):
            postMessage.SetLabel("No Filepath Specified")
        else:
            postItem(  # self.usernameField.GetValue(), self.passwordField.GetValue(), self.subredditField.GetValue(),
                self.filepathField.GetValue(), self.passwordField.GetValue())


# noinspection PyPep8Naming,PyRedundantParentheses
class GetPanel(wx.Panel):
    """
    This is the panel where files can be retrieved.
    The window switches to this panel when pressing the "Get" tab.
    """

    def __init__(self, parent: Union[wx.Window, None] = None):
        """
        Initializes the 'Get' panel
        :param parent: The parent process of the panel
        """
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        pub.subscribe(self.fileListener, "fileListener")
        self.InitUI()

    def fileListener(self, fileName):
        """Sets the value in the 'Filepath' field.
        Subscribed to 'fileListener' event"""
        self.fileToGetField.SetValue(fileName)

    # noinspection PyAttributeOutsideInit
    def InitUI(self):
        """Initializes the UI for the panel"""
        ID_GET_BUTTON = wx.NewIdRef(count=1)
        ID_SAVE_FILE_BUTTON = wx.NewIdRef(count=1)
        ID_GET_REDDIT_LIST_BUTTON = wx.NewIdRef(count=1)

        hbox = wx.BoxSizer(wx.VERTICAL)

        fgs = wx.FlexGridSizer(6, 2, 9, 15)
        gs = wx.GridSizer(2, 2, 9, 10)

        file_to_get = wx.StaticText(self, label="File to get")
        KEYPASS = wx.StaticText(self, label="Encryption key")
        filename = wx.StaticText(self, label="Filepath")
        get = wx.Button(self, ID_GET_BUTTON, "Get")
        saveFile = wx.Button(self, ID_SAVE_FILE_BUTTON, "Save File As")
        getRedditList = wx.Button(self, ID_GET_REDDIT_LIST_BUTTON, "Retrieve List of Stored Files ")

        global postMessage1
        postMessage1 = wx.StaticText(self, label="")

        self.fileToGetField = wx.TextCtrl(self)
        self.keypassField = wx.TextCtrl(self)
        self.filepathField = wx.TextCtrl(self)

        fgs.AddMany([(file_to_get, 1, wx.EXPAND), (self.fileToGetField, 1, wx.EXPAND), (KEYPASS, 1, wx.EXPAND),
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
        """Opens a file dialog window so users can choose where to save the file.
        Called when user clicks the 'Save File As' button
        """
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
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def onClickGetItem(self, e):
        """
        Gets the file from the specified Reddit post and downloads to specified file path.
        Activated when the 'Get' button is clicked
        """
        if (self.fileToGetField.IsEmpty()):
            postMessage1.SetLabel("No File Specified")
        elif (self.keypassField.IsEmpty()):
            postMessage1.SetLabel("No Encryption Key Specified")
        elif (self.filepathField.IsEmpty()):
            postMessage1.SetLabel("No Filepath Specified")
        else:
            getItem(  # self.subredditField.GetValue(),
                self.filepathField.GetValue(), self.fileToGetField.GetValue(), self.keypassField.GetValue())

    @staticmethod
    def onClickGetRedditList(e):
        """
        Shows a list of files in a separate window posted to the subreddit.
        """
        frame = RedditList()
        pub.sendMessage("subredditListener", subreddit_name=SUBREDDIT)
        frame.Show()


class MainNotebook(wx.Notebook):

    def __init__(self, parent: Union[wx.Window, None] = None):
        """
        Constructs a notebook.
        :param parent: The parent window of the notebook.
        """
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        self.InitUI()

    def InitUI(self):
        """Initializes the UI for the notbook"""
        tab_one = PostPanel(self)
        self.AddPage(tab_one, "Post")

        tab_two = GetPanel(self)
        self.AddPage(tab_two, "Get")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        """Event for when tab is finished changing"""
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        """Event for when tab is about to change"""
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()


class MainWindow(wx.Frame):

    def __init__(self, parent, title: str):
        """
        Creates a wxPython window.
        :param parent: The parent process for this window
        :param title: The title of the window. Process will show up in things such as Task Manager or 'ps' with this name
        """
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
def postItem(filename: str, PASSKEY: str):
    """
    Encrypts and then posts a file to Reddit
    :param filename: The title of the post to be created
    :param PASSKEY: The password used to generate the encryption key
    """
    filepath = filename
    k = filename.rfind("/")
    filename = filename[k + 1:]
    del k
    gc.collect()
    # loginMod(username, password, subreddit)
    cipher = AESCipher(PASSKEY)
    encrypt_items = cipher.encrypt_file(filepath)
    b64ciphertext = b64encode(encrypt_items[0])
    b64mac = b64encode(encrypt_items[1])
    b64nonce = b64encode(encrypt_items[2])
    del encrypt_items
    gc.collect()
    post_encryption(filename, b64ciphertext, b64mac, cipher.salt, b64nonce, cipher.argon2params)
    postMessage.SetLabel("Done")  # Todo: these labels need to disappear after some time
    postMessage1.SetLabel("Done")


# noinspection PyUnusedLocal,PyPep8Naming
def getItem(save_location: str, file_to_get: str, PASSKEY: Union[str, bytes]):
    """
    Gets an encrypted file from Reddit
    :param save_location: The location to save the file at
    :param file_to_get: The name of the file to get. This should be the same as the post title on Reddit
    :param PASSKEY: The password used to generate the encryption key.
    """
    filepath = save_location
    cipher = AESCipher(PASSKEY)
    encrypt_items = get_ciphertext(file_to_get)
    cipher.decrypt_to_file(encrypt_items, filepath)
    del encrypt_items
    gc.collect()
    postMessage1.SetLabel("Done")
    postMessage.SetLabel("Done")


def StartApp():
    """
    Starts the app UI. Does not execute in a separate thread. Code after this function will only execute after
    the window is closed.
    """
    app = wx.App()
    MainWindow(None, title='subreddit')
    app.MainLoop()


if __name__ == '__main__':
    StartApp()
