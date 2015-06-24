import sublime, sublime_plugin

# Test cases:
#
# For all tests assume the cursor is placed at the X.
#
# 1) The command should select the double quoted string
# "Here is the X cursor"
#
# 2) The command should select 'the X cursor'
# "Here is 'the X cursor' now"
#
# 3) The command should select hte outer double quotes
# "Here the cursor is 'outside' the X selection"
#
# 4) The command should select in the inner "HeXlo"
# """HeXlo"""
#
# 5) The command should select the ' X'
# "d' X' "lasd""

# view.run_command("expand_selection_to_quotes")

class ExpandToStringCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        single_quoted = self.view.find_all("'")
        double_quoted = self.view.find_all('"')

        #combine the regions of the quotes.
        def combineQuoted(qs):
            rs=[]
            prev = 0
            for later in range(1,len(qs)):
                before = qs[prev].begin() + 1
                after = qs[later].end() - 1
                if( after - before == 0):
                    # the region is empty (ie "")
                    # therefore when we select we want to have the quote marks
                    # selected
                    rs.append(sublime.Region(before-1,after+1))
                else:
                    # we don't want the quote marks also selected.
                    # therefore we use the region (befor +1, after -1)
                    rs.append(sublime.Region(before,after))

                # keep track of the previous region which holds a quote mark
                prev = later

            # Return the new array of regions
            return rs

        # determine the set of quoted regions
        quoted_regions = combineQuoted(double_quoted)
        quoted_regions.extend(combineQuoted(single_quoted))

        # we sort the quoted regions by length.
        # This ensure that when we are trying to find a match for a quoted string
        # we always get the inner most region.
        # i.e Test 2
        quoted_regions.sort(key=lambda x:x.size())


        # for each selection, find the intersecting quoted region.
        new_regions = []
        for s in self.view.sel():
            for q in quoted_regions:
                if(q.contains(s)):
                    if( q == s):
                        new_regions.append(sublime.Region(s.begin()-1, s.end() + 1))
                        break
                    else:
                        new_regions.append(q)
                        break

        # add all the regions to our selection.
        # sublime takes care of dealing with all the intersection and overlaps
        self.view.sel().add_all(new_regions)
