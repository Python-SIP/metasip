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


""" The :mod:`dip.ui` module implements a :term:`toolkit` independent API for
defining a user interface declaratively.
"""


from .i_action import IAction
from .i_action_collection import IActionCollection
from .i_application import IApplication
from .i_box import IBox
from .i_check_box import ICheckBox
from .i_collection_editor import ICollectionEditor
from .i_combo_box import IComboBox
from .i_container import IContainer
from .i_dialog import IDialog, DialogButton
from .i_display import IDisplay
from .i_dock import IDock
from .i_editor import IEditor
from .i_filesystem_location_editor import IFilesystemLocationEditor
from .i_float_spin_box import IFloatSpinBox
from .i_form import IForm
from .i_grid import IGrid
from .i_group_box import IGroupBox
from .i_h_box import IHBox
from .i_label import ILabel
from .i_line_editor import ILineEditor
from .i_list_editor import IListEditor
from .i_main_window import IMainWindow
from .i_menu import IMenu
from .i_menu_bar import IMenuBar
from .i_message_area import IMessageArea
from .i_object import IObject
from .i_option_list import IOptionList
from .i_option_selector import IOptionSelector
from .i_push_button import IPushButton
from .i_radio_buttons import IRadioButtons
from .i_single_view_container import ISingleViewContainer
from .i_spin_box import ISpinBox
from .i_splitter import ISplitter
from .i_stack import IStack
from .i_table_editor import ITableEditor
from .i_text_editor import ITextEditor
from .i_tool_button import IToolButton
from .i_v_box import IVBox
from .i_validator import IValidator
from .i_view import IView
from .i_wizard import IWizard
from .i_wizard_page import IWizardPage

from .action import Action
from .action_collection import ActionCollection
from .application import Application
from .bindings import Bindings
from .box_layout_factory import BoxLayoutFactory
from .check_box import CheckBox
from .collection_validator import CollectionValidator
from .combo_box import ComboBox
from .container_factory import ContainerFactory
from .controller import Controller
from .dialog import Dialog
from .dialog_controller import DialogController
from .dock import Dock
from .editor_factory import EditorFactory
from .filesystem_location_editor import FilesystemLocationEditor
from .filesystem_location_validator import FilesystemLocationValidator
from .float_spin_box import FloatSpinBox
from .form import Form
from .grid import Grid
from .group_box import GroupBox
from .h_box import HBox
from .label import Label
from .line_editor import LineEditor
from .list_column import ListColumn
from .list_editor import ListEditor
from .main_window import MainWindow
from .menu import Menu
from .menu_bar import MenuBar
from .message_area import MessageArea
from .option_list import OptionList
from .option_selector_factory import OptionSelectorFactory
from .option_validator import OptionValidator
from .push_button import PushButton
from .radio_buttons import RadioButtons
from .single_subview_container_factory import SingleSubviewContainerFactory
from .spin_box import SpinBox
from .splitter import Splitter
from .stack import Stack
from .stretch import Stretch
from .string_validator import StringValidator
from .table_column import TableColumn
from .table_editor import TableEditor
from .text_editor import TextEditor
from .tool_button import ToolButton
from .v_box import VBox
from .view_factory import ViewFactory
from .wizard import Wizard
from .wizard_controller import WizardController
from .wizard_page import WizardPage

from .toolkits import UIToolkit

# Make sure the toolkit adapters get registered.
UIToolkit.application
