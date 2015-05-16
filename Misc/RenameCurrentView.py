import sublime, sublime_plugin

# Command to 'rename' the current file
# Uses the RenamePathCommand implemented by the Sidebar.
class RenameCurrentViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        p = self.view.file_name()
        if p != None :
            self.view.window().run_command("rename_path",{"paths":[p]})
