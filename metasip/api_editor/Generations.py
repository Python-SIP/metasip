# Copyright (c) 2013 Riverbank Computing Limited.
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

        # Initialise the dialog.  The start list will have the list of versions
        # with the first version replaced by "First".  The end list will have
        # the list of versions excluding the first version and with "Latest"
        # appended.
        for i, v in enumerate(prj.versions):
            if i == 0:
                # The first version never actually appears itself.
                self.sgen.addItem("First", '')
            else:
                self.sgen.addItem(v, v)
                self.egen.addItem(v, v)

        self.egen.addItem("Latest", '')

        if len(api_item.versions) == 0:
            api_start = ''
            api_end = ''
        else:
            api_start = api_item.versions[0].startversion
            api_end = api_item.versions[0].endversion

        if api_start == '':
            start_index = 0
        else:
            start_index = prj.versions.index(api_start)

        if api_end == '':
            end_index = len(prj.versions) - 1
        else:
            end_index = prj.versions.index(api_end) - 1

        self.sgen.setCurrentIndex(start_index)
        self.egen.setCurrentIndex(end_index)

    def fields(self):
        """ Return a tuple of the dialog fields. """

        start_index = self.sgen.currentIndex()
        end_index = self.egen.currentIndex()

        return (self.sgen.itemData(start_index), self.egen.itemData(end_index))
