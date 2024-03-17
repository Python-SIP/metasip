# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass
from typing import Callable, Optional

from PyQt6.QtCore import QByteArray, QMimeData, Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (QApplication, QMenu, QMessageBox, QProgressDialog,
        QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from ....models import (Access, Class, Constructor, Destructor, Enum,
        EnumValue, ExtendedAccess, Function, ManualCode, Method, Module,
        Namespace, OperatorCast, OpaqueClass, OperatorFunction, OperatorMethod,
        Tagged, Typedef, Variable, VersionRange)
from ....models.adapters import adapt

from ...helpers import warning

from .dialogs import (ArgumentPropertiesDialog, CallablePropertiesDialog,
        ClassPropertiesDialog, EnumPropertiesDialog,
        EnumMemberPropertiesDialog, FeaturesDialog, ManualCodeDialog,
        ModulePropertiesDialog, MoveHeaderDialog, NamespacePropertiesDialog,
        OpaqueClassPropertiesDialog, PlatformsDialog, ProjectPropertiesDialog,
        TypedefPropertiesDialog, VariablePropertiesDialog, VersionsDialog)

from .external_editor import ExternalEditor


class ApiEditor(QTreeWidget):
    """ This class implements the API editor. """

    MIME_FORMAT = 'application/x-item'

    # The column numbers.
    (NAME, ACCESS, STATUS, VERSIONS) = range(4)

    def __init__(self, shell):
        """ Initialise the editor. """

        super().__init__()

        self._shell = shell
        self._project_view = None

        # Tweak the tree widget.
        self.setHeaderLabels(("Name", "Access", "Status", "Versions"))
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)

        self.dragged = None

    def api_status(self, api):
        """ Handle the change of status of an API. """

        for view in self._all_views():
            if view.api is api:
                view.draw_status()
                break

    def api_versions(self, api):
        """ Handle the change of versions of an API. """

        for view in self._all_views():
            if view.api is api:
                view.draw_versions()
                break

    def container_api_add(self, container, api):
        """ Handle the addition of an API to a container. """

        for view in self._all_views():
            if view.api is container:
                view.api_add(api)
                break

    def container_api_delete(self, container, api):
        """ Handle the deletion of an API from a container. """

        for view in self._all_views():
            if view.api is container:
                view.api_delete(api)
                break

    def module_add(self, module):
        """ Handle the addition of a module. """

        self._project_view.module_add(module)

    def module_delete(self, module):
        """ Handle the deletion of a module. """

        self._project_view.module_delete(module)

    def module_rename(self, module):
        """ A module has been renamed. """

        self._project_view.module_rename(module)

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('header')
        if state is not None:
            self.header().restoreState(state)

    def set_project(self):
        """ Set the current project. """

        self.clear()
        self._project_view = ProjectView(self._shell, self)

    def root_module_updated(self):
        """ The name of the root module has been updated. """

        self._project_view.root_module_updated()

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('header', self.header().saveState())

    def contextMenuEvent(self, ev):
        """ Reimplemented to handle a context menu event. """

        # Find the view.
        view = self.itemAt(ev.pos())

        if view:
            # Get the list of siblings that are also selected.
            siblings = []

            parent = view.parent()
            if parent is not None:
                for sibling in parent.all_child_views():
                    if sibling is not view and sibling.isSelected() and not sibling.isHidden():
                        siblings.append(sibling)

            # Check it has a menu.
            options = view.get_menu(siblings)

            if options:
                # Create the menu.
                menu = QMenu()

                for option in options:
                    if option is None:
                        menu.addSeparator()
                        continue

                    action = menu.addAction(option.text, option.handler)

                    action.setEnabled(option.enabled)

                    if option.checked is not None:
                        action.setCheckable(True)
                        action.setChecked(option.checked)

                menu.exec(ev.globalPos())

                ev.accept()
                return

        super().contextMenuEvent(ev)

    def startDrag(self, actions):
        """ Reimplemented to start the drag of a view. """

        # Find the selected view.
        dragging = None

        it = QTreeWidgetItemIterator(self,
                QTreeWidgetItemIterator.IteratorFlag.Selected)
        itm = it.value()

        while itm is not None:
            # We can only drag one view.
            if dragging is not None:
                return

            dragging = itm

            it += 1
            itm = it.value()

        # Make sure there was something to drag.
        if dragging is None:
            return

        # Serialize the id() of the view being dragged.
        data = QByteArray.number(dragging.type())
        mime = QMimeData()
        mime.setData(self.MIME_FORMAT, data)

        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec()

    def dragEnterEvent(self, ev):
        """ Reimplemented to validate a drag enter. """

        if ev.source() is self:
            ev.accept()
        else:
            ev.ignore()

    def dragMoveEvent(self, ev):
        """ Reimplemented to validate a drag move. """

        if ev.source() is self:
            ev.accept()
        else:
            ev.ignore()

    def dropEvent(self, ev):
        """ Reimplemented to handle a drop. """

        source_target = self._source_target(ev)

        if source_target is None:
            ev.ignore()
        else:
            source, target = source_target
            target.drop(source)
            ev.accept()

    def _source_target(self, ev):
        """ Return a 2-tuple of source and target views or None if the drop
        wasn't appropriate.
        """

        # Get the target.
        target = self.itemAt(ev.position().toPoint())

        # Check that the payload is a view.
        mime = ev.mimeData()
        if not mime.hasFormat(self.MIME_FORMAT):
            return None

        # Get the view from the payload.
        source_id = int(mime.data(self.MIME_FORMAT))
        source = None

        it = QTreeWidgetItemIterator(self,
                QTreeWidgetItemIterator.IteratorFlag.DragEnabled)
        itm = it.value()

        while itm is not None:
            if itm.type() == source_id:
                source = itm
                break

            it += 1
            itm = it.value()

        if source is None or source is target:
            return None

        # Ask the target if it can handle the source.
        if not (isinstance(target, DropSite) and target.droppable(source)):
            return None

        return source, target

    def _all_views(self, container_view=None):
        """ A generator for all API views. """

        if container_view is None:
            container_view = self._project_view

        for view in container_view.all_child_views():
            yield view

            for sub_view in self._all_views(view):
                yield sub_view


@dataclass
class MenuOption:
    """ This class specifies a menu option. """

    # The option text.
    text: str

    # The option handler.
    handler: Callable

    # Set if the option is checked.
    checked: Optional[bool] = None

    # Set if the option is enabled.
    enabled: bool = True


class DropSite:
    """ This mixin class implements a drop site.  Any derived class must also
    derive QTreeWidgetItem.
    """

    def __init__(self):
        """ Initialise the instance. """

        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsDropEnabled)

    def droppable(self, view):
        """ Return True if a view can be dropped. """

        raise NotImplementedError

    def drop(self, view):
        """ Handle the drop of a view. """

        raise NotImplementedError


# Each QTreeWidgetItem has a unique key used in the DND support.
_view_id = QTreeWidgetItem.ItemType.UserType


class APIView(QTreeWidgetItem):
    """ This class represents the view of an API in the editor. """

    def __init__(self, api, shell, parent, after=None):
        """ Initialise the view. """

        global _view_id
        view_id = _view_id
        _view_id += 1

        if after is parent:
            super().__init__(parent, None, view_id)
        elif after is None:
            super().__init__(parent, view_id)
        else:
            super().__init__(parent, after, view_id)

        self.api = api
        self.shell = shell

    def all_child_views(self):
        """ A generator for all the views's children. """

        for index in range(self.childCount()):
            yield self.child(index)

    def api_add(self, api):
        """ An API has been added. """

        # The order of views must match the order of APIs.
        index = self.api.content.index(api)
        after = self if index == 0 else self.child(index - 1)
        self.get_child_factory()(api, self.shell, self, after)

    def api_delete(self, api):
        """ An API has been deleted. """

        for view in self.all_child_views():
            if view.api is api:
                self.removeChild(view)
                break

    def api_as_str(self):
        """ Returns the API as a string for display purposes. """

        return adapt(self.api).as_str()

    def get_child_factory(self):
        """ Return the callable that will return a child instance. """

        raise NotImplementedError

    def get_menu(self, siblings):
        """ Return the list of context menu options or None if the view doesn't
        have a context menu.  Each element is a 3-tuple of the text of the
        option, the bound method that handles the option, and a flag that is
        True if the option should be enabled.
        """

        # This default implementation doesn't have a menu.
        return None


class ProjectView(APIView):
    """ This class implements a view of a project. """

    def __init__(self, shell, parent):
        """ Initialise the project view. """

        super().__init__(shell.project, shell, parent)

        self.root_module_updated()
        self.setExpanded(True)

        project = self.api

        # Progress will be reported against .sip files so count them all.
        nr_steps = 0
        for module in project.modules:
            nr_steps += len(module.content)

        # Display the progress dialog.
        progress = QProgressDialog("Building the GUI...", None, 0, nr_steps)
        progress.setWindowTitle(project.name)
        progress.setValue(0)

        so_far = 0
        for module in project.modules:
            ModuleView(module, self.shell, self)

            so_far += len(module.content)
            progress.setValue(so_far)
            QApplication.processEvents()

        self._sort()

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        if siblings:
            return None

        return [MenuOption("Properties...", self._handle_project_properties)]

    def module_add(self, module):
        """ Handle the addition of a module. """

        ModuleView(module, self.shell, self)
        self._sort()

    def module_delete(self, module):
        """ Handle the deletion of a module. """

        for view in self.all_child_views():
            if view.api is module:
                self.removeChild(view)
                break

    def module_rename(self, module):
        """ A module has been renamed. """

        for view in self.all_child_views():
            if view.api is module:
                view.setText(ApiEditor.NAME, module.name)
                break

        self._sort()

    def root_module_updated(self):
        """ The name of the root module has been updated. """

        name = self.shell.project.rootmodule
        if name == '':
            name = "Modules"

        self.setText(ApiEditor.NAME, name)

    def _handle_project_properties(self):
        """ Handle the project's properties. """

        dialog = ProjectPropertiesDialog(self.shell.project,
                "Project Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True

    def _sort(self):
        """ Sort the modules. """

        self.sortChildren(ApiEditor.NAME, Qt.SortOrder.AscendingOrder)


class ModuleView(APIView, DropSite):
    """ This class implements a view of a module. """

    def __init__(self, module, shell, parent):
        """ Initialise the module view. """

        super().__init__(module, shell, parent)

        self.setText(ApiEditor.NAME, module.name)

        for sip_file in module.content:
            SipFileView(sip_file, self.shell, self)

    def droppable(self, view):
        """ Return True if a view can be dropped. """

        # We allow .sip files to be moved around anywhere.
        return isinstance(view, SipFileView)

    def drop(self, view):
        """ Handle the drop of a view. """

        view_parent = view.parent()

        # Remove the view from its parent and the API item from its container.
        api = view.api
        view_parent.api.content.remove(api)
        view_parent.removeChild(view)

        # The .sip file is always placed at the top.
        self.api.content.insert(0, api)
        self.insertChild(0, view)

        self.shell.dirty = True

    def get_child_factory(self):
        """ Return the callable that will return a child view. """

        return SipFileView

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        if siblings:
            return None

        return [MenuOption("Properties...", self._handle_module_properties)]

    def _handle_module_properties(self):
        """ Handle the module's properties. """

        dialog = ModulePropertiesDialog(self.api, "Module Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True


class ContainerView(APIView, DropSite):
    """ This class implements a view of a potential container for code. """

    # The current external editor objects.
    editors = {}

    def __init__(self, container, shell, parent, after):
        """ Initialise the container view. """

        super().__init__(container, shell, parent, after)

        if hasattr(container, 'content'):
            for code in container.content:
                CodeView(code, self.shell, self)

    @classmethod
    def add_editor_option(cls, menu, name, handler, value, editor_id):
        """ Add the option that will invoke the external editor to a menu. """

        menu.append(
                MenuOption(name + '...', handler, checked=(value != ''),
                        enabled=(editor_id not in cls.editors)))

    def droppable(self, view):
        """ Return True if a view can be dropped. """

        parent = self.parent()
        view_parent = view.parent()

        # See if we are moving a sibling.
        if view_parent is parent:
            return True

        # See if we are moving a child to the top.
        if view_parent is self:
            return True

        return False

    def drop(self, view):
        """ Handle the drop of a view. """

        parent = self.parent()
        view_parent = view.parent()

        # Remove the view from its parent and the API item from its container.
        api = view.api
        view_parent.api.content.remove(api)
        view_parent.removeChild(view)

        if view_parent is parent:
            # We are moving a sibling after us.
            parent_content = parent.api.content

            new_idx = parent_content.index(self.api) + 1
            if new_idx < len(parent_content):
                parent_content.insert(new_idx, api)
                parent.insertChild(new_idx, view)
            else:
                parent_content.append(api)
                parent.addChild(view)

        elif view_parent is self:
            # Dropping a child is interpreted as moving it to the top.
            self.api.content.insert(0, api)
            self.insertChild(0, view)

        self.shell.dirty = True

    def get_child_factory(self):
        """ Return the callable that will return a child instance. """

        return CodeView

    def new_manual_code(self):
        """ Return a new ManualCode object appropriately configured. """

        manual_code = ManualCode(status='unknown')

        project_versions = self.shell.project.versions
        if project_versions:
            manual_code.versions.append(
                    VersionRange(startversion=project_versions[-1]))

        return manual_code


class SipFileView(ContainerView):
    """ This class implements a view of a .sip file. """

    def __init__(self, sip_file, shell, parent, after=None):
        """ Initialise the .sip file view. """

        super().__init__(sip_file, shell, parent, after)

        self._targets = []

        self.setText(ApiEditor.NAME, sip_file.name)

    def droppable(self, view):
        """ Return True if a view can be dropped. """

        # See if we are moving another .sip file.
        if isinstance(view, SipFileView):
            return True

        # See if we are moving a child to the top.
        if view.parent() is self:
            return True

        return False

    def drop(self, view):
        """ Handle the drop of a view. """

        parent = self.parent()
        view_parent = view.parent()

        # Remove the view from its parent and the API item from its container.
        api = view.api
        view_parent.api.content.remove(api)
        view_parent.removeChild(view)

        if isinstance(view, SipFileView):
            # We are moving a sibling after us.
            parent_content = parent.api.content

            new_idx = parent_content.index(self.api) + 1
            if new_idx < len(parent_content):
                parent_content.insert(new_idx, api)
                parent.insertChild(new_idx, view)
            else:
                parent_content.append(api)
                parent.addChild(view)

        elif view_parent is self:
            # Dropping a child is interpreted as moving it to the top.
            self.api.content.insert(0, api)
            self.insertChild(0, view)

        self.shell.dirty = True

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        if siblings:
            return None

        multiple_modules = (len(self.shell.project.modules) > 0)

        empty_sipfile = True
        for code in self.api.content:
            if code.status != 'ignored':
                empty_sipfile = False
                break

        menu = []

        menu.append(MenuOption("Hide Ignored", self._hideIgnoredSlot)),
        menu.append(MenuOption("Show Ignored", self._showIgnoredSlot)),
        menu.append(None)
        menu.append(
                MenuOption("Add manual code...",
                        self._handle_add_manual_code))
        menu.append(None)
        self.add_editor_option(menu, "%ExportedHeaderCode",
                self._exportedHeaderCodeSlot, self.api.exportedheadercode,
                'ehc')
        self.add_editor_option(menu, "%ModuleHeaderCode",
                self._moduleHeaderCodeSlot, self.api.moduleheadercode, 'mhc')
        self.add_editor_option(menu, "%ModuleCode", self._moduleCodeSlot,
                self.api.modulecode, 'moc')
        self.add_editor_option(menu, "%PreInitialisationCode",
                self._preInitCodeSlot, self.api.preinitcode, 'pric')
        self.add_editor_option(menu, "%InitialisationCode", self._initCodeSlot,
                self.api.initcode, 'ic')
        self.add_editor_option(menu, "%PostInitialisationCode",
                self._postInitCodeSlot, self.api.postinitcode, 'poic')
        menu.append(None)
        self.add_editor_option(menu, "%ExportedTypeHintCode",
                self._exportedTypeHintCodeSlot, self.api.exportedtypehintcode,
                'ethc')
        self.add_editor_option(menu, "%TypeHintCode", self._typeHintCodeSlot,
                self.api.typehintcode, 'thc')
        menu.append(None)
        menu.append(MenuOption("Move to...", self._handle_move,
                enabled=multiple_modules))
        menu.append(MenuOption("Delete", self._deleteFile,
                enabled=empty_sipfile))

        return menu

    def _handle_move(self):
        """ Move a .sip file to a different module. """

        src_module = self.parent().api

        dialog = MoveHeaderDialog(src_module, "Move Header File", self.shell)

        dst_module = dialog.get_destination_module()
        if dst_module is not None:
            # Mark as dirty before moving it.
            self.shell.dirty = True

            src_module.content.remove(self.api)
            dst_module.content.append(self.api)

    def _deleteFile(self):
        """ Delete an empty .sip file. """

        ans = QMessageBox.question(self.treeWidget(), "Delete header file",
                "Are you sure you want to delete this header file?",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

        if ans is QMessageBox.StandardButton.Yes:
            # Mark as dirty before removing it.
            self.shell.dirty = True

            parent = self.parent()
            parent.api.content.remove(self.api)
            parent.removeChild(self)

    def _handle_add_manual_code(self):
        """ Slot to handle the creation of manual code. """

        manual_code = self.new_manual_code()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code", self.shell)

        if dialog.update():
            CodeView(manual_code, self.shell, self, after=self)

            self.api.content.insert(0, manual_code)
            self.shell.dirty = True

    def _exportedHeaderCodeSlot(self):
        """ Slot to handle %ExportedHeaderCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._exportedHeaderCodeDone)
        ed.edit(self.api.exportedheadercode, "%ExportedHeaderCode: " + self.api.name)
        self.editors['ehc'] = ed

    def _exportedHeaderCodeDone(self, text_changed, text):
        """ Slot to handle changed %ExportedHeaderCode. """

        if text_changed:
            self.api.exportedheadercode = text
            self.shell.dirty = True

        del self.editors['ehc']

    def _moduleHeaderCodeSlot(self):
        """ Slot to handle %ModuleHeaderCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._moduleHeaderCodeDone)
        ed.edit(self.api.moduleheadercode, "%ModuleHeaderCode: " + self.api.name)
        self.editors['mhc'] = ed

    def _moduleHeaderCodeDone(self, text_changed, text):
        """ Slot to handle changed %ModuleHeaderCode. """

        if text_changed:
            self.api.moduleheadercode = text
            self.shell.dirty = True

        del self.editors['mhc']

    def _moduleCodeSlot(self):
        """ Slot to handle %ModuleCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._moduleCodeDone)
        ed.edit(self.api.modulecode, "%ModuleCode: " + self.api.name)
        self.editors['moc'] = ed

    def _moduleCodeDone(self, text_changed, text):
        """ Slot to handle changed %ModuleCode. """

        if text_changed:
            self.api.modulecode = text
            self.shell.dirty = True

        del self.editors['moc']

    def _preInitCodeSlot(self):
        """ Slot to handle %PreInitialisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._preInitCodeDone)
        ed.edit(self.api.preinitcode, "%PreInitialisationCode: " + self.api.name)
        self.editors['pric'] = ed

    def _preInitCodeDone(self, text_changed, text):
        """ Slot to handle changed %PreInitialisationCode. """

        if text_changed:
            self.api.preinitcode = text
            self.shell.dirty = True

        del self.editors['pric']

    def _initCodeSlot(self):
        """ Slot to handle %InitialisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._initCodeDone)
        ed.edit(self.api.initcode, "%InitialisationCode: " + self.api.name)
        self.editors['ic'] = ed

    def _initCodeDone(self, text_changed, text):
        """ Slot to handle changed %InitialisationCode. """

        if text_changed:
            self.api.initcode = text
            self.shell.dirty = True

        del self.editors['ic']

    def _postInitCodeSlot(self):
        """ Slot to handle %PostInitialisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._postInitCodeDone)
        ed.edit(self.api.postinitcode, "%PostInitialisationCode: " + self.api.name)
        self.editors['poic'] = ed

    def _postInitCodeDone(self, text_changed, text):
        """ Slot to handle changed %PostInitialisationCode. """

        if text_changed:
            self.api.postinitcode = text
            self.shell.dirty = True

        del self.editors['poic']

    def _exportedTypeHintCodeSlot(self):
        """ Slot to handle %ExportedTypeHintCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._exportedTypeHintCodeDone)
        ed.edit(self.api.exportedtypehintcode, "%ExportedTypeHintCode: " + self.api.name)
        self.editors['ethc'] = ed

    def _exportedTypeHintCodeDone(self, text_changed, text):
        """ Slot to handle changed %ExportedTypeHintCode. """

        if text_changed:
            self.api.exportedtypehintcode = text
            self.shell.dirty = True

        del self.editors['ethc']

    def _typeHintCodeSlot(self):
        """ Slot to handle %TypeHintCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typeHintCodeDone)
        ed.edit(self.api.typehintcode, "%TypeHintCode: " + self.api.name)
        self.editors['thc'] = ed

    def _typeHintCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeHintCode. """

        if text_changed:
            self.api.typehintcode = text
            self.shell.dirty = True

        del self.editors['thc']

    def _hideIgnoredSlot(self):
        """ Hide all ignored scope elements. """

        self._setIgnoredVisibility(False)

    def _showIgnoredSlot(self):
        """ Show all ignored scope elements. """

        self._setIgnoredVisibility(True)

    def _setIgnoredVisibility(self, visible):
        """ Set the visibility of all ignored scope elements. """

        it = QTreeWidgetItemIterator(self)
        itm = it.value()

        while itm:
            if isinstance(itm, CodeView) and itm.api.status == "ignored":
                itm.setHidden(not visible)

            it += 1
            itm = it.value()


class ArgumentView(APIView):
    """ This class implements a view of a function argument. """

    def __init__(self, argument, shell, parent):
        """ Initialise the argument view. """

        super().__init__(argument, shell, parent)

        self.setFlags(Qt.ItemFlag.ItemIsEnabled)

        self.draw_name()

        # Stash this so that an argument can re-draw itself.
        argument._view = self

    def draw_name(self):
        """ Draw the name column. """

        self.setText(ApiEditor.NAME, self.api_as_str())

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        if siblings:
            return None

        return [MenuOption("Properties...", self._handle_argument_properties)]

    def _handle_argument_properties(self):
        """ Slot to handle the argument's properties. """

        dialog = ArgumentPropertiesDialog(self.api, "Argument Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True

            self.draw_name()
            self.parent().draw_name()
            self.parent().draw_status()


class CodeView(ContainerView):
    """ This class implements a view of code in a .sip file. """

    def __init__(self, code, shell, parent, after=None):
        """ Initialise the code view. """

        super().__init__(code, shell, parent, after)

        self._targets = []

        self.draw_name()
        self._draw_access()
        self.draw_status()
        self.draw_versions()

        if code.status == 'ignored':
            self.setHidden(True)

        # Create any children.
        if hasattr(code, 'args'):
            for arg in code.args:
                ArgumentView(arg, self.shell, self)

    def draw_name(self):
        """ Update the item's name. """

        self.setText(ApiEditor.NAME, self.api_as_str())

    def _draw_access(self):
        """ Update the item's access. """

        # Not everything has an access specifier.
        try:
            access = self.api.access
        except AttributeError:
            access = ''

        self.setText(ApiEditor.ACCESS, access)

    def _has_unnamed_args(self):
        """ Returns ``True`` if the code has unnamed arguments. """

        # These types don't use named arguments.
        if isinstance(self.api, (OperatorMethod, OperatorCast, OperatorFunction)):
            return False

        # Ignore private items.
        try:
            private = (self.api.access == 'private')
        except AttributeError:
            private = False

        if private:
            return False

        for arg in self.api.args:
            if arg.unnamed and arg.default != '':
                return True

        return False

    def draw_status(self):
        """ Update the item's status. """

        status = []

        expand = False
        s = self.api.status

        if s == 'removed':
            text = "Removed"
            expand = True
        elif s == 'todo':
            text = "Todo"
            expand = True
        elif s == 'unknown':
            text = "Unchecked"
            expand = True
        elif s == 'ignored':
            text = "Ignored"
        else:
            text = ''

        if text:
            status.append(text)

        if s != 'ignored' and hasattr(self.api, 'args') and self._has_unnamed_args():
            status.append("Unnamed arguments")
            expand = True

        self.setText(ApiEditor.STATUS, ", ".join(status))

        if expand:
            parent = self.parent()
            while parent is not None:
                if isinstance(parent, CodeView):
                    if parent.api.status == 'ignored':
                        break

                parent.setExpanded(True)
                parent = parent.parent()

    def draw_versions(self):
        """ Update the item's versions. """

        self.setText(ApiEditor.VERSIONS,
                adapt(self.api, Tagged).versions_as_str())

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        project = self.shell.project

        # Save the list of targets for the menu action, including this one.
        self._targets = siblings[:]
        self._targets.append(self)

        menu = []

        # Handle the workflow.
        menu.append(
                MenuOption("Checked", self._setStatusChecked,
                        checked=(self.api.status == '')))
        menu.append(
                MenuOption("Todo", self._setStatusTodo,
                        checked=(self.api.status == 'todo')))
        menu.append(
                MenuOption("Unchecked", self._setStatusUnchecked,
                        checked=(self.api.status == 'unknown')))
        menu.append(
                MenuOption("Ignored", self._setStatusIgnored,
                        checked=(self.api.status == 'ignored')))

        menu.append(None)
        self.add_editor_option(menu, "Comments", self._handle_comments,
                self.api.comments, 'comments')

        # Handle the access specifiers.
        if isinstance(self.api, (Access, ExtendedAccess)):
            menu.append(None)
            menu.append(
                    MenuOption("public", self._setAccessPublic,
                            checked=(self.api.access == '')))

            if isinstance(self.api, ExtendedAccess):
                menu.append(
                        MenuOption("public slots", self._setAccessPublicSlots,
                                checked=(self.api.access == 'public slots')))

            menu.append(
                    MenuOption("protected", self._setAccessProtected,
                            checked=(self.api.access == 'protected')))

            if isinstance(self.api, ExtendedAccess):
                menu.append(
                        MenuOption("protected slots",
                                self._setAccessProtectedSlots,
                                checked=(self.api.access == 'protected slots')))

            menu.append(
                    MenuOption("private", self._setAccessPrivate,
                            checked=(self.api.access == 'private')))

            if isinstance(self.api, ExtendedAccess):
                menu.append(
                        MenuOption("private slots",
                                self._setAccessPrivateSlots,
                                checked=(self.api.access == 'private slots')))
                menu.append(
                        MenuOption("signals", self._setAccessSignals,
                                checked=(self.api.access == 'signals')))

        if siblings:
            if project.versions:
                menu.append(None)
                menu.append(MenuOption("Versions...", self._handle_versions))

            menu.append(None)
            menu.append(
                    MenuOption("Delete", self._deleteCode,
                            enabled=(not self.editors)))

            return menu

        # Handle the manual code part of the menu.
        menu.append(None)
        menu.append(
                MenuOption("Add manual code...", self._handle_add_manual_code))

        # See what extra menu items are needed.
        thcslot = False
        thicslot = False
        tcslot = False
        cttcslot = False
        cftcslot = False
        mcslot = False
        vccslot = False
        fcslot = False
        sccslot = False
        acslot = False
        gcslot = False
        scslot = False
        gctcslot = False
        gcccslot = False
        bigetbslot = False
        birelbslot = False
        birbslot = False
        biwbslot = False
        biscslot = False
        bicbslot = False
        pickslot = False
        xaslot = False
        properties_handler = None
        dsslot = None

        if isinstance(self.api, ManualCode):
            menu.append(
                    MenuOption("Modify manual code...",
                            self._handle_modify_manual_code))
            menu.append(
                    MenuOption("Modify manual code body...",
                            self._bodyManualCode,
                            checked=(self.api.body != ''),
                            enabled=('mcb' not in self.editors)))

            mcslot = True
            properties_handler = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, Namespace):
            properties_handler = self._handle_namespace_properties
        elif isinstance(self.api, OpaqueClass):
            properties_handler = self._handle_opaque_class_properties
        elif isinstance(self.api, Namespace):
            thcslot = True
        elif isinstance(self.api, Class):
            thcslot = True
            thicslot = True
            tcslot = True
            cttcslot = True
            cftcslot = True
            fcslot = True
            sccslot = True
            gctcslot = True
            gcccslot = True
            bigetbslot = True
            birelbslot = True
            birbslot = True
            biwbslot = True
            biscslot = True
            bicbslot = True
            pickslot = True
            xaslot = True
            properties_handler = self._handle_class_properties
            dsslot = True
        elif isinstance(self.api, Constructor):
            mcslot = True
            properties_handler = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, Destructor):
            mcslot = True
            vccslot = True
            properties_handler = self._handle_callable_properties
        elif isinstance(self.api, OperatorCast):
            mcslot = True
            properties_handler = self._handle_callable_properties
        elif isinstance(self.api, Method):
            mcslot = True

            if self.api.virtual:
                vccslot = True

            properties_handler = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, OperatorMethod):
            mcslot = True

            if self.api.virtual:
                vccslot = True

            properties_handler = self._handle_callable_properties
        elif isinstance(self.api, Function):
            mcslot = True
            properties_handler = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, OperatorFunction):
            mcslot = True
            properties_handler = self._handle_callable_properties
        elif isinstance(self.api, Typedef):
            properties_handler = self._handle_typedef_properties
            dsslot = True
        elif isinstance(self.api, Variable):
            acslot = True
            gcslot = True
            scslot = True
            properties_handler = self._handle_variable_properties
        elif isinstance(self.api, Enum):
            properties_handler = self._handle_enum_properties
        elif isinstance(self.api, EnumValue):
            properties_handler = self._handle_enum_member_properties

        if thcslot or thicslot or tcslot or cttcslot or cftcslot or fcslot or sccslot or mcslot or vccslot or acslot or gcslot or scslot or gctcslot or gcccslot or bigetbslot or birelbslot or birbslot or biwbslot or biscslot or bicbslot or pickslot or xaslot or dsslot:
            menu.append(None)

            if thcslot:
                self.add_editor_option(menu, '%TypeHeaderCode',
                        self._typeheaderCodeSlot, self.api.typeheadercode,
                        'thc')

            if tcslot:
                self.add_editor_option(menu, '%TypeCode', self._typeCodeSlot,
                        self.api.typecode, 'tc')

            if thicslot:
                self.add_editor_option(menu, '%TypeHintCode',
                        self._typehintCodeSlot, self.api.typehintcode, 'thic')

            if fcslot:
                self.add_editor_option(menu, '%FinalisationCode',
                        self._finalCodeSlot, self.api.finalisationcode, 'fc')

            if sccslot:
                self.add_editor_option(menu, '%ConvertToSubClassCode',
                        self._subclassCodeSlot, self.api.subclasscode, 'scc')

            if cttcslot:
                self.add_editor_option(menu, '%ConvertToTypeCode',
                        self._convToTypeCodeSlot, self.api.convtotypecode,
                        'cttc')

            if cftcslot:
                self.add_editor_option(menu, '%ConvertFromTypeCode',
                        self._convFromTypeCodeSlot, self.api.convfromtypecode,
                        'cftc')

            if mcslot:
                self.add_editor_option(menu, '%MethodCode',
                        self._methodCodeSlot, self.api.methcode, 'mc')

            if vccslot:
                self.add_editor_option(menu, '%VirtualCatcherCode',
                        self._virtualCatcherCodeSlot, self.api.virtcode, 'vcc')

            if acslot:
                self.add_editor_option(menu, '%AccessCode',
                        self._accessCodeSlot, self.api.accesscode, 'ac')

            if gcslot:
                self.add_editor_option(menu, '%GetCode', self._getCodeSlot,
                        self.api.getcode, 'gc')

            if scslot:
                self.add_editor_option(menu, '%SetCode', self._setCodeSlot,
                        self.api.setcode, 'sc')

            if gctcslot:
                self.add_editor_option(menu, '%GCTraverseCode',
                        self._gcTraverseCodeSlot, self.api.gctraversecode,
                        'gctc')

            if gcccslot:
                self.add_editor_option(menu, '%GCClearCode',
                        self._gcClearCodeSlot, self.api.gcclearcode, 'gccc')

            if bigetbslot:
                self.add_editor_option(menu, '%BIGetBufferCode',
                        self._biGetBufCodeSlot, self.api.bigetbufcode,
                        'bigetb')

            if birelbslot:
                self.add_editor_option(menu, '%BIReleaseBufferCode',
                        self._biRelBufCodeSlot, self.api.birelbufcode,
                        'birelb')

            if birbslot:
                self.add_editor_option(menu, '%BIGetReadBufferCode',
                        self._biReadBufCodeSlot, self.api.bireadbufcode,
                        'birb')

            if biwbslot:
                self.add_editor_option(menu, '%BIGetWriteBufferCode',
                        self._biWriteBufCodeSlot, self.api.biwritebufcode,
                        'biwb')

            if biscslot:
                self.add_editor_option(menu, '%BIGetSegCountCode',
                        self._biSegCountCodeSlot, self.api.bisegcountcode,
                        'bisc')

            if bicbslot:
                self.add_editor_option(menu, '%BIGetCharBufferCode',
                        self._biCharBufCodeSlot, self.api.bicharbufcode,
                        'bicb')

            if pickslot:
                self.add_editor_option(menu, '%PickleCode',
                        self._pickleCodeSlot, self.api.picklecode, 'pick')

            if dsslot:
                self.add_editor_option(menu, '%Docstring', self._docstringSlot,
                        self.api.docstring, 'ds')

        if isinstance(self.api, (Constructor, Function, Method)):
            menu.append(None)
            menu.append(
                    MenuOption("Accept all argument names", self._acceptNames))

        if project.versions or project.platforms or project.features or project.externalfeatures:
            menu.append(None)

            if project.versions:
                menu.append(MenuOption("Versions...", self._handle_versions))

            if project.platforms:
                menu.append(
                        MenuOption("Platform Tags...", self._handle_platforms,
                                checked=bool(self.api.platforms)))

            if project.features or project.externalfeatures:
                menu.append(
                        MenuOption("Feature Tags...", self._handle_features,
                                checked=bool(self.api.features)))

        if properties_handler is not None:
            menu.append(MenuOption("Properties...", properties_handler))

        menu.append(None)
        menu.append(
                MenuOption("Delete", self._deleteCode,
                        enabled=(not self.editors)))

        return menu

    def _acceptNames(self):
        """ Accept all argument names. """

        updated = False

        for arg in self.api.args:
            if arg.unnamed and arg.default != '':
                arg.unnamed = False
                arg._view.draw_name()
                updated = True

        if updated:
            self.draw_name()
            self.draw_status()
            self.shell.dirty = True

    def _handle_comments(self):
        """ Slot to handle comments. """

        name = self.api.precis if isinstance(self.api, ManualCode) else self.api.name

        ed = ExternalEditor()
        ed.editDone.connect(self._handle_comments_done)
        ed.edit(self.api.comments, "Comments: " + name)
        self.editors['comments'] = ed

    def _handle_comments_done(self, text_changed, text):
        """ Slot to handle changed comments. """

        if text_changed:
            self.api.comments = text
            self.shell.dirty = True

        del self.editors['comments']

    def _handle_add_manual_code(self):
        """ Slot to handle the addition of manual code. """

        manual_code = self.new_manual_code()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code", self.shell)

        if dialog.update():
            CodeView(manual_code, self.shell, self.parent(), after=self)

            parent_content = self.parent().api.content
            parent_content.insert(parent_content.index(self.api) + 1,
                    manual_code)
            self.shell.dirty = True

    def _handle_modify_manual_code(self):
        """ Slot to handle the update of the manual code. """

        dialog = ManualCodeDialog(self.api, "Modify Manual Code", self.shell)

        if dialog.update():
            self.shell.dirty = True

            self.draw_name()

    def _bodyManualCode(self):
        """ Slot to handle the update of the manual code body. """

        ed = ExternalEditor()
        ed.editDone.connect(self._mcBodyDone)
        ed.edit(self.api.body, "Manual Code: " + self.api.precis)
        self.editors['mcb'] = ed

    def _mcBodyDone(self, text_changed, text):
        """ Slot to handle changed manual code body. """

        if text_changed:
            self.api.body = text
            self.shell.dirty = True

        del self.editors['mcb']

    def _deleteCode(self):
        """ Slot to handle the deletion of one or more code items. """

        what = "this part" if len(self._targets) == 1 else "these parts"
        ans = QMessageBox.question(self.treeWidget(), "Delete Code",
                "Are you sure you want to delete {0} of the API?".format(what),
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

        if ans is QMessageBox.StandardButton.Yes:
            # Mark as dirty before removing them.
            self.shell.dirty = True

            parent = self.parent()

            for target in self._targets:
                parent.api.content.remove(target.api)
                parent.removeChild(target)

    def _accessCodeSlot(self):
        """ Slot to handle %AccessCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._accessCodeDone)
        ed.edit(self.api.accesscode, "%AccessCode: " + self.api_as_str())
        self.editors['ac'] = ed

    def _accessCodeDone(self, text_changed, text):
        """ Slot to handle changed %AccessCode. """

        if text_changed:
            self.api.accesscode = text
            self.shell.dirty = True

        del self.editors['ac']

    def _getCodeSlot(self):
        """ Slot to handle %GetCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._getCodeDone)
        ed.edit(self.api.getcode, "%GetCode: " + self.api_as_str())
        self.editors['gc'] = ed

    def _getCodeDone(self, text_changed, text):
        """ Slot to handle changed %GetCode. """

        if text_changed:
            self.api.getcode = text
            self.shell.dirty = True

        del self.editors['gc']

    def _setCodeSlot(self):
        """ Slot to handle %SetCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._setCodeDone)
        ed.edit(self.api.setcode, "%SetCode: " + self.api_as_str())
        self.editors['sc'] = ed

    def _setCodeDone(self, text_changed, text):
        """ Slot to handle changed %SetCode. """

        if text_changed:
            self.api.setcode = text
            self.shell.dirty = True

        del self.editors['sc']

    def _typehintCodeSlot(self):
        """ Slot to handle %TypeHintCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typehintCodeDone)
        ed.edit(self.api.typeheadercode, "%TypeHintCode: " + self.api_as_str())
        self.editors['thic'] = ed

    def _typehintCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeHintCode. """

        if text_changed:
            self.api.typehintcode = text
            self.shell.dirty = True

        del self.editors['thic']

    def _typeheaderCodeSlot(self):
        """ Slot to handle %TypeHeaderCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typeheaderCodeDone)
        ed.edit(self.api.typeheadercode,
                "%TypeHeaderCode: " + self.api_as_str())
        self.editors['thc'] = ed

    def _typeheaderCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeHeaderCode. """

        if text_changed:
            self.api.typeheadercode = text
            self.shell.dirty = True

        del self.editors['thc']

    def _typeCodeSlot(self):
        """ Slot to handle %TypeCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typeCodeDone)
        ed.edit(self.api.typecode, "%TypeCode: " + self.api_as_str())
        self.editors['tc'] = ed

    def _typeCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeCode. """

        if text_changed:
            self.api.typecode = text
            self.shell.dirty = True

        del self.editors['tc']

    def _convToTypeCodeSlot(self):
        """ Slot to handle %ConvertToTypeCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._convToTypeCodeDone)
        ed.edit(self.api.convtotypecode,
                "%ConvertToTypeCode: " + self.api_as_str())
        self.editors['cttc'] = ed

    def _convToTypeCodeDone(self, text_changed, text):
        """ Slot to handle changed %ConvertToTypeCode. """

        if text_changed:
            self.api.convtotypecode = text
            self.shell.dirty = True

        del self.editors['cttc']

    def _convFromTypeCodeSlot(self):
        """ Slot to handle %ConvertFromTypeCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._convFromTypeCodeDone)
        ed.edit(self.api.convfromtypecode,
                "%ConvertFromTypeCode: " + self.api_as_str())
        self.editors['cftc'] = ed

    def _convFromTypeCodeDone(self, text_changed, text):
        """ Slot to handle changed %ConvertFromTypeCode. """

        if text_changed:
            self.api.convfromtypecode = text
            self.shell.dirty = True

        del self.editors['cftc']

    def _gcTraverseCodeSlot(self):
        """ Slot to handle %GCTraverseCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._gcTraverseCodeDone)
        ed.edit(self.api.gctraversecode,
                "%GCTraverseCode: " + self.api_as_str())
        self.editors['gctc'] = ed

    def _gcTraverseCodeDone(self, text_changed, text):
        """ Slot to handle changed %GCTraverseCode. """

        if text_changed:
            self.api.gctraversecode = text
            self.shell.dirty = True

        del self.editors['gctc']

    def _gcClearCodeSlot(self):
        """ Slot to handle %GCClearCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._gcClearCodeDone)
        ed.edit(self.api.gcclearcode, "%GCClearCode: " + self.api_as_str())
        self.editors['gccc'] = ed

    def _gcClearCodeDone(self, text_changed, text):
        """ Slot to handle changed %GCClearCode. """

        if text_changed:
            self.api.gcclearcode = text
            self.shell.dirty = True

        del self.editors['gccc']

    def _biGetBufCodeSlot(self):
        """ Slot to handle %BIGetBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biGetBufCodeDone)
        ed.edit(self.api.bigetbufcode,
                "%BIGetBufferCode: " + self.api_as_str())
        self.editors['bigetb'] = ed

    def _biGetBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetBufferCode. """

        if text_changed:
            self.api.bigetbufcode = text
            self.shell.dirty = True

        del self.editors['bigetb']

    def _biRelBufCodeSlot(self):
        """ Slot to handle %BIReleaseBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biRelBufCodeDone)
        ed.edit(self.api.birelbufcode,
                "%BIReleaseBufferCode: " + self.api_as_str())
        self.editors['birelb'] = ed

    def _biRelBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIReleaseBufferCode. """

        if text_changed:
            self.api.birelbufcode = text
            self.shell.dirty = True

        del self.editors['birelb']

    def _biReadBufCodeSlot(self):
        """ Slot to handle %BIGetReadBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biReadBufCodeDone)
        ed.edit(self.api.bireadbufcode,
                "%BIGetReadBufferCode: " + self.api_as_str())
        self.editors['birb'] = ed

    def _biReadBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetReadBufferCode. """

        if text_changed:
            self.api.bireadbufcode = text
            self.shell.dirty = True

        del self.editors['birb']

    def _biWriteBufCodeSlot(self):
        """ Slot to handle %BIGetWriteBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biWriteBufCodeDone)
        ed.edit(self.api.biwritebufcode,
                "%BIGetWriteBufferCode: " + self.api_as_str())
        self.editors['biwb'] = ed

    def _biWriteBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetWriteBufferCode. """

        if text_changed:
            self.api.biwritebufcode = text
            self.shell.dirty = True

        del self.editors['biwb']

    def _biSegCountCodeSlot(self):
        """ Slot to handle %BIGetSegCountCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biSegCountCodeDone)
        ed.edit(self.api.bisegcountcode,
                "%BIGetSegCountCode: " + self.api_as_str())
        self.editors['bisc'] = ed

    def _biSegCountCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetSegCountCode. """

        if text_changed:
            self.api.bisegcountcode = text
            self.shell.dirty = True

        del self.editors['bisc']

    def _biCharBufCodeSlot(self):
        """ Slot to handle %BIGetCharBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biCharBufCodeDone)
        ed.edit(self.api.bicharbufcode,
                "%BIGetCharBufferCode: " + self.api_as_str())
        self.editors['bicb'] = ed

    def _biCharBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetCharBufferCode. """

        if text_changed:
            self.api.bicharbufcode = text
            self.shell.dirty = True

        del self.editors['bicb']

    def _pickleCodeSlot(self):
        """ Slot to handle %PickleCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._pickleCodeDone)
        ed.edit(self.api.picklecode, "%PickleCode: " + self.api_as_str())
        self.editors['pick'] = ed

    def _pickleCodeDone(self, text_changed, text):
        """ Slot to handle changed %PickleCode. """

        if text_changed:
            self.api.picklecode = text
            self.shell.dirty = True

        del self.editors['pick']

    def _finalCodeSlot(self):
        """ Slot to handle %FinalisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._finalCodeDone)
        ed.edit(self.api.finalisationcode,
                "%FinalisationCode: " + self.api_as_str())
        self.editors['fc'] = ed

    def _finalCodeDone(self, text_changed, text):
        """ Slot to handle changed %FinalisationCode. """

        if text_changed:
            self.api.finalisationcode = text
            self.shell.dirty = True

        del self.editors['fc']

    def _subclassCodeSlot(self):
        """ Slot to handle %ConvertToSubClassCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._subclassCodeDone)
        ed.edit(self.api.subclasscode,
                "%ConvertToSubClassCode: " + self.api_as_str())
        self.editors['scc'] = ed

    def _subclassCodeDone(self, text_changed, text):
        """ Slot to handle changed %ConvertToSubClassCode. """

        if text_changed:
            self.api.subclasscode = text
            self.shell.dirty = True

        del self.editors['scc']

    def _docstringSlot(self):
        """ Slot to handle %Docstring. """

        ed = ExternalEditor()
        ed.editDone.connect(self._docstringDone)
        ed.edit(self.api.docstring, "%Docstring: " + self.api_as_str())
        self.editors['ds'] = ed

    def _docstringDone(self, text_changed, text):
        """ Slot to handle changed %Docstring. """

        if text_changed:
            self.api.docstring = text
            self.shell.dirty = True

        del self.editors['ds']

    def _methodCodeSlot(self):
        """ Slot to handle %MethodCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._methodCodeDone)
        ed.edit(self.api.methcode, "%MethodCode: " + self.api_as_str())
        self.editors['mc'] = ed

    def _methodCodeDone(self, text_changed, text):
        """ Slot to handle changed %MethodCode. """

        if text_changed:
            self.api.methcode = text
            self.draw_name()
            self.shell.dirty = True

        del self.editors['mc']

    def _virtualCatcherCodeSlot(self):
        """ Slot to handle %VirtualCatcherCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._virtualCatcherCodeDone)
        ed.edit(self.api.virtcode, "%VirtualCatcherCode: " + self.api_as_str())
        self.editors['vcc'] = ed

    def _virtualCatcherCodeDone(self, text_changed, text):
        """ Slot to handle changed %VirtualCatcherCode. """

        if text_changed:
            self.api.virtcode = text
            self.shell.dirty = True

        del self.editors['vcc']

    def _handle_versions(self):
        """ Slot to handle the versions. """

        dialog = VersionsDialog(self.api, "Versions", self.shell)

        if dialog.update():
            self.draw_versions()

            # Apply the version range to all targets.
            for view in self._targets:
                if view.api is not self.api:
                    view.api.versions = list(self.api.versions)
                    view.draw_versions()

            self.shell.dirty = True

    def _handle_platforms(self):
        """ Slot to handle the platforms. """

        dialog = PlatformsDialog(self.api, "Platform Tags", self.shell)

        if dialog.update():
            self.shell.dirty = True

    def _handle_features(self):
        """ Slot to handle the features. """

        dialog = FeaturesDialog(self.api, "Feature Tags", self.shell)

        if dialog.update():
            self.shell.dirty = True

    def _handle_namespace_properties(self):
        """ Slot to handle the properties for namespaces. """

        dialog = NamespacePropertiesDialog(self.api, "Namespace Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_opaque_class_properties(self):
        """ Slot to handle the properties for opaque classes. """

        dialog = OpaqueClassPropertiesDialog(self.api,
                "Opaque Class Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_class_properties(self):
        """ Slot to handle the properties for classes. """

        dialog = ClassPropertiesDialog(self.api, "Class Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_callable_properties(self):
        """ Slot to handle the properties for callables. """

        dialog = CallablePropertiesDialog(self.api, 'Placeholder', self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_typedef_properties(self):
        """ Slot to handle the properties for typedefs. """

        dialog = TypedefPropertiesDialog(self.api, "Typedef Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_variable_properties(self):
        """ Slot to handle the properties for variables. """

        dialog = VariablePropertiesDialog(self.api, "Variable Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_enum_properties(self):
        """ Slot to handle the properties for enums. """

        dialog = EnumPropertiesDialog(self.api, "Enum Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _handle_enum_member_properties(self):
        """ Slot to handle the properties for enum members. """

        dialog = EnumMemberPropertiesDialog(self.api,
                "Enum Member Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_as_str())

    def _setStatusChecked(self):
        """ Slot to handle the status being set to checked. """

        self._setStatus('')

    def _setStatusTodo(self):
        """ Slot to handle the status being set to todo. """

        self._setStatus('todo')

    def _setStatusUnchecked(self):
        """ Slot to handle the status being set to unchecked. """

        self._setStatus('unknown')

    def _setStatusIgnored(self):
        """ Slot to handle the status being set to ignored. """

        self._setStatus('ignored')

    def _setStatus(self, new):
        """ Set the status column. """

        for view in self._targets:
            if view.api.status != new:
                view.api.status = new
                self.shell.dirty = True

                # FIXME: Observe the status attribute.
                view.draw_status()

    def _setAccessPublic(self):
        """ Slot to handle the access being set to public. """

        self._setAccess('')

    def _setAccessPublicSlots(self):
        """ Slot to handle the access being set to public slots. """

        self._setAccess("public slots")

    def _setAccessProtected(self):
        """ Slot to handle the access being set to protected. """

        self._setAccess("protected")

    def _setAccessProtectedSlots(self):
        """ Slot to handle the access being set to protected slots. """

        self._setAccess("protected slots")

    def _setAccessPrivate(self):
        """ Slot to handle the access being set to private. """

        self._setAccess("private")

    def _setAccessPrivateSlots(self):
        """ Slot to handle the access being set to private slots. """

        self._setAccess("private slots")

    def _setAccessSignals(self):
        """ Slot to handle the access being set to signals. """

        self._setAccess("signals")

    def _setAccess(self, new):
        """ Set the access column. """

        for view in self._targets:
            if view.api.access != new:
                view.api.access = new
                self.shell.dirty = True

                # FIXME: Observe the access attribute.
                view._draw_access()
