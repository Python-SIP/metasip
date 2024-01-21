# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QDialog, QGroupBox, QVBoxLayout

from ....helpers import BaseDialog

from .helpers import split_annos


class NamespacePropertiesDialog(BaseDialog):
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

        for name, value in split_annos(self.model.annos):
            if name == 'PyQtNoQMetaObject':
                self._pyqt_no_qmetaobject.setChecked(True)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        if self._pyqt_no_qmetaobject.isChecked():
            annos_list.append('PyQtNoQMetaObject')

        self.model.annos = ','.join(annos_list)

        return True
