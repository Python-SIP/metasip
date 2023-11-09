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


from PyQt6.QtWidgets import QComboBox, QDialog, QGridLayout, QLabel

from .base_dialog import BaseDialog


class FeaturesDialog(BaseDialog):
    """ This class implements the dialog for selecting a number of features.
    """

    FEATURE_VALUES = ("Unset", "Set", "Inverted")

    def populate(self):
        """ Populate the dialog's layout. """

        layout = self.layout()

        grid = QGridLayout()
        layout.insertLayout(0, grid)

        all_features = self.project.features + self.project.externalfeatures
        self._features = []

        for row, feature in enumerate(all_features):
            name = QLabel(feature)
            grid.addWidget(name, row, 0)

            state = QComboBox()
            state.insertItems(0, self.FEATURE_VALUES)
            grid.addWidget(state, row, 1)
            self._features.append((state, feature))

            for f in self.api_item.features:
                if f.startswith('!') and feature == f[1:]:
                    state.setCurrentIndex(2)
                elif feature == f:
                    state.setCurrentIndex(1)

    def exec(self):
        """ Return a list of features or None if the dialog was cancelled. """

        if super().exec() == int(QDialog.DialogCode.Rejected):
            return None

        features = []

        for state, feature in self._features:
            state_index = state.currentIndex()

            if state_index == 2:
                features.append('!' + feature)
            elif state_index == 1:
                features.append(feature)

        return features
