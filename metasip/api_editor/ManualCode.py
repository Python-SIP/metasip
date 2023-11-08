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


""" This module handles a manual code item. """


from PyQt6.QtWidgets import QDialog

from .Designer.ManualCodeBase import Ui_ManualCodeBase


class ManualCodeDialog(QDialog, Ui_ManualCodeBase):
    """
    This class implements the dialog for manual code.
    """
    def __init__(self, precis, parent):
        """
        Initialise the dialog.

        precis is the current precis.
        parent is the parent widget.
        """
        super(ManualCodeDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self.precis.setText(precis)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        precis = str(self.precis.text()).strip()

        return (precis, )
