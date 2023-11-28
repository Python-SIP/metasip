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


from abc import ABC, abstractmethod

from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QSizePolicy,
        QSpacerItem, QVBoxLayout)


class BaseDialog(ABC):
    """ A base class for dialogs that update a model. """

    def __init__(self, model, title, shell):
        """ Initialise the dialog. """

        self.model = model
        self.shell = shell

        self.dialog = QDialog(shell.shell_widget)

        self.dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        self.dialog.setLayout(layout)

        self.populate(layout)

        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Cancel |
                QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self._handle_accept)
        button_box.rejected.connect(self.dialog.reject)
        layout.addWidget(button_box)

    @abstractmethod
    def populate(self, layout):
        """ Reimplemented by a sub-class to populate the dialog's layout. """

        ...

    def update(self):
        """ Return True if the model was updated or False if the dialog was
        cancelled.
        """

        self.set_fields()

        return self.dialog.exec() == int(QDialog.DialogCode.Accepted)

    def set_fields(self):
        """ Normally reimplemented by a sub-class to set the dialog's fields
        from the model.
        """

        # This default implementation does nothing.
        pass

    def get_fields(self):
        """ Reimplemented by a sub-class to update the model from the
        dialog's fields.  Returns True if the update was valid.
        """

        # This default implementation does nothing.
        return True

    def _handle_accept(self):
        """ Handle the Ok button. """

        # Only accept the dialog if the fields are valid. """
        if self.get_fields():
            self.dialog.accept()

