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


from PyQt4.QtGui import QTreeWidget


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

        # FIXME: Observe the project's name.

    def set_working_version(self):
        """ Set the working version. """

        try:
            self.working_version = self.project.versions[-1]
        except IndexError:
            self.working_version = None
