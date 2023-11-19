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


from PyQt6.QtWidgets import QMainWindow


class Shell:
    """ This class encapsulates an editor and a collection of tools. """

    def __init__(self, editor, *tools):
        """ Initialise the shell. """

        # Create the widget that implements the shell.
        self._shell_widget = QMainWindow()

        self._shell_widget.setCentralWidget(editor)

    def show(self):
        """ Make the shell visible. """

        self._shell_widget.show()

