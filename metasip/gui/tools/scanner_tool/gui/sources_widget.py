# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem

from .....project import HeaderDirectory, HeaderFile


class SourcesWidget(QTreeWidget):
    """ This class is a widget that implements a browser of the header files of
    a source directory.
    """

    # The column numbers.
    (NAME, STATUS) = range(2)

    def __init__(self, tool):
        """ Initialise the widget. """

        super().__init__()

        self._tool = tool

        self._root_item = None
        self.working_version = None

        self.setHeaderLabels(("Name", "Status"))

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.currentItemChanged.connect(self._handle_selection_change)

    # TODO
    def hide_ignored(self, header_directory, hide):
        """ Show or hide all the ignored files in a header directory. """

        for itm in self._items():
            if itm.project_item is header_directory:
                for hfile_idx in range(itm.childCount()):
                    hfile_itm = itm.child(hfile_idx)

                    if hfile_itm.get_working_file() is not None and hfile_itm.text(SourcesWidget.STATUS) == "Ignored":
                        hfile_itm.setHidden(hide)

                break

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('header')
        if state is not None:
            self.header().restoreState(state)

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('header', self.header().saveState())

    def set_project(self):
        """ Set the current project. """

        self.clear()

        for hdir in self._tool.shell.project.headers:
            _HeaderDirectoryItem(hdir, self)

        self.sortItems(SourcesWidget.NAME, Qt.SortOrder.AscendingOrder)

    def set_working_version(self, working_version):
        """ Set the current working version. """

        self.working_version = working_version

        for itm in self._items():
            itm.set_working_version(working_version)

    def _handle_selection_change(self, current, previous):
        """ Invoked when the item selection changes. """

        project_item = current.project_item

        header_directory = None
        header_file = None

        if isinstance(project_item, HeaderDirectory):
            header_directory = project_item
        elif isinstance(project_item, HeaderFile):
            header_directory = current.parent().project_item
            header_file = project_item

        self._tool.set_header_file(header_file, header_directory)

    def _items(self, root=None):
        """ A generator for all the header items depth first. """

        if root is None:
            root = self.invisibleRootItem()

        for i in range(root.childCount()):
            child = root.child(i)

            for itm in self._items(child):
                yield itm

            yield child


class _SourcesItem(QTreeWidgetItem):
    """ This is a base class for all items in the sources tree. """

    def __init__(self, project_item, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self.project_item = project_item

    def set_working_version(self, working_version):
        """ Set the current working versions. """

        # This default implementation does nothing.
        pass


class _HeaderDirectoryItem(_SourcesItem):
    """ This class represents a header directory in the sources tree. """

    def __init__(self, header_directory, parent):
        """ Initialise the item. """

        super().__init__(header_directory, parent)

        self.setText(SourcesWidget.NAME, header_directory.name)

        for header_file in header_directory.content:
            _HeaderFileItem(header_file, self)

        self.sortChildren(SourcesWidget.NAME, Qt.SortOrder.AscendingOrder)

    def set_working_version(self, working_version):
        """ Set the current working version. """

        # Draw the status column.
        if working_version is None:
            needs_scanning = (len(self.project_item.scan) != 0)
        else:
            needs_scanning = (working_version in self.project_item.scan)

        self.setText(SourcesWidget.STATUS,
                "Needs scanning" if needs_scanning else '')


class _HeaderFileItem(_SourcesItem):
    """ This class represents a header file in the sources tree. """

    def __init__(self, header_file, parent):
        """ Initialise the item. """

        super().__init__(header_file, parent)

        self.setText(SourcesWidget.NAME, header_file.name)

    def get_working_file(self):
        """ Get the version of the header file corresponding to the working
        version, if there is one.
        """

        working_version = self.treeWidget().working_version
        hfile_versions = self.project_item.versions

        if working_version is None:
            working_file = None if len(hfile_versions) == 0 else hfile_versions[0]
        else:
            for working_file in hfile_versions:
                if working_file.version == working_version:
                    break
            else:
                working_file = None

        return working_file

    def set_working_version(self, working_version):
        """ Set the current working version. """

        self._draw_status()

    def _draw_status(self):
        """ Draw the status column. """

        # Get the working version of the file, if any.
        working_file = self.get_working_file()

        self.setHidden(working_file is None)

        # Determine the status.
        expand = False

        if self.project_item.ignored:
            status = "Ignored"
            self.setHidden(True)
        elif len(self.project_item.versions) == 0:
            # This happens when all the versions containing this header file
            # have been deleted.
            status = "Unused"
            expand = True
            self.setHidden(False)
        elif self.project_item.module == '':
            status = "Needs assigning"
            expand = True
        elif working_file is not None and working_file.parse:
            status = "Needs parsing"
            expand = True
        else:
            status = ''

        self.setText(SourcesWidget.STATUS, status)

        if expand:
            self.parent().setExpanded(True)

    # TODO
    def __on_ignored_changed(self, change):
        """ Invoked when a header file's ignored state changes. """

        self._draw_status()

    # TODO
    def __on_module_changed(self, change):
        """ Invoked when a header file's assigned module changes. """

        self._draw_status()

    # TODO
    def __on_versions_changed(self, change):
        """ Invoked when a header file's list of versions changes. """

        #for hfile_version in change.old:
        #    observe('parse', hfile_version, self.__on_parse_changed,
        #            remove=True)

        #for hfile_version in change.new:
        #    observe('parse', hfile_version, self.__on_parse_changed)

        self._draw_status()

    # TODO
    def __on_parse_changed(self, change):
        """ Invoked when a header file version's parse state changes. """

        self._draw_status()
