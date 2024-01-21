# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QComboBox, QGridLayout, QLabel

from ....helpers import BaseDialog


class FeaturesDialog(BaseDialog):
    """ This class implements the dialog for selecting a number of features.
    """

    FEATURE_VALUES = ("Unset", "Set", "Inverted")

    def populate(self, layout):
        """ Populate the dialog's layout. """

        project = self.shell.project

        grid = QGridLayout()
        layout.insertLayout(0, grid)

        all_features = project.features + project.externalfeatures
        self._features = []

        for row, feature in enumerate(all_features):
            grid.addWidget(QLabel(feature), row, 0)

            combo_box = QComboBox()
            combo_box.insertItems(0, self.FEATURE_VALUES)
            grid.addWidget(combo_box, row, 1)
            self._features.append((combo_box, feature))

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for combo_box, feature in self._features:
            for f in self.model.features:
                if f.startswith('!') and feature == f[1:]:
                    index = 2
                elif feature == f:
                    index = 1
                else:
                    index = 0

                combo_box.setCurrentIndex(index)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        features = []

        for combo_box, feature in self._features:
            index = combo_box.currentIndex()

            if index == 2:
                features.append('!' + feature)
            elif index == 1:
                features.append(feature)

        self.model.features = features

        return True
