import sublime, sublime_plugin
import re
from collections import namedtuple
import os.path

"""
KeyMapQueryCommand allows you to quickly query if a key-binding is bound.
A combo-box will appear displayings a list of bound key-bindings. Type a key-combination
into the inptu box to narrow the results ( i.e. ctrl+k,ctrl+i ).

If there is a conflict in key-bindings,by default,the highest precendence match
is shown lower in the list.
i.e. if ctrl+o is bound in two files.
    ["ctrl+o" : command 1]
    ["ctrl+o" : command 2] <-- this is the one which actually gets used.

"""
class KeyMapQueryCommand(sublime_plugin.WindowCommand):
    """
    InternalObject holds state during the execution of the command.
    """
    class InternalObject(object):
        KeyMap  = namedtuple("KeyMap",["filename","bindings"])

        def __init__(self):
            self.keymaps = []
            self.single_array = []
            self.settings = sublime.load_settings("KeyMapQuery.sublime-settings")

        def get_key_binding(self,index):
            s = self.single_array[index]
            return s.split(":")[0]

        def get_relative_index(self,index):
            count = 0
            for d in self.keymaps:
                if count <= index < count + len(d.bindings):
                    return index - count
                else:
                    count += len(d.bindings)
            raise IndexError("Index out of range")

        # given an index from the on_select() callback
        # determine the sublime-keymap filename which it belongs to.
        def get_filename(self,index):
            count = 0
            for d in self.keymaps:
                if count <= index < count + len(d.bindings):
                    return d.filename
                else:
                    count += len(d.bindings)
            raise IndexError("Index out of range")

        # Given the keymap files we loaded in, flatten them into
        # a single array of strings to be used by the window.show_quick_panel()
        def get_string_list_of_keymaps(self):
            # flatten the keymaps into a single array contains only the keybinding object
            rs = []
            for d in self.keymaps:
                rs.extend(d.bindings)

            # convert each key-binding into a string
            # The format should look like
            # ["ctrl+i","ctrl+j"]          : command_to_be_run_1
            # ["ctrl+i","ctrl+k"]          : command_to_be_run_2
            # ["ctrl+i","ctrl+l"]          : command_to_be_run_3
            def str_format(obj):
                objs = map(lambda x: '"' + x +'"', obj["keys"])
                return "{:30s} : {}".format("["+ ",".join(objs) + "]",obj["command"])
            self.single_array = list(map(str_format,rs))
            return self.single_array

        # Load all the sublime-keymap files that are known to sublime.
        # This includes keymap files zipped inside sublime-package directories.
        def load_keymaps(self,file_re):
            # Get all the keymap filenames
            all_keymap_files = sublime.find_resources("*.sublime-keymap")
            # sort them, such as described by the merging/precedence rules defined
            # http://docs.sublimetext.info/en/latest/extensibility/packages.html?highlight=precedence
            all_keymap_files.sort()
            if self.settings.get("reverse_sort_order"):
                all_keymap_files.reverse()
            filtered_files = list(filter(lambda x : re.match(file_re,x) != None,all_keymap_files))

            # Load the keymap files; decode them into pyobjects;
            # and then convert them into KeyMap tuples
            def mapToPythonObj(filename):
                res = sublime.load_resource(filename)
                # assumption is that the decoded json is represented as
                # a python array of dictionaries.
                return self.KeyMap(filename,sublime.decode_value(res))
            self.keymaps = list(map(mapToPythonObj,filtered_files))


    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------

    def __init__(self,window):
        self.window = window
        self.file_re = self._get_keymap_regex(sublime.platform())
        self.state = None

    def run(self):
        self.state = self.InternalObject()
        self.state.load_keymaps(self.file_re)
        input_array = self.state.get_string_list_of_keymaps()

        view = self.window.show_quick_panel(
                input_array,
                flags=sublime.MONOSPACE_FONT,
                selected_index=0,
                on_select= self.on_select,
                on_highlight=None)
                # on_highlight=self.on_highlight)

    def _get_keymap_regex(self,platform):
        if( platform == "windows"):
            file_re = re.compile(r'(.*(Default \(Windows\)|Default)\.sublime-keymap)')
        elif (platform == "linux"):
            file_re = re.compile(r'(.*(Default \(Linux\)|Default)\.sublime-keymap)')
        else:
            file_re = re.compile(r'(.*(Default \(OSX\)|Default)\.sublime-keymap)')
        return file_re

    def on_highlight(self,value):
        if value == -1:
            return

    def on_select(self,value):
        if value == -1:
            return
        # open the keymap file.
        filename = self.state.get_filename(value)
        split_filename = "/".join(filename.split("/")[1:])

        # This fucking sucks. I would really like to use the sublime API open_file()
        # directly. This would get me a direct ref to the View object and allow me
        # to set the cursor to the proper position to show the hotkey binding.
        # There are a few problems with this:
        # i) sublime-packages are compresesd (zip).
        # ii) packages are stored in different folders ( pakcages, pakcage/user, etc)
        #       and they are all differnet on differenct architectures.
        # iii) Changing the sel() on a view doesn't update the cursor position
        #       on the screen. Not sure if this is a bug, but I thinkg it is
        #       becaues we aren't making edits using an Edit object. Therefore
        #       any changes that we make aren't known/shown until some user
        #       interaction
        # Because of these problems I use the following hack.
        # 1.) Open the file using the window.run_command, and use the ${packages}
        #   variables substitution.The internal sublime api automatically finds and
        #   uncompresses all the files for me. I don't have to deal with anything
        #   and the proper files gets opened (assuming it exists).
        # 2.) The pit-fall to this is that I don't get a direct ref to the View
        #   that is created/opened. This means that I can't set the cursor position.
        #   Additinally,because the run_command is async, I don't even know when
        #   the View gets fully loaded (i.e. I can't use window.active_view())
        # 3.) To get around this problem. I creat a helper TextCommand class.
        #   The purpose of this class is to positoin the cursor on the view.
        #   (i.e find_all() on a regex string). This is hacky because it pollutes
        #   the command namespace. This only solves the problem of being able to
        #   set the cursor position. I still have to use a set_timeout() in order
        #   to "ensure" the file is opened before I issue the command.
        self.window.run_command("open_file",{"file":"${packages}/"+split_filename})
        def inner():
            self.window.run_command("move_cursor_to_pattern",
                {"pattern":r'"keys"\s*:\s*\[',
                "index":self.state.get_relative_index(value)})

        # TODO: extract settings into my own class,whcih allows you to specify defaults
        delay= self.state.settings.get("timeout_delay")
        if(delay == None):
            delay = 250
        sublime.set_timeout(inner,delay)


# A Helper command used to move the cursor to the beginning/end of
# a regex pattern in the view.
class MoveCursorToPatternCommand(sublime_plugin.TextCommand):
    def run(self,edit,pattern,index=0):
        r = self.view.find_all(pattern)
        if index < 0  or index >= len(r):
            print("Pattern not found \"{}\"".format(pattern))
            return
        r = r[index]
        self.view.show_at_center(r)
        sel = self.view.sel()
        sel.clear()
        sel.add(sublime.Region(r.b,r.b))