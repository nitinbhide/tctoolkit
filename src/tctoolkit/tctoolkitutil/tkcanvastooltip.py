'''
Tooltips for Tk Canvas object.
When you hover on a object draw on the Canvas, tooltip will be display.
Tooltip uses the text in the 'tooltip' tag. Format of tooltip 'tooltip:<string>'

Based on recipe http://code.activestate.com/recipes/576688/

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

from Tkinter import Toplevel, Message, StringVar
from time import time
import string


class TkCanvasToolTip(Toplevel):

    """
    Provides a ToolTip widget for Tkinter.
    To apply a ToolTip to any Tkinter widget, simply pass the widget to the
    ToolTip constructor
    """

    def __init__(self, wdgt, delay=1, follow=True):
        """
        Initialize the ToolTip

        Arguments:
          wdgt: The widget this ToolTip is assigned to
          msg:  A static string message assigned to the ToolTip
          msgFunc: A function that retrieves a string to use as the ToolTip text
          delay:   The delay in seconds before the ToolTip appears(may be float)
          follow:  If True, the ToolTip follows motion, otherwise hides
        """
        self.wdgt = wdgt
        # The parent of the ToolTip is the parent of the ToolTips widget
        self.parent = self.wdgt.master
        # Initalise the Toplevel
        Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)
        # Hide initially
        self.withdraw()
        # The ToolTip Toplevel should have no frame or title bar
        self.overrideredirect(True)

        # The msgVar will contain the text displayed by the ToolTip
        self.msgVar = StringVar()
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        Message(self, textvariable=self.msgVar, bg='#FFFFDD',
                aspect=1000).grid()                                           # The test of the ToolTip is displayed in a Message widget
# self.wdgt.bind( '<Enter>', self.spawn, '+' )                            # Add bindings to the widget.  This will NOT override bindings that the widget already has
##        self.wdgt.bind( '<Leave>', self.hide, '+' )
##        self.wdgt.bind( '<Motion>', self.move, '+' )

    def updatebindings(self):
        objids = self.wdgt.find_all()
        for objid in objids:
            tags = self.wdgt.gettags(objid)
            for tag in tags:
                if(tag.startswith('tooltip:')):
                    self.wdgt.tag_bind(
                        objid, '<Enter>', lambda e, id=objid: self.spawn(e, id), '+')
                    self.wdgt.tag_bind(objid, '<Leave>', self.hide, '+')
                    self.wdgt.tag_bind(objid, '<Motion>', self.move, '+')

    def getmsg(self, objid):
        # get the message from objects on canvas
        msg = ''
        tags = self.wdgt.gettags(objid)
        for tag in tags:
            if(tag.startswith('tooltip:')):
                msg = tag[len('tooltip:'):]

        return(msg)

    def spawn(self, event=None, objid=None):
        """
        Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
        Usually this is caused by entering the widget

        Arguments:
          event: The event that called this funciton
        """
        self.visible = 1
        # The after function takes a time argument in miliseconds
        self.after(int(self.delay * 1000), self.show)
        try:
            msg = self.getmsg(objid)
            # Try to call the message function.  Will not change the message if
            # the message function is None or the message function fails
            self.msgVar.set(msg)
        except Exception, expinst:
            print expinst
            pass

    def show(self):
        """
        Displays the ToolTip if the time delay has been long enough
        """

        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        """
        Processes motion within the widget.

        Arguments:
          event: The event that called this function
        """
        self.lastMotion = time()
        # If the follow flag is not set, motion within the widget will make the
        # ToolTip dissapear
        if self.follow == False:
            self.withdraw()
            self.visible = 1
        # Offset the ToolTip 10x10 pixes southwest of the pointer
        self.geometry('+%i+%i' % (event.x_root + 10, event.y_root + 10))

        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """
        Hides the ToolTip.  Usually this is caused by leaving the widget

        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()
