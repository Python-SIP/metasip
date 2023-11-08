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


from ...model import Model, Tuple


class AbstractUIToolkit(Model):
    """ The AbstractUIToolkit class is an abstract base class for
    :term:`toolkits<toolkit>` that implements UI support.
    """

    # A map of declarative factories to attribute types.
    attribute_type_to_declarative_factory_map = Tuple()

    # A map of editor factories to attribute types.
    attribute_type_to_editor_factory_map = Tuple()

    def action(self, parent):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface.

        :param parent:
            is the optional parent view.
        :return:
            the action.
        """

        raise NotImplementedError

    def application(self, argv, **properties):
        """ Create a singleton application, i.e. an object that can be adapted
        to the :class:`~dip.ui.IApplication` interface.

        :param argv:
            is the sequence of command line arguments.
        :param \*\*properties:
            are the keyword arguments used as toolkit specific property names
            and values that are used to configure the application.
        :return:
            the application.  Repeated calls must return the same application.
        """

        raise NotImplementedError

    def check_box(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.ICheckBox` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def close_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle closing an object.

        :return:
            the action.
        """

        raise NotImplementedError

    def combo_box(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IComboBox` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def declarative_factory_for_attribute_type(self, attribute_type):
        """ Get an :class:`~dip.ui.EditorFactory` sub-class that will create a
        factory that will create an editor to handle attributes of a particular
        type.

        :param attribute_type:
            is the type of the attribute.
        :return:
            the :class:`~dip.ui.EditorFactory` sub-class.
        """

        for at, df in self.attribute_type_to_declarative_factory_map:
            if isinstance(attribute_type, at):
                return df

        raise TypeError(
                "there is no editor factory that creates instances of "
                "{0}".format(type(attribute_type).__name__))

    def dialog(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IDialog`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def dock(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IDock`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def editor_factory_for_attribute_type(self, attribute_type):
        """ Get a callable that will create a editor to handle attributes of a
        particular type.

        :param attribute_type:
            is the type of the attribute.
        :return:
            the callable.
        """

        for at, ef in self.attribute_type_to_editor_factory_map:
            if isinstance(attribute_type, at):
                return ef

        raise TypeError(
                "there is no editor factory that creates instances of "
                "{0}".format(type(attribute_type).__name__))

    def error(self, title, text, parent, detail):
        """ Display an error message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the error.
        :param parent:
            is the optional parent view.
        :param detail:
            is the optional additional detail.
        """

        raise NotImplementedError

    def filesystem_location_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IFilesystemLocationEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.  Any factory properties will be applied to an internal
            :class:`~PyQt6.QtWidgets.QLineEdit`.
        """

        raise NotImplementedError

    def find_toolkit_view(self, toolkit_root, id):
        """ Find the toolkit view with a particular identifier.

        :param toolkit_root:
            is the root toolkit view to begin the search.
        :param id:
            is the identifier of the view to search for.
        :return:
            the toolkit view.  An exception will be raised if the view could
            not be found.
        """

        raise NotImplementedError

    def float_spin_box(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IFloatSpinBox` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def form(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IForm`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def get_open_file(self, title, directory='', filter='', parent=None):
        """ Get the name of a file to open from the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param directory:
            is the name of an optional initial directory or file.
        :param filter:
            is the optional file filter.
        :param parent:
            is the optional parent view.
        :return:
            the name of the file to open or an empty string if there was none.
        """

        raise NotImplementedError

    def get_save_file(self, title, directory='', filter='', parent=None):
        """ Get the name of a file to save from the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param directory:
            is the name of an optional initial directory or file.
        :param filter:
            is the optional file filter.
        :param parent:
            is the optional parent view.
        :return:
            the name of the file to save or an empty string if there was none.
        """

        raise NotImplementedError

    def grid(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IGrid`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def group_box(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IGroupBox`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def h_box(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IHBox`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def information(self, title, text, parent):
        """ Display a informational message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the message.
        :param parent:
            is the optional parent view.
        """

        raise NotImplementedError

    def label(self, parent, top_level):
        """ Create an editor that can be adapted to the :class:`~dip.ui.ILabel`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def line_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.ILineEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def list_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IListEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def main_window(self, parent, top_level):
        """ Create a view that can be adapted to the
        :class:`~dip.ui.IMainWindow` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def menu(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IMenu`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def menu_bar(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IMenuBar`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def message_area(self, parent, top_level):
        """ Create a view that can be adapted to the
        :class:`~dip.ui.IMessageArea` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def new_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle creating a new object.

        :return:
            the action.
        """

        raise NotImplementedError

    def open_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle opening an object.

        :return:
            the action.
        """

        raise NotImplementedError

    def option_list(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IOptionList` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def push_button(self, parent, top_level):
        """ Create an that can be adapted to the :class:`~dip.ui.IPushButton`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def question(self, title, text, parent, detail, buttons):
        """ Ask the user a question.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the question.
        :param parent:
            is the optional parent view.
        :param detail:
            is the optional additional detail.
        :param buttons:
            is the sequence of buttons to display.  Possible buttons are 'yes',
            'no', 'cancel', 'save' and 'discard'.  The first in the sequence is
            used as the default.
        :return:
            The button that was pressed.
        """

        raise NotImplementedError

    def quit_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle quitting the application.

        :return:
            the action.
        """

        raise NotImplementedError

    def radio_buttons(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IRadioButtons` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.  Any factory properties will be applied to each of the
            buttons.
        """

        raise NotImplementedError

    def save_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle saving an object.

        :return:
            the action.
        """

        raise NotImplementedError

    def save_as_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle saving an object under a
        new name.

        :return:
            the action.
        """

        raise NotImplementedError

    def spin_box(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.ISpinBox` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def splitter(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.ISplitter`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def stack(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IStack`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def storage_location_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IStorageLocationEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.  Any factory properties will be applied to an internal
            :class:`~PyQt6.QtWidgets.QLineEdit`.
        """

        raise NotImplementedError

    def table_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.ITableEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def text_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.ITextEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def tool_button(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IToolButton` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.
        """

        raise NotImplementedError

    def v_box(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IVBox`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def warning(self, title, text, parent, detail):
        """ Display a warning message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the warning.
        :param parent:
            is the optional parent view.
        :param detail:
            is the optional additional detail.
        """

        raise NotImplementedError

    def whats_this_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle "What's This?".

        :return:
            the action.
        """

        raise NotImplementedError

    def wizard(self, parent, top_level):
        """ Create a view that can be adapted to the :class:`~dip.ui.IWizard`
        interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    def wizard_page(self, parent, top_level):
        """ Create a view that can be adapted to the
        :class:`~dip.ui.IWizardPage` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        raise NotImplementedError

    @attribute_type_to_declarative_factory_map.default
    def attribute_type_to_declarative_factory_map(self):
        """ Invoked to get the default map between attribute types and
        declarative factories.
        """

        from ... import model, ui

        return (
            (model.Bool,        ui.CheckBox),
            (model.Enum,        ui.ComboBox),
            (model.Float,       ui.FloatSpinBox),
            (model.Int,         ui.SpinBox),
            (model.List,        ui.ListEditor),
            (model.Str,         ui.LineEditor),
            (model.Trigger,     ui.PushButton)
        )

    @attribute_type_to_editor_factory_map.default
    def attribute_type_to_editor_factory_map(self):
        """ Invoked to get the default map between attribute types and editor
        factories.
        """

        from ... import model, pui

        return (
            (model.Bool,        pui.CheckBox),
            (model.Enum,        pui.ComboBox),
            (model.Float,       pui.FloatSpinBox),
            (model.Int,         pui.SpinBox),
            (model.Str,         pui.LineEditor)
        )
