# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator

from dip.model import observe


class ScannerView(QTreeWidget):
    """ ScannerView is an internal class that implements the project specific
    part of the scanner tool GUI.
    """

    # The column numbers.
    (NAME, STATUS) = range(2)

    def __init__(self, controller, project):
        """ Initialise the view. """

        super().__init__()

        self.setHeaderLabels(["Name", "Status"])

        self.itemSelectionChanged.connect(self.refresh_selection)

        self._controller = controller
        self.project = project
        self.source_directory = ''

        self.reset_working_version()

        ProjectItem(project, self)

    def get_working_version(self):
        """ Get the working version. """

        return self._working_version

    def set_working_version(self, working_version):
        """ Set the working version. """

        if self._working_version != working_version:
            self._working_version = working_version

            for itm in self._items():
                itm.update_working_version()

    def reset_working_version(self):
        """ Reset the working version. """

        try:
            self._working_version = self.project.versions[-1]
        except IndexError:
            self._working_version = None

    def refresh_selection(self):
        """ Invoked when the item selection changes. """

        self._controller.selection(
                [itm.get_project_item() for itm in self.selectedItems()])

    def _items(self):
        """ A generator for all the items in the tree. """

        it = QTreeWidgetItemIterator(self)

        value = it.value()
        while value is not None:
            yield value
            it += 1
            value = it.value()


class ScannerItem(QTreeWidgetItem):
    """ ScannerItem is an internal base class for all items in the scanner tool
    tree.
    """

    def update_working_version(self):
        """ Update in the light of the working versions.  This default
        implementation does nothing.
        """

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        raise NotImplementedError


class ProjectItem(ScannerItem):
    """ ProjectItem is an internal class that represents a project in the
    scanner tool GUI.
    """

    def __init__(self, project, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._project = project

        self.setText(ScannerView.NAME, project.descriptive_name())
        observe('name', project,
                lambda c: self.setText(ScannerView.NAME,
                        c.model.descriptive_name()))

        self.setExpanded(True)

        for header_directory in project.headers:
            HeaderDirectoryItem(header_directory, self)

        self.sortChildren(ScannerView.NAME, Qt.AscendingOrder)

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        return self._project


class HeaderDirectoryItem(ScannerItem):
    """ HeaderDirectoryItem is an internal class that represents a header
    directory in the scanner tool GUI.
    """

    def __init__(self, header_directory, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._header_directory = header_directory

        self._draw_status()
        observe('scan', header_directory, lambda c: self._draw_status())

        self.setText(ScannerView.NAME, header_directory.name)

        expand = False

        for header_file in header_directory.content:
            itm = HeaderFileItem(header_file, self)

            # Expand the header directory if there is at least one non-ignored
            # file that needs something doing.
            if not header_file.ignored and itm.text(ScannerView.STATUS) != '':
                expand = True

        self.sortChildren(ScannerView.NAME, Qt.AscendingOrder)

        if expand:
            self.setExpanded(True)

    def update_working_version(self):
        """ Update in the light of the working version. """

        self._draw_status()

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        return self._header_directory

    def _draw_status(self):
        """ Draw the status column. """

        working_version = self.treeWidget().get_working_version()
        if working_version is None:
            needs_scanning = (len(self._header_directory.scan) != 0)
        else:
            needs_scanning = (working_version in self._header_directory.scan)

        self.setText(ScannerView.STATUS,
                "Needs scanning" if needs_scanning else "")

class HeaderFileItem(ScannerItem):
    """ HeaderFileItem is an internal class that represents a header file in
    the scanner tool GUI.
    """

    def __init__(self, header_file, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._header_file = header_file

        self.update_working_version()

        # Draw the rest of the item.
        self.setText(ScannerView.NAME, header_file.name)

    def update_working_version(self):
        """ Update in the light of the working version. """

        # Get the working version of the file, if any.
        working_version = self.treeWidget().get_working_version()

        if working_version is None:
            working_file = self._header_file.versions[0]
        else:
            for working_file in self._header_file.versions:
                if working_file.version == working_version:
                    break
            else:
                working_file = None

        self.setHidden(working_file is None)

        # Determine the status.
        if self._header_file.ignored:
            status = "Ignored"
        elif working_file is not None and working_file.parse:
            status = "Needs parsing"
        else:
            status = ''

        self.setText(ScannerView.STATUS, status)

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        return self._header_file
