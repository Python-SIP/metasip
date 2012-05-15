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
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem

from dip.model import observe


class ScannerView(QTreeWidget):
    """ ScannerView is an internal class that implements the project specific
    part of the scanner tool GUI.
    """

    def __init__(self, project):
        """ Initialise the view.

        :param project:
            is the project.
        """

        super().__init__()

        self.setHeaderLabels(["Name", "Status", "Module"])

        self.project = project
        self.source_directory = ''

        self.set_working_version()

        ProjectItem(project, self)

    def set_working_version(self):
        """ Set the working version. """

        try:
            self.working_version = self.project.versions[-1]
        except IndexError:
            self.working_version = None


class ProjectItem(QTreeWidgetItem):
    """ ProjectItem is an internal class that represents a project in the
    scanner tool GUI.
    """

    def __init__(self, project, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._project = project

        self.setText(0, project.descriptive_name())
        observe('name', project,
                lambda c: self.setText(0, c.model.descriptive_name()))

        self.setExpanded(True)

        for header_directory in project.headers:
            HeaderDirectoryItem(header_directory, self)

        self.sortChildren(0, Qt.AscendingOrder)


class HeaderDirectoryItem(QTreeWidgetItem):
    """ HeaderDirectoryItem is an internal class that represents a header
    directory in the scanner tool GUI.
    """

    def __init__(self, header_directory, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._header_directory = header_directory

        self.setText(0, header_directory.name)

        for header_file in header_directory.content:
            HeaderFileItem(header_file, self)

        self.sortChildren(0, Qt.AscendingOrder)


class HeaderFileItem(QTreeWidgetItem):
    """ HeaderFileItem is an internal class that represents a header file in
    the scanner tool GUI.
    """

    def __init__(self, header_file, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._header_file = header_file

        self.setText(0, header_file.name)
