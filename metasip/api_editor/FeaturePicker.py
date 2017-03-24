# Copyright (c) 2017 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt5.QtWidgets import QComboBox, QDialog, QGridLayout, QLabel

from .Designer.FeaturePickerBase import Ui_FeaturePickerBase


class FeaturePickerDialog(QDialog, Ui_FeaturePickerBase):
    """ This class implements the dialog for selecting a number of feature
    tags.
    """

    FEATURE_VALUES = ["Unset", "Set", "Inverted"]

    def __init__(self, prj, code, parent):
        """
        Initialise the dialog.

        prj is the containing project.
        code is the code item.
        parent is the parent widget.
        """
        super(FeaturePickerDialog, self).__init__(parent)

        self.setupUi(self)

        lay = self.layout()
        grid = QGridLayout()
        lay.insertLayout(0, grid)

        flistset = code.features
        self._features = []

        # Initialise the dialog.
        all_features = prj.features + prj.externalfeatures

        for row, feature in enumerate(all_features):
            name = QLabel(feature, self)
            grid.addWidget(name, row, 0)

            state = QComboBox(self)
            state.insertItems(0, self.FEATURE_VALUES)
            state._feature = feature
            grid.addWidget(state, row, 1)
            self._features.append(state)

            for f in flistset:
                if f.startswith('!') and feature == f[1:]:
                    state.setCurrentIndex(2)
                elif feature == f:
                    state.setCurrentIndex(1)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        fl = []

        for state in self._features:
            state_index = state.currentIndex()

            if state_index == 2:
                fl.append('!' + state._feature)
            elif state_index == 1:
                fl.append(state._feature)

        return (fl, )
