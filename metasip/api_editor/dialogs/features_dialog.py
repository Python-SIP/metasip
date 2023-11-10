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


from PyQt6.QtWidgets import QComboBox, QGridLayout, QLabel

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
            grid.addWidget(QLabel(feature), row, 0)

            combo_box = QComboBox()
            combo_box.insertItems(0, self.FEATURE_VALUES)
            grid.addWidget(combo_box, row, 1)
            self._features.append((combo_box, feature))

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for combo_box, _ in self._features:
            for f in self.api_item.features:
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

        self.api_item.features = features
