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


from PyQt4.QtGui import QDialog

from .Designer.GenerationsBase import Ui_GenerationsBase


class GenerationsDialog(QDialog, Ui_GenerationsBase):
    """ This class implements the dialog for versions. """

    def __init__(self, prj, api_item, parent):
        """
        Initialise the dialog.

        prj is the containing project.
        api_item is the API item.
        parent is the parent widget.
        """
        # FIXME: Support multiple version ranges.
        super().__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self.sgen.addItem("First", None)

        start_index = 0
        end_index = len(prj.versions)

        if len(api_item.versions) == 0:
            api_start = None
            api_end = None
        else:
            vers = api_item.versions[0]
            api_start = vers.startversion
            api_end = vers.endversion

        for i, v in enumerate(prj.versions):
            self.sgen.addItem(v.name, v)
            if v is api_start:
                start_index = i + 1

            self.egen.addItem(v.name, v)
            if v is api_end:
                end_index = i

        self.egen.addItem("Latest", None)

        self.sgen.setCurrentIndex(start_index)
        self.egen.setCurrentIndex(end_index)

    def fields(self):
        """ Return a tuple of the dialog fields. """

        start_index = self.sgen.currentIndex()
        end_index = self.egen.currentIndex()

        return (self.itemData(start_index), self.itemData(end_index))
