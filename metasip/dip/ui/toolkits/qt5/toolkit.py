# Copyright (c) 2020 Riverbank Computing Limited.
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


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
        QDialog, QDialogButtonBox, QDockWidget, QDoubleSpinBox, QFileDialog,
        QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLayout,
        QLineEdit, QListView, QMainWindow, QMessageBox, QMenu, QMenuBar,
        QPushButton, QSpinBox, QSplitter, QStyle, QTabWidget, QTextEdit,
        QToolButton, QTreeView, QVBoxLayout, QWhatsThis, QWidget, QWizard,
        QWizardPage)

from ...toolkits import AbstractUIToolkit

from .exceptions import Qt5ToplevelWidgetError
from .utils import as_QLayout, as_QWidget, as_QWidget_parent


class Toolkit(AbstractUIToolkit):
    """ The Toolkit class implements the toolkit-specific UI support. """

    def action(self, parent):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface.

        :param parent:
            is the optional parent view.
        :return:
            the action.
        """

        return QAction(parent)

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

        app = QApplication.instance()

        if app is None:
            app = QApplication(argv, **properties)

        return app

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

        return QCheckBox()

    def close_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle closing an object.

        :return:
            the action.
        """

        return QAction("&Close", None, shortcut=QKeySequence.Close)

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

        return QComboBox()

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

        if not top_level:
            raise Qt5ToplevelWidgetError('QDialog')

        dialog = QDialog(as_QWidget_parent(parent))

        layout = QVBoxLayout()
        layout.addWidget(QDialogButtonBox())
        dialog.setLayout(layout)

        return dialog

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

        return QDockWidget()

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

        parent = as_QWidget_parent(parent)

        if detail != '':
            msg_box = QMessageBox(QMessageBox.Critical, title, text,
                    parent=parent, detailedText=detail)
            msg_box.exec()
        else:
            QMessageBox.critical(parent, title, text)

    def filesystem_location_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IFilesystemLocationEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.  Any factory properties will be applied to an internal
            :class:`~PyQt5.QtWidgets.QLineEdit`.
        """

        return self._tk_location_editor(top_level)

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

        if toolkit_root.objectName() == id:
            return toolkit_root

        widget = toolkit_root.findChild(QWidget, id)

        if widget is None:
            raise NameError("{0} has no QLayout or QWidget with an object "
                    "name of '{1}'".format(toolkit_root, id))

        return widget

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

        return QDoubleSpinBox()

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

        if top_level:
            view = QWidget()
            view.setLayout(QFormLayout())
        else:
            view = QFormLayout()

        return view

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

        return QFileDialog.getOpenFileName(as_QWidget_parent(parent), title,
                directory, filter)[0]

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

        return QFileDialog.getSaveFileName(as_QWidget_parent(parent), title,
                directory, filter)[0]

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

        if top_level:
            view = QWidget()
            view.setLayout(QGridLayout())
        else:
            view = QGridLayout()

        return view

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

        return QGroupBox()

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

        if top_level:
            view = QWidget()
            view.setLayout(QHBoxLayout())
        else:
            view = QHBoxLayout()

        return view

    def information(self, title, text, parent):
        """ Display a informational message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the message.
        :param parent:
            is the optional parent view.
        """

        QMessageBox.information(as_QWidget_parent(parent), title, text)

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

        return QLabel()

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

        return QLineEdit()

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

        return QTreeView()

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

        return QMainWindow()

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

        return QMenu()

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

        return QMenuBar()

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

        return QLabel(styleSheet='color: red', wordWrap=True)

    def new_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle creating a new object.

        :return:
            the action.
        """

        return QAction("&New...", None, shortcut=QKeySequence.New)

    def open_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle opening an object.

        :return:
            the action.
        """

        return QAction("&Open...", None, shortcut=QKeySequence.Open)

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

        return QListView()

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

        return QPushButton()

    # The map of dip message box buttons to the Qt equivalents.
    _button_map = {'yes': QMessageBox.Yes, 'no': QMessageBox.No,
            'cancel': QMessageBox.Cancel, 'save': QMessageBox.Save,
            'discard': QMessageBox.Discard}

    @classmethod
    def _qbutton_from_button(cls, button):
        """ Return the Qt standard button from the given button name. """

        try:
            return cls._button_map[button]
        except KeyError:
            raise ValueError("invalid button '{0}'".format(button))

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

        parent = as_QWidget_parent(parent)

        # Configure the buttons.
        qbuttons = 0
        qdefault = 0
        for button in buttons:
            qbutton = self._qbutton_from_button(button)
            qbuttons |= qbutton

            if qdefault == 0:
                qdefault = qbutton

        if detail != '':
            msg_box = QMessageBox(QMessageBox.Question, title, text, qbuttons,
                    parent, detailedText=detail)
            msg_box.setDefaultButton(qdefault)
            answer = msg_box.exec()
        else:
            answer = QMessageBox.question(parent, title, text, qbuttons,
                    qdefault)

        for button, qbutton in self._button_map.items():
            if qbutton == answer:
                return button

        # This should never happen.
        raise ValueError("unexpected Qt button: {0}".format(answer))

    def quit_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle quitting the application.

        :return:
            the action.
        """

        return QAction("&Quit", None, menuRole=QAction.QuitRole,
                shortcut=QKeySequence.Quit)

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

        layout = QVBoxLayout()

        # Make sure the buttons are together.
        layout.addStretch()

        if top_level:
            view = QWidget()
            view.setLayout(layout)
        else:
            view = layout

        return view

    def save_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle saving an object.

        :return:
            the action.
        """

        return QAction("&Save", None, shortcut=QKeySequence.Save)

    def save_as_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle saving an object under a
        new name.

        :return:
            the action.
        """

        return QAction("Save &As...", None, shortcut=QKeySequence.SaveAs)

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

        return QSpinBox()

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

        return QSplitter()

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

        return QTabWidget()

    def storage_location_editor(self, parent, top_level):
        """ Create an editor that can be adapted to the
        :class:`~dip.ui.IStorageLocationEditor` interface.

        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the editor.  Any factory properties will be applied to an internal
            :class:`~PyQt5.QtWidgets.QLineEdit`.
        """

        return self._tk_location_editor(top_level)

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

        return QTreeView()

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

        return QTextEdit()

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

        return QToolButton()

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

        if top_level:
            view = QWidget()
            view.setLayout(QVBoxLayout())
        else:
            view = QVBoxLayout()

        return view

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

        parent = as_QWidget_parent(parent)

        if detail != '':
            msg_box = QMessageBox(QMessageBox.Warning, title, text,
                    parent=parent, detailedText=detail)
            msg_box.exec()
        else:
            QMessageBox.warning(parent, title, text)

    def whats_this_action(self):
        """ Create an action, i.e. an object that can be adapted to the
        :class:`~dip.ui.IAction` interface, to handle "What's This?".

        :return:
            the action.
        """

        return QWhatsThis.createAction()

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

        if not top_level:
            raise Qt5ToplevelWidgetError('QWizard')

        return QWizard(as_QWidget_parent(parent))

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

        return QWizardPage()

    def _tk_location_editor(self, top_level):
        """ Create a line editor with an associated browse button. """

        layout = QHBoxLayout()

        layout.addWidget(QLineEdit())
        layout.addWidget(QToolButton(
                icon=QApplication.style().standardIcon(QStyle.SP_DirIcon),
                toolTip="Browse"))

        if top_level:
            view = QWidget()
            view.setLayout(layout)
        else:
            view = layout

        return view
