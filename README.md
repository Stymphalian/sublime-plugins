Author: Jordan Yu  
Date: May 16th, 2015  

#Purpose:
This repository holds various sublime plugins that I created to patch-up pain points in my daily sublime usage. Most of this stuff is brutally brittle as I only intend for it to work on my system and with only my current version of Sublime. I try to document my code as much as I can so that if anybody does stumble-upon it, they atleast have some chance modifying it for themselves.

#Plugins List
##KeyMapQuery
Plugin which allows you to quickly check if key-binding is currently being 
used in sublime.A combo-box will appear displayings a list of bound key-
bindings. Type a key-combination into the inptu box to narrow the results
( i.e. ctrl+k,ctrl+i ).If there is a conflict in key-bindings,by default,
the highest precendence match is shown lower in the list.  

    For Example:
    if ctrl+o is bound in two files.
    ["ctrl+o" : command 1]
    ["ctrl+o" : command 2] <-- this is the one which actually gets used.

![Screenshot of KeyMapQuery plugin.](screenshots/KeyMapQuery_1.png "KeyMapQuery")

##GetTheScope
Plugin which shows a popup of the _scope_ string of the currently selected text.This is to make it easier to develop plugins which require _contexts_ in the command.

![Screenshot of GetTheScope plugin.](screenshots/GetTheScope_1.png "GetTheScope")

##Misc
###RenameCurrentView 
    hotkey command to rename the currently opened view.

