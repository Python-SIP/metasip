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


import os

from PyQt4.QtGui import QApplication, QProgressDialog


class SlowPyfile:
    """ The SlowPyfile class implements a file-like object for files that may
    take time to process.  If so the user is updated with progress.
    """

    def __init__(self, name):
        """ Initialise the object.

        :param name:
            is the name of the file.
        """

        self.name = name

        self._file = open(name, 'rb')

        # Get the file size.
        self._file_size = os.fstat(self._file.fileno()).st_size

        # Create the progress dialog.
        self._progress = QProgressDialog("Loading...", None, 0,
                self._file_size)
        self._progress.setWindowTitle(name)

        self._read_so_far = 0
        self._update_progress()

    def close(self):
        """ Implement the standard file object close() method. """

        self._file.close()

    def read(self, size=-1):
        """ Implement the standard file object read() method. """

        block = self._file.read(size)

        self._read_so_far += len(block)
        self._update_progress()

        return block

    def _update_progress(self):
        """ Update the progress dialog. """

        self._progress.setValue(self._read_so_far)
        QApplication.processEvents()
