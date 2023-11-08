# Copyright (c) 2018 Riverbank Computing Limited.
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


from ..ui import UIToolkit


def Action(parent=None, **args):
    """ Create a toolkit specific action that implements the
    :class:`~dip.ui.IAction` interface.

    :param parent:
        is the optional parent view.
    :param args:
        are the initial attribute and property values.
    :return:
        the action.
    """

    from ..ui import IAction

    return _factory(UIToolkit.action, IAction, args, parent)


def CheckBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific check box that implements the
    :class:`~dip.ui.ICheckBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the check box.
    """

    from ..ui import ICheckBox

    return _factory(UIToolkit.check_box, ICheckBox, args, parent, top_level)


def ComboBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific combo box that implements the
    :class:`~dip.ui.IComboBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the combo box.
    """

    from ..ui import IComboBox

    return _factory(UIToolkit.combo_box, IComboBox, args, parent, top_level)


def Dialog(parent=None, top_level=False, **args):
    """ Create a toolkit specific dialog that implements the
    :class:`~dip.ui.IDialog` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the dialog.
    """

    from ..ui import IDialog

    return _factory(UIToolkit.dialog, IDialog, args, parent, top_level)


def Dock(parent=None, top_level=False, **args):
    """ Create a toolkit specific dock that implements the
    :class:`~dip.ui.IDock` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the dock.
    """

    from ..ui import IDock

    return _factory(UIToolkit.dock, IDock, args, parent, top_level)


def FilesystemLocationEditor(parent=None, top_level=False, **args):
    """ Create a toolkit specific file selector that implements the
    :class:`~dip.ui.IFilesystemLocationEditor` interface.  Note that
    :class:`~dip.pui.StorageLocationEditor` should normally be used instead.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the filesystem location editor.
    """

    from ..ui import IFilesystemLocationEditor

    return _factory(UIToolkit.filesystem_location_editor,
            IFilesystemLocationEditor, args, parent, top_level)


def FloatSpinBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific float spin box that implements the
    :class:`~dip.ui.IFloatSpinBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the float spin box.
    """

    from ..ui import IFloatSpinBox

    return _factory(UIToolkit.float_spin_box, IFloatSpinBox, args, parent,
            top_level)


def Form(parent=None, top_level=False, **args):
    """ Create a toolkit specific form that implements the
    :class:`~dip.ui.IForm` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the form.
    """

    from ..ui import IForm

    return _factory(UIToolkit.form, IForm, args, parent, top_level)


def Grid(parent=None, top_level=False, **args):
    """ Create a toolkit specific grid container that implements the
    :class:`~dip.ui.IGrid` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the grid container.
    """

    from ..ui import IGrid

    return _factory(UIToolkit.grid, IGrid, args, parent, top_level)


def GroupBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific group box that implements the
    :class:`~dip.ui.IGroupBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the group box.
    """

    from ..ui import IGroupBox

    return _factory(UIToolkit.group_box, IGroupBox, args, parent, top_level)


def HBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific horizontal box container that implements the
    the :class:`~dip.ui.IHBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the horizontal box container.
    """

    from ..ui import IHBox

    return _factory(UIToolkit.h_box, IHBox, args, parent, top_level)


def Label(parent=None, top_level=False, **args):
    """ Create a toolkit specific label that implements the
    :class:`~dip.ui.ILabel` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the label.
    """

    from ..ui import ILabel

    return _factory(UIToolkit.label, ILabel, args, parent, top_level)


def LineEditor(parent=None, top_level=False, **args):
    """ Create a toolkit specific line editor that implements the
    :class:`~dip.ui.ILineEditor` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the line editor.
    """

    from ..ui import ILineEditor

    return _factory(UIToolkit.line_editor, ILineEditor, args, parent,
            top_level)


def ListEditor(parent=None, top_level=False, **args):
    """ Create a toolkit specific list editor that implements the
    :class:`~dip.ui.IListEditor` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the list editor.
    """

    from ..ui import IListEditor

    return _factory(UIToolkit.list_editor, IListEditor, args, parent,
            top_level)


def MainWindow(parent=None, top_level=False, **args):
    """ Create a toolkit specific main window that implements the
    :class:`~dip.ui.IMainWindow` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the main window.
    """

    from ..ui import IMainWindow

    return _factory(UIToolkit.main_window, IMainWindow, args, parent,
            top_level)


def Menu(parent=None, top_level=False, **args):
    """ Create a toolkit specific menu that implements the
    :class:`~dip.ui.IMenu` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the menu.
    """

    from ..ui import IMenu

    return _factory(UIToolkit.menu, IMenu, args, parent, top_level)


def MenuBar(parent=None, top_level=False, **args):
    """ Create a toolkit specific menu bar that implements the
    :class:`~dip.ui.IMenuBar` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the menu bar.
    """

    from ..ui import IMenuBar

    return _factory(UIToolkit.menu_bar, IMenuBar, args, parent, top_level)


def MessageArea(parent=None, top_level=False, **args):
    """ Create a toolkit specific message area that implements the
    :class:`~dip.ui.IMessageArea` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the message area.
    """

    from ..ui import IMessageArea

    return _factory(UIToolkit.message_area, IMessageArea, args, parent,
            top_level)


def OptionList(parent=None, top_level=False, **args):
    """ Create a toolkit specific option list that implements the
    :class:`~dip.ui.IOptionList` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the option list.
    """

    from ..ui import IOptionList

    return _factory(UIToolkit.option_list, IOptionList, args, parent,
            top_level)


def PushButton(parent=None, top_level=False, **args):
    """ Create a toolkit specific push button that implements the
    :class:`~dip.ui.IPushButton` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the push button.
    """

    from ..ui import IPushButton

    return _factory(UIToolkit.push_button, IPushButton, args, parent,
            top_level)


def RadioButtons(parent=None, top_level=False, **args):
    """ Create a toolkit specific set of radio buttons that implements the
    :class:`~dip.ui.IRadioButtons` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the radio buttons.
    """

    from ..ui import IRadioButtons

    return _factory(UIToolkit.radio_buttons, IRadioButtons, args, parent,
            top_level)


def SpinBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific int spin box that implements the
    :class:`~dip.ui.ISpinBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the int spin box.
    """

    from ..ui import ISpinBox

    return _factory(UIToolkit.spin_box, ISpinBox, args, parent, top_level)


def Splitter(parent=None, top_level=False, **args):
    """ Create a toolkit specific splitter that implements the
    :class:`~dip.ui.ISplitter` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the splitter.
    """

    from ..ui import ISplitter

    return _factory(UIToolkit.splitter, ISplitter, args, parent, top_level)


def Stack(parent=None, top_level=False, **args):
    """ Create a toolkit specific view stack that implements the
    :class:`~dip.ui.IStack` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the view stack.
    """

    from ..ui import IStack

    return _factory(UIToolkit.stack, IStack, args, parent, top_level)


def StorageLocationEditor(parent=None, top_level=False, **args):
    """ Create a toolkit specific file selector that implements the
    :class:`~dip.ui.IStorageLocationEditor` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the storage location editor.
    """

    from ..ui import IStorageLocationEditor

    return _factory(UIToolkit.storage_location_editor, IStorageLocationEditor,
            args, parent, top_level)


def TableEditor(parent=None, top_level=False, **args):
    """ Create a toolkit specific table editor that implements the
    :class:`~dip.ui.ITableEditor` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the table editor.
    """

    from ..ui import ITableEditor

    return _factory(UIToolkit.table_editor, ITableEditor, args, parent,
            top_level)


def TextEditor(parent=None, top_level=False, **args):
    """ Create a toolkit specific text editor that implements the
    :class:`~dip.ui.ITextEditor` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the text editor.
    """

    from ..ui import ITextEditor

    return _factory(UIToolkit.text_editor, ITextEditor, args, parent,
            top_level)


def ToolButton(parent=None, top_level=False, **args):
    """ Create a toolkit specific tool button that implements the
    :class:`~dip.ui.IToolButton` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the tool button.
    """

    from ..ui import IToolButton

    return _factory(UIToolkit.tool_button, IToolButton, args, parent,
            top_level)


def VBox(parent=None, top_level=False, **args):
    """ Create a toolkit specific vertical box container that implements the
    :class:`~dip.ui.IVBox` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the vertical box container.
    """

    from ..ui import IVBox

    return _factory(UIToolkit.v_box, IVBox, args, parent, top_level)


def Wizard(parent=None, top_level=False, **args):
    """ Create a toolkit specific wizard that implements the
    :class:`~dip.ui.IWizard` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the wizard.
    """

    from ..ui import IWizard

    return _factory(UIToolkit.wizard, IWizard, args, parent, top_level)


def WizardPage(parent=None, top_level=False, **args):
    """ Create a toolkit specific wizard page that implements the
    :class:`~dip.ui.IWizardPage` interface.

    :param parent:
        is the optional parent view.
    :param top_level:
        is ``True`` if the view is to be used as a top-level widget.
    :param args:
        are the initial attribute and property values.
    :return:
        the wizard page.
    """

    from ..ui import IWizardPage

    return _factory(UIToolkit.wizard_page, IWizardPage, args, parent,
            top_level)


def _factory(factory, interface, args, parent, top_level=None):
    """ Use the default toolkit to create a configured object. """

    obj = interface(
            factory(parent) if top_level is None else factory(parent, top_level))

    if args:
        # Go through any arguments setting those that correspond to interface
        # attributes and saving the rest which must therefore be toolkit view
        # specific properties.
        properties = {}

        for aname, avalue in args.items():
            if hasattr(obj, aname):
                setattr(obj, aname, avalue)
            else:
                properties[aname] = avalue

        obj.configure(properties)

    return obj
