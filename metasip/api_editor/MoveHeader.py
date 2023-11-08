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


from PyQt6.QtWidgets import QDialog

from .Designer.MoveHeaderBase import Ui_MoveHeaderBase


class MoveHeaderDialog(QDialog, Ui_MoveHeaderBase):
    """ This class implements the dialog for moving a header file to another
    module.
    """

    def __init__(self, prj, src_module, sip_file, parent):
        """
        Initialise the dialog.

        prj is the containing project.
        sip_file is the header item to move.
        parent is the parent widget.
        """
        super().__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        for mod in sorted(prj.modules, key=lambda m: m.name):
            if mod is src_module:
                continue

            self.destCb.addItem(mod.name, mod)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def exec(self):
        """ Start the dialog and return the destination module or None if the
        user cancelled.
        """

        if super().exec() == QDialog.Rejected:
            return None

        return self.destCb.currentData()
