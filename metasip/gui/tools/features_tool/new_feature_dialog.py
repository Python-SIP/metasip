# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QFormLayout, QLineEdit

from ...helpers import BaseDialog
from ...shell import EventType

from .helpers import validate_feature_name


class NewFeatureDialog(BaseDialog):
    """ This class implements the dialog for creating a new feature. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._feature = QLineEdit()
        form.addRow("Feature name", self._feature)

        self._external = QCheckBox("Feature is defined in another project?")
        layout.addWidget(self._external)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        feature = self._feature.text().strip()
        if not validate_feature_name(feature, project, self):
            return False

        if self._external.isChecked():
            features_list = project.externalfeatures
        else:
            features_list = project.features

        features_list.append(feature)

        self.shell.notify(EventType.FEATURE_ADD, feature)

        return True
