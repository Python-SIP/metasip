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


from PyQt6.QtWidgets import QMessageBox


def warning(title, text, detail=None, parent=None):
    """ Display a warning message to the user. """

    if detail is None:
        QMessageBox.warning(parent, title, text)
    else:
        message_box = QMessageBox(QMessageBox.StandardButton.Warning, title,
                text, parent=parent, detailedText=detail)
        message_box.exec()
