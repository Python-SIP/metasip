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


from PyQt6.QtWidgets import QBoxLayout, QRadioButton, QWidget

from .....model import adapt, Dict, List, Model
from .....ui import IDisplay, IRadioButtons

from .editor_adapters import EditorLayoutAdapter, EditorWidgetAdapter


class RadioButtonsAdapterMixin(Model):
    """ A mixin for adapters implementing IRadioButtons for widgets and
    layouts.
    """

    # The list of buttons.
    _tk_buttons = List(QRadioButton)

    # The properties to configure new buttons with.
    _tk_properties = Dict()

    def configure(self, properties):
        """ Configure the editor. """

        self._tk_properties = properties

        for button in self._tk_buttons:
            self.tk_configure_button(button)

    @IRadioButtons.read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        for button in self._tk_buttons:
            button.setEnabled(not value)

    @IRadioButtons.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        for button in self._tk_buttons:
            if button.isChecked():
                return button.objectName()

        return None

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        # Save for the notifier.
        self.tk_editor_old_value = value

        if value is None:
            for button in self._tk_buttons:
                button.setChecked(False)
        else:
            for button in self._tk_buttons:
                if button.objectName() == value:
                    button.setChecked(True)
                    break
            else:
                raise ValueError("invalid option: {0}".format(value))

    def tk_configure_button(self, button):
        """ Configure a new button. """

        button.setEnabled(not self.read_only)

        try:
            button.pyqtConfigure(**self._tk_properties)
        except AttributeError:
            pass

        button.clicked.connect(self.__on_button_clicked)

    def tk_options_setter(self, layout, value):
        """ Set the options. """

        # Create or delete buttons as required to match the number of options.
        nr_buttons = len(self._tk_buttons)
        nr_options = len(value)

        if nr_buttons > nr_options:
            for i in range(nr_options, nr_buttons):
                button = self._tk_buttons.pop[nr_options]
                layout.removeWidget(button)

        elif nr_buttons < nr_options:
            for i in range(nr_buttons, nr_options):
                button = QRadioButton()
                self.tk_configure_button(button)

                # Add to the layout allowing for it to have a stretch at the
                # end.
                layout.insertWidget(i, button)

                self._tk_buttons.append(button)

        # Set up the options in the buttons.
        for i in range(nr_options):
            self._tk_buttons[i].setObjectName(value[i])

        self.tk_set_button_text(layout, value, self.labels)

    def tk_sorted_setter(self, layout, value):
        """ Set the sorted state. """

        if value:
            self.tk_sort(layout)

    def tk_set_button_text(self, layout, options, labels):
        """ Set the text of each button. """

        for button in self._tk_buttons:
            option = button.objectName()
            idx = options.index(option)

            try:
                text = labels[idx]
            except IndexError:
                idisplay = IDisplay(option, exception=False)
                text = '' if idisplay is None else idisplay.name
                if text == '':
                    text = str(option)

            button.setText(text)

        if self.sorted:
            self.tk_sort(layout)

    def tk_sort(self, layout):
        """ Sort the buttons according to their labels. """

        # Remove all the buttons from the layout.
        for button in self._tk_buttons:
            layout.removeWidget(button)

        # Sort the buttons.
        buttons = sorted(buttons, key=lambda button: button.text(),
                reverse=True)

        # Re-add them to the layout allowing for it to have a stretch at the
        # end.
        for button in buttons:
            layout.insertWidget(0, button)

    def tk_vertical_getter(self, layout):
        """ Get the orientation. """

        return layout.direction() in (QBoxLayout.TopToBottom,
                QBoxLayout.BottomToTop)

    def tk_vertical_setter(self, layout, value):
        """ Set the orientation. """

        layout.setDirection(
                QBoxLayout.TopToBottom if value else QBoxLayout.LeftToRight)

    def __on_button_clicked(self):
        """ Invoked when a button is clicked. """

        self.tk_editor_notify(self.value)


@adapt(QBoxLayout, to=IRadioButtons)
class QBoxLayoutIRadioButtonsAdapter(EditorLayoutAdapter, RadioButtonsAdapterMixin):
    """ An adapter to implement IRadioButtons for a QBoxLayout. """

    @IRadioButtons.labels.setter
    def labels(self, value):
        """ Invoked to set the labels. """

        self.tk_set_button_text(self.adaptee, self.options, value)

    @IRadioButtons.options.setter
    def options(self, value):
        """ Invoked to set the options. """

        self.tk_options_setter(self.adaptee, value)

    @IRadioButtons.sorted.setter
    def sorted(self, value):
        """ Invoked to set the sorted state. """

        self.tk_sorted_setter(self.adaptee, value)

    @IRadioButtons.vertical.getter
    def vertical(self):
        """ Invoked to get the orientation. """

        return self.tk_vertical_getter(self.adaptee)

    @vertical.setter
    def vertical(self, value):
        """ Invoked to set the orientation. """

        self.tk_vertical_setter(self.adaptee, value)


@adapt(QWidget, to=IRadioButtons)
class QWidgetIRadioButtonsAdapter(EditorWidgetAdapter, RadioButtonsAdapterMixin):
    """ An adapter to implement IRadioButtons for a QWidget. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        return isinstance(adaptee.layout(), QBoxLayout)

    @IRadioButtons.labels.setter
    def labels(self, value):
        """ Invoked to set the labels. """

        self.tk_set_button_text(self.adaptee.layout(), self.options, value)

    @IRadioButtons.options.setter
    def options(self, value):
        """ Invoked to set the options. """

        self.tk_options_setter(self.adaptee.layout(), value)

    @IRadioButtons.sorted.setter
    def sorted(self, value):
        """ Invoked to set the sorted state. """

        self.tk_sorted_setter(self.adaptee.layout(), value)

    @IRadioButtons.vertical.getter
    def vertical(self):
        """ Invoked to get the orientation. """

        return self.tk_vertical_getter(self.adaptee.layout())

    @vertical.setter
    def vertical(self, value):
        """ Invoked to set the orientation. """

        self.tk_vertical_setter(self.adaptee.layout(), value)
