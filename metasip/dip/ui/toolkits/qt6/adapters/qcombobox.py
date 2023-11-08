# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt6.QtWidgets import QComboBox

from .....model import adapt
from .....ui import IComboBox, IDisplay, IOptionSelector

from .editor_adapters import EditorWidgetAdapter


@adapt(QComboBox, to=IComboBox)
class QComboBoxIComboBoxAdapter(EditorWidgetAdapter):
    """ An adapter to implement IComboBox for a QComboBox. """

    def configure(self, properties):
        """ Configure the editor. """

        self.adaptee.currentIndexChanged.connect(
                self._on_current_index_changed)

        super().configure(properties)

    @IComboBox.labels.setter
    def labels(self, value):
        """ Invoked to set the labels. """

        widget = self.adaptee

        # For each item see if we have a new label allowing for the items
        # having been sorted.
        nr_labels = len(value)

        for row in range(widget.count()):
            try:
                idx = self.options.index(widget.itemData(row))
            except ValueError:
                idx = -1

            if idx >= 0 and idx < nr_labels:
                widget.setItemText(idx, value[idx])

        if self.sorted:
            widget.model().sort(0)

    @IComboBox.options.setter
    def options(self, value):
        """ Invoked to set the options. """

        widget = self.adaptee

        blocked = widget.blockSignals(True)

        # Save the current value for later.
        selected = self._get_value()

        # Create or delete items as required to match the number of options.
        nr_items = widget.count()
        nr_options = len(value)

        if nr_items > nr_options:
            for i in range(nr_options, nr_items):
                widget.removeItem(nr_options)

        elif nr_items < nr_options:
            for i in range(nr_items, nr_options):
                widget.addItem('')

        # Set the options before sorting.
        for idx, option in enumerate(value):
            try:
                as_string = self.labels[idx]
            except IndexError:
                option = value[idx]
                idisplay = IDisplay(option, exception=False)
                as_string = '' if idisplay is None else idisplay.name
                if as_string == '':
                    as_string = str(option)

            widget.setItemText(idx, as_string)
            widget.setItemData(idx, option)

        if self.sorted:
            widget.model().sort(0)

        # Restore the current value.
        self._set_value(selected)

        widget.blockSignals(blocked)

    @IComboBox.sorted.setter
    def sorted(self, value):
        """ Invoked to set the sorted state. """

        if value:
            self.adaptee.model().sort(0)

    @IComboBox.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self._get_value()

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        widget = self.adaptee

        # Save for the notifier.
        self.tk_editor_old_value = value

        blocked = widget.blockSignals(True)
        self._set_value(value)
        widget.blockSignals(blocked)

    def _on_current_index_changed(self, idx):
        """ Invoked when the current index changes. """

        self.tk_editor_notify(self.adaptee.itemData(idx) if idx >= 0 else None)

    def _get_value(self):
        """ Get the editor's value. """

        widget = self.adaptee

        idx = widget.currentIndex()

        return widget.itemData(idx) if idx >= 0 else None

    def _set_value(self, value):
        """ Set the editor's value. """

        widget = self.adaptee

        if value is None:
            idx = -1
        else:
            for idx in range(widget.count()):
                itm = widget.itemData(idx)

                if itm == value:
                    break
            else:
                raise ValueError("'{0}' is not a valid option".format(value))

        widget.setCurrentIndex(idx)
