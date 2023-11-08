# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from ....model import implements, Model, observe

from ... import IDirty, ITool


@implements(ITool)
class DirtyTool(Model):
    """ The DirtyTool is the default implementation of a :term:`tool`
    that supports the toolkit specific method of indicating that a shell has
    unsaved data.
    """

    # The tool's identifier.
    id = 'dip.shell.tools.dirty'

    @observe('shell')
    def __shell_changed(self, change):
        """ Invoked when the shell changes. """

        shell = change.old
        if shell is not None:
            observe('tools', shell, self.__tools_changed, remove=True)

            for tool in shell.tools:
                self._observe_tool(tool, remove=True)

        shell = change.new
        if shell is not None:
            for tool in shell.tools:
                self._observe_tool(tool)

            observe('tools', shell, self.__tools_changed)

    def __tools_changed(self, change):
        """ Invoked when the list of tools changes. """

        for tool in change.old:
            self._observe_tool(tool, remove=True)

        for tool in change.new:
            self._observe_tool(tool)

    def _observe_tool(self, tool, remove=False):
        """ Observe (or not) the dirty state of a tool. """

        dirty = IDirty(tool, exception=False)
        if dirty is not None:
            observe('dirty', dirty, self.__tool_dirty_changed, remove=remove)

    def __tool_dirty_changed(self, change):
        """ Invoked when a tool's dirty state changes. """

        # Handle the trivial case where the shell doesn't support the feature.
        shell_dirty = IDirty(self.shell, exception=False)
        if shell_dirty is None:
            return

        is_dirty = False

        for tool in self.shell.tools:
            dirty = IDirty(tool, exception=False)
            if dirty is not None and dirty.dirty:
                is_dirty = True
                break

        shell_dirty.dirty = is_dirty
