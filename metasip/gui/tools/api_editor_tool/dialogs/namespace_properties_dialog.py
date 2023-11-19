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


from PyQt6.QtWidgets import QCheckBox, QDialog, QGroupBox, QVBoxLayout

from .abstract_dialog import AbstractDialog
from .helpers import split_annos


class NamespacePropertiesDialog(AbstractDialog):
    """ This class implements the dialog for a namespace's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        group_box = QGroupBox("Annotations")
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        self._pyqt_no_qmetaobject = QCheckBox('PyQtNoQMetaObject')
        group_box_layout.addWidget(self._pyqt_no_qmetaobject)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for name, value in split_annos(self.api_item.annos):
            if name == 'PyQtNoQMetaObject':
                self._pyqt_no_qmetaobject.setChecked(True)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        if self._pyqt_no_qmetaobject.isChecked():
            annos_list.append('PyQtNoQMetaObject')

        self.api_item.annos = ','.join(annos_list)
