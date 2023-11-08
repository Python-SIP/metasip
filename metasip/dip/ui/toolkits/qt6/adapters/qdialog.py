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


from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLayout

from .....model import adapt, Instance, unadapted
from .....ui import IDialog, IView

from ..exceptions import Qt6ToolkitError

from .single_view_container_adapters import SingleViewContainerWidgetAdapter


# The map of dip dialog buttons to the Qt equivalents.
_button_map = {'ok': QDialogButtonBox.Ok, 'cancel': QDialogButtonBox.Cancel,
        'yes': QDialogButtonBox.Yes, 'no': QDialogButtonBox.No}


@adapt(QDialog, to=IDialog)
class QDialogIDialogAdapter(SingleViewContainerWidgetAdapter):
    """ An adapter to implement IDialog for a QDialog. """

    # The button box.
    _button_box = Instance(QDialogButtonBox)

    # The layout.
    _layout = Instance(QLayout)

    # These are all the button roles that require a valid view in order to be
    # enabled.
    _valid_roles = (QDialogButtonBox.AcceptRole,
            QDialogButtonBox.DestructiveRole, QDialogButtonBox.ActionRole,
            QDialogButtonBox.YesRole, QDialogButtonBox.ApplyRole)

    def configure(self, properties):
        """ Configure the widget. """

        self._button_box.accepted.connect(self._on_accepted)
        self._button_box.rejected.connect(self.adaptee.reject)

        super().configure(properties)

    def execute(self):
        """ Execute the dialog as a modal dialog.

        :return:
            ``True`` if the user accepted the dialog.
        """

        return bool(self.adaptee.exec())

    @IDialog.acceptable.setter
    def acceptable(self, value):
        """ Invoked to set the acceptable state. """

        button_box = self._button_box

        for qbutton in button_box.buttons():
            if button_box.buttonRole(qbutton) in self._valid_roles:
                qbutton.setEnabled(value)

    @IDialog.buttons.getter
    def buttons(self):
        """ Invoked to get the buttons. """

        button_box = self._button_box

        buttons = []
        for qbutton in self._button_box.buttons():
            sbutton = button_box.standardButton(qbutton)

            for button, standard_button in _button_map.items():
                if sbutton == standard_button:
                    buttons.append(button)

        return tuple(buttons)

    @buttons.setter
    def buttons(self, value):
        """ Invoked to set the buttons. """

        button_box = self._button_box

        # Remove any existing buttons.
        button_box.clear()

        # Add the new buttons.
        for button in value:
            button_box.addButton(_button_map[button])

    @IDialog.view.getter
    def view(self):
        """ Invoked to get the contained view. """

        # We assume that it is the first item in the top level layout (so long
        # as there is more than one item).
        layout = self._layout
        if layout.count() <= 1:
            return None

        itm = layout.itemAt(0)
        w = itm.widget()

        return IView(itm.layout()) if w is None else IView(w)

    @view.setter
    def view(self, value):
        """ Invoked to set the contained view. """

        layout = self._layout

        # Assume we are replacing a widget if there is more than one item.
        if layout.count() > 1:
            layout.takeItem(0)

        value = unadapted(value)

        if value is not None:
            if isinstance(value, QLayout):
                layout.insertLayout(0, value)
            else:
                layout.insertWidget(0, value)

    @_button_box.default
    def _button_box(self):
        """ Invoked to get the button box. """

        dialog = self.adaptee

        button_box = dialog.findChild(QDialogButtonBox)
        if button_box is None:
            raise Qt6ToolkitError("{0} instance implementing a Dialog does "
                    "not contain a QDialogButtonBox".format(
                            type(dialog).__name__))

        return button_box

    @_layout.default
    def _layout(self):
        """ Invoked to get the layout. """

        dialog = self.adaptee

        layout = dialog.layout()
        if layout is None:
            raise Qt6ToolkitError("{0} instance implementing a Dialog does "
                    "not have a layout".format(type(dialog).__name__))

        return layout

    def _on_accepted(self):
        """ Invoked when the dialog is accepted. """

        self.accepted = True
        self.adaptee.accept()
