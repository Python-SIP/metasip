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

        self.setHeaderLabels(("Name", "Status"))

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.currentItemChanged.connect(self._handle_selection_change)

    def header_directory_added(self, header_directory, working_version):
        """ A header directory has been added. """

        header_directory_item = _HeaderDirectoryItem(header_directory, self)
        header_directory_item.set_working_version(working_version)
        self._sort_header_directories()

    def header_directory_removed(self, header_directory):
        """ A header directory has been removed. """

        header_directory_item = self._find_header_directory_item(
                header_directory)
        self.takeTopLevelItem(self.indexOfTopLevelItem(header_directory_item))

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('header')
        if state is not None:
            self.header().restoreState(state)

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('header', self.header().saveState())

    def set_header_directories_state(self):
        """ Set the state of all header directories. """

        for header_directory_item in self._header_directory_items():
            header_directory_item.set_status()

    def set_header_file_state(self, header_file):
        """ Set the state of a header file. """

        for header_directory_item in self._header_file_directories():
            for header_file_item in self._header_file_items(header_directory_item):
                if header_file_item.project_item is header_file:
                    header_file_item.set_status()
                    return

    def set_header_files_visibility(self, header_directory, showing_ignored):
        """ Show or hide all the ignored files in a header directory. """

        header_directory_item = self._find_header_directory_item(
                header_directory)

        header_directory_item.showing_ignored = showing_ignored

        for header_file_item in self._header_file_items(header_directory_item):
            if header_file_item.project_item.ignored:
                header_file_item.setHidden(not showing_ignored)

    def set_project(self):
        """ Set the current project. """

        self.clear()

        for header_directory in self._tool.shell.project.headers:
            _HeaderDirectoryItem(header_directory, self)

        self._sort_header_directories()

    def set_working_version(self, working_version):
        """ Set the current working version. """

        for header_directory_item in self._header_directory_items():
            header_directory_item.set_working_version(working_version)

            for header_file_item in self._header_file_items(header_directory_item):
                header_file_item.set_working_version(working_version)

    def _find_header_directory_item(self, header_directory):
        """ Return the header directory item for a header directory. """

        for header_directory_item in self._header_directory_items():
            if header_directory_item.project_item is header_directory:
                return header_directory_item

        # This should never happen.
        return None

    def _handle_selection_change(self, current, previous):
        """ Invoked when the item selection changes. """

        project_item = current.project_item

        if self.indexOfTopLevelItem(current) >= 0:
            header_directory_item = current
            header_file = None
        else:
            header_directory_item = current.parent()
            header_file = project_item

        self._tool.set_header_file(header_file,
                header_directory_item.project_item,
                header_directory_item.showing_ignored)

    def _header_directory_items(self):
        """ A generator for the header directory items. """

        for idx in range(self.topLevelItemCount()):
            yield self.topLevelItem(idx)

    def _header_file_items(self, header_directory_item):
        """ A generator for the header file items of a header directory. """

        for idx in range(header_directory_item.childCount()):
            yield header_directory_item.child(idx)

    def _sort_header_directories(self):
        """ Sort the header directoroes in order. """

        self.sortItems(SourcesWidget.NAME, Qt.SortOrder.AscendingOrder)


class _SourcesItem(QTreeWidgetItem):
    """ This is a base class for all items in the sources tree. """

    def __init__(self, project_item, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self.project_item = project_item
        self.working_version = None

    def set_status(self):
        """ Set the status of the item. """

        raise NotImplementedError

    def set_working_version(self, working_version):
        """ Set the current working versions. """

        self.working_version = working_version
        self.set_status()


class _HeaderDirectoryItem(_SourcesItem):
    """ This class represents a header directory in the sources tree. """

    def __init__(self, header_directory, parent):
        """ Initialise the item. """

        super().__init__(header_directory, parent)

        self.showing_ignored = False

        self.setText(SourcesWidget.NAME, header_directory.name)

        for header_file in header_directory.content:
            _HeaderFileItem(header_file, self)

        self.sortChildren(SourcesWidget.NAME, Qt.SortOrder.AscendingOrder)

    def set_status(self):
        """ Set the status of the item. """

        self.setExpanded(False)

        # Draw the status column.
        if self.working_version is None:
            needs_scanning = (len(self.project_item.scan) != 0)
        else:
            needs_scanning = (self.working_version in self.project_item.scan)

        self.setText(SourcesWidget.STATUS,
                "Needs scanning" if needs_scanning else '')


class _HeaderFileItem(_SourcesItem):
    """ This class represents a header file in the sources tree. """

    def __init__(self, header_file, parent):
        """ Initialise the item. """

        super().__init__(header_file, parent)

        self.setText(SourcesWidget.NAME, header_file.name)

    def set_status(self):
        """ Set the status of the item. """

        hidden = False
        expand_parent = False
        status = ''

        if self.project_item.ignored:
            status = "Ignored"
            hidden = not self.parent().showing_ignored
        elif self.project_item.module == '':
            status = "Needs assigning"
            expand_parent = True
        else:
            working_header_file = self._get_working_header_file()

            if working_header_file is None:
                hidden = True
            elif working_header_file.parse:
                status = "Needs parsing"
                expand_parent = True

        self.setText(SourcesWidget.STATUS, status)
        self.setHidden(hidden)

        if expand_parent:
            self.parent().setExpanded(True)

    def _get_working_header_file(self):
        """ Return the version header file for the current working version if
        any.
        """

        header_file_versions = self.project_item.versions

        if self.working_version is None:
            working_file = None if self.project_item.ignored else header_file_versions[0]
        else:
            for working_file in header_file_versions:
                if working_file.version == self.working_version:
                    break
            else:
                working_file = None

        return working_file
