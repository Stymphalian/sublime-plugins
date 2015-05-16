"""
Shows the scope-string for the current cursor position.
Reveals a pop-up with the scope-string
Clicking on the string/link copies the text into your clipboard.
Additionally,it will outline the region that is captured by the scope.

Compatibility:
Only Sublime 3. We use the view.show_popup() command.
"""
import sublime, sublime_plugin

class GetTheScopeCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # Get the points from the selected regions.
        points = list(map(lambda x:(min(x.a,x.b)),self.view.sel()))
        # only get the scope of the first selected region
        point = self.view.extract_scope(points[0]).a
        # retrieve the scope string
        content = self.view.scope_name(point)

        # 'Outline the region which this scope belongs to
        self.region_key = "scope_region"
        self.view.erase_regions(self.region_key)
        r = self.view.extract_scope(points[0])
        self.view.add_regions(self.region_key,[r],
            flags=sublime.DRAW_NO_FILL,
            scope="comment",
            icon="")

        # show a pop-up holding to display the scope-string
        self.view.show_popup(
            '<a href="copy" style="font-size:10">'+content+'</a>',
            flags=sublime.HTML,
            # begin at the beginning of the cursor
            location=points[0],
            # Size the pop-up based on the current viewport extent
            max_width=self.view.viewport_extent()[0],
            max_height=self.view.viewport_extent()[1],
            # clicking on the link, copies the content into your clipboard
            on_navigate=self.on_navigate(content),
            # hide the pop-up + erase the region
            on_hide=self.on_hide
        )

    def on_hide(self):
        # self.view.hide_popup()
        self.view.erase_regions(self.region_key)

    def on_navigate(self,data):
        def inner(href):
            sublime.set_clipboard(data)
            self.view.hide_popup()
            self.on_hide()
        return inner