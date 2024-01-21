# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from abc import ABC, abstractmethod

from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QSizePolicy,
        QSpacerItem, QVBoxLayout)


class BaseDialog(ABC):
    """ A base class for dialogs that update a model. """

    def __init__(self, model, title, shell):
        """ Initialise the dialog. """

        self.model = model
        self.shell = shell

        self.widget = QDialog(shell.widget)

        self.widget.setWindowTitle(title)

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        self.populate(layout)

        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Cancel |
                QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self._handle_accept)
        button_box.rejected.connect(self.widget.reject)
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

        return self.widget.exec() == int(QDialog.DialogCode.Accepted)

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
            self.widget.accept()

