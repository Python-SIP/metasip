# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtCore import QByteArray, QMimeData, Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (QApplication, QMenu, QMessageBox, QProgressDialog,
        QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from ....models import (Class, Constructor, Destructor, Method, Function, Enum,
        EnumValue, OperatorFunction, Access, OperatorMethod, ManualCode,
        Module, OpaqueClass, OperatorCast, Namespace, Tagged, Typedef,
        Variable)
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
            opts = view.get_menu(siblings)

            if opts:
                # Create the menu.
                menu = QMenu()

                for o in opts:
                    if o is None:
                        menu.addSeparator()
                        continue

                    enabled = True
                    checked = None

                    if len(o) == 2:
                        (mtext, mslot) = o
                    elif len(o) == 3:
                        (mtext, mslot, enabled) = o
                    else:
                        (mtext, mslot, enabled, checked) = o

                    action = menu.addAction(mtext, mslot)

                    action.setEnabled(enabled)

                    if checked is not None:
                        action.setCheckable(True)
                        action.setChecked(checked)

                menu.exec(ev.globalPos())

                ev.accept()
                return

        super().contextMenuEvent(ev)

    def startDrag(self, actions):
        """ Reimplemented to start the drag of a view. """

        # Find the selected view.
        dragging = None

        it = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.Selected)
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
        target = self.itemAt(ev.pos())

        # Check that the payload is a view.
        mime = ev.mimeData()
        if not mime.hasFormat(self.MIME_FORMAT):
            return None

        # Get the view from the payload.
        source_id = int(mime.data(self.MIME_FORMAT))
        source = None

        it = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.DragEnabled)
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


class DropSite():
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
        index = self.api.content.find(api)
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

        if len(siblings) != 0:
            return None

        return [("Properties...", self._handle_project_properties)]

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

        # The .sip file is always placed at the top.
        sip_file = view.api
        dst_api = self.api.content
        src_api = view.parent().api.content

        src_api.remove(sip_file)
        dst_api.insert(0, sip_file)

        self.shell.dirty = True

    def get_child_factory(self):
        """ Return the callable that will return a child view. """

        return SipFileView

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        if len(siblings) != 0:
            return None

        return [("Properties...", self._handle_module_properties)]

    def _handle_module_properties(self):
        """ Handle the module's properties. """

        dialog = ModulePropertiesDialog(self.api, "Module Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True


class ContainerView(APIView, DropSite):
    """ This class implements a view of a potential container for code. """

    def __init__(self, container, shell, parent, after):
        """ Initialise the container view. """

        super().__init__(container, shell, parent, after)

        if hasattr(container, 'content'):
            for code in container.content:
                CodeView(code, self.shell, self)

    def droppable(self, view):
        """ Return True if a view can be dropped. """

        # See if we are moving a sibling.
        if view.parent() is self.parent():
            return True

        # See if we are moving a child to the top.
        if view.parent() is self:
            return True

        return False

    def drop(self, view):
        """ Handle the drop of a view. """

        if view.parent() is self.parent():
            # We are moving a sibling after us.
            parent_content = self.parent().api.content
            api = view.api

            parent_content.remove(api)

            new_idx = parent_content.index(self.api) + 1
            if new_idx < len(parent_content):
                parent_content.insert(new_idx, api)
            else:
                parent_content.append(api)

            self.shell.dirty = True

            return

        if view.parent() is self:
            # Dropping a child is interpreted as moving it to the top.
            my_content = self.api.content
            api = view.api

            my_content.remove(api)
            my_content.insert(0, api)

            self.shell.dirty = True

            return

    def get_child_factory(self):
        """ Return the callable that will return a child instance. """

        return CodeView


class SipFileView(ContainerView):
    """ This class implements a view of a .sip file. """

    def __init__(self, sip_file, shell, parent, after=None):
        """ Initialise the .sip file view. """

        super().__init__(sip_file, shell, parent, after)

        self._targets = []
        self._editors = {}

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

        if isinstance(view, SipFileView):
            # We are moving another .sip file after us.  First remove it from
            # its container.
            view.parent().api.content.remove(view.api)

            # Now add it to our container.
            content = self.parent().api.content
            idx = content.index(self.api) + 1
            if idx < len(content):
                content.insert(idx, view.api)
            else:
                content.append(view.api)

            self.shell.dirty = True

            return

        if view.parent() is self:
            # Dropping a child is interpreted as moving it to the top.
            content = self.api.content

            content.remove(view.api)
            content.insert(0, view.api)

            self.shell.dirty = True

            return

    def get_menu(self, siblings):
        """ Return the list of context menu options. """

        if len(siblings) != 0:
            return None

        multiple_modules = (len(self.shell.project.modules) > 0)

        empty_sipfile = True
        for code in self.api.content:
            if code.status != 'ignored':
                empty_sipfile = False
                break

        return [("Hide Ignored", self._hideIgnoredSlot),
                ("Show Ignored", self._showIgnoredSlot),
                None,
                ("Add manual code...", self._handle_add_manual_code),
                None,
                ("%ExportedHeaderCode", self._exportedHeaderCodeSlot, ("ehc" not in self._editors)),
                ("%ModuleHeaderCode", self._moduleHeaderCodeSlot, ("mhc" not in self._editors)),
                ("%ModuleCode", self._moduleCodeSlot, ("moc" not in self._editors)),
                ("%PreInitialisationCode", self._preInitCodeSlot, ("pric" not in self._editors)),
                ("%InitialisationCode", self._initCodeSlot, ("ic" not in self._editors)),
                ("%PostInitialisationCode", self._postInitCodeSlot, ("poic" not in self._editors)),
                None,
                ("%ExportedTypeHintCode", self._exportedTypeHintCodeSlot, ("ethc" not in self._editors)),
                ("%TypeHintCode", self._typeHintCodeSlot, ("thc" not in self._editors)),
                None,
                ("Move to...", self._handle_move, multiple_modules),
                ("Delete", self._deleteFile, empty_sipfile)]

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

            self.parent().api.content.remove(self.api)

    def _handle_add_manual_code(self):
        """ Slot to handle the creation of manual code. """

        manual_code = ManualCode()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code", self.shell)

        if dialog.update():
            self.api.content.insert(0, manual_code)
            self.shell.dirty = True

    def _exportedHeaderCodeSlot(self):
        """ Slot to handle %ExportedHeaderCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._exportedHeaderCodeDone)
        ed.edit(self.api.exportedheadercode, "%ExportedHeaderCode: " + self.api.name)
        self._editors["ehc"] = ed

    def _exportedHeaderCodeDone(self, text_changed, text):
        """ Slot to handle changed %ExportedHeaderCode. """

        if text_changed:
            self.api.exportedheadercode = text
            self.shell.dirty = True

        del self._editors["ehc"]

    def _moduleHeaderCodeSlot(self):
        """ Slot to handle %ModuleHeaderCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._moduleHeaderCodeDone)
        ed.edit(self.api.moduleheadercode, "%ModuleHeaderCode: " + self.api.name)
        self._editors["mhc"] = ed

    def _moduleHeaderCodeDone(self, text_changed, text):
        """ Slot to handle changed %ModuleHeaderCode. """

        if text_changed:
            self.api.moduleheadercode = text
            self.shell.dirty = True

        del self._editors["mhc"]

    def _moduleCodeSlot(self):
        """ Slot to handle %ModuleCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._moduleCodeDone)
        ed.edit(self.api.modulecode, "%ModuleCode: " + self.api.name)
        self._editors["moc"] = ed

    def _moduleCodeDone(self, text_changed, text):
        """ Slot to handle changed %ModuleCode. """

        if text_changed:
            self.api.modulecode = text
            self.shell.dirty = True

        del self._editors["moc"]

    def _preInitCodeSlot(self):
        """ Slot to handle %PreInitialisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._preInitCodeDone)
        ed.edit(self.api.preinitcode, "%PreInitialisationCode: " + self.api.name)
        self._editors["pric"] = ed

    def _preInitCodeDone(self, text_changed, text):
        """ Slot to handle changed %PreInitialisationCode. """

        if text_changed:
            self.api.preinitcode = text
            self.shell.dirty = True

        del self._editors["pric"]

    def _initCodeSlot(self):
        """ Slot to handle %InitialisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._initCodeDone)
        ed.edit(self.api.initcode, "%InitialisationCode: " + self.api.name)
        self._editors["ic"] = ed

    def _initCodeDone(self, text_changed, text):
        """ Slot to handle changed %InitialisationCode. """

        if text_changed:
            self.api.initcode = text
            self.shell.dirty = True

        del self._editors["ic"]

    def _postInitCodeSlot(self):
        """ Slot to handle %PostInitialisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._postInitCodeDone)
        ed.edit(self.api.postinitcode, "%PostInitialisationCode: " + self.api.name)
        self._editors["poic"] = ed

    def _postInitCodeDone(self, text_changed, text):
        """ Slot to handle changed %PostInitialisationCode. """

        if text_changed:
            self.api.postinitcode = text
            self.shell.dirty = True

        del self._editors["poic"]

    def _exportedTypeHintCodeSlot(self):
        """ Slot to handle %ExportedTypeHintCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._exportedTypeHintCodeDone)
        ed.edit(self.api.exportedtypehintcode, "%ExportedTypeHintCode: " + self.api.name)
        self._editors["ethc"] = ed

    def _exportedTypeHintCodeDone(self, text_changed, text):
        """ Slot to handle changed %ExportedTypeHintCode. """

        if text_changed:
            self.api.exportedtypehintcode = text
            self.shell.dirty = True

        del self._editors["ethc"]

    def _typeHintCodeSlot(self):
        """ Slot to handle %TypeHintCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typeHintCodeDone)
        ed.edit(self.api.typehintcode, "%TypeHintCode: " + self.api.name)
        self._editors["thc"] = ed

    def _typeHintCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeHintCode. """

        if text_changed:
            self.api.typehintcode = text
            self.shell.dirty = True

        del self._editors["thc"]

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
            if isinstance(itm, CodeView) and itm.code.status == "ignored":
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

        if len(siblings) != 0:
            return None

        return [("Properties...", self._handle_argument_properties)]

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
        self._editors = {}

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

        menu = [("Checked", self._setStatusChecked, True, (self.api.status == "")),
                ("Todo", self._setStatusTodo, True, (self.api.status == "todo")),
                ("Unchecked", self._setStatusUnchecked, True, (self.api.status == "unknown")),
                ("Ignored", self._setStatusIgnored, True, (self.api.status == "ignored"))]

        # Handle the access specifiers.
        if isinstance(self.api, Access):
                menu.append(None)
                menu.append(("public", self._setAccessPublic, True, (self.api.access == "")))
                menu.append(("public slots", self._setAccessPublicSlots, True, (self.api.access == "public slots")))
                menu.append(("protected", self._setAccessProtected, True, (self.api.access == "protected")))
                menu.append(("protected slots", self._setAccessProtectedSlots, True, (self.api.access == "protected slots")))
                menu.append(("private", self._setAccessPrivate, True, (self.api.access == "private")))
                menu.append(("private slots", self._setAccessPrivateSlots, True, (self.api.access == "private slots")))
                menu.append(("signals", self._setAccessSignals, True, (self.api.access == "signals")))

        if len(siblings) != 0:
            menu.append(None)
            menu.append(("Versions...", self._handle_versions,
                    (len(project.versions) != 0)))

            menu.append(None)
            menu.append(("Delete", self._deleteCode, (not self._editors)))

            return menu

        # Handle the manual code part of the menu.
        menu.append(None)
        menu.append(("Add manual code...", self._handle_add_manual_code))

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
        pslot = None
        dsslot = None

        if isinstance(self.api, ManualCode):
            menu.append(("Modify manual code...", self._handle_modify_manual_code))
            menu.append(("Modify manual code body...", self._bodyManualCode, ("mcb" not in self._editors)))

            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, Namespace):
            pslot = self._handle_namespace_properties
        elif isinstance(self.api, OpaqueClass):
            pslot = self._handle_opaque_class_properties
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
            pslot = self._handle_class_properties
            dsslot = True
        elif isinstance(self.api, Constructor):
            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, Destructor):
            mcslot = True
            vccslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.api, OperatorCast):
            mcslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.api, Method):
            mcslot = True

            if self.api.virtual:
                vccslot = True

            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, OperatorMethod):
            mcslot = True

            if self.api.virtual:
                vccslot = True

            pslot = self._handle_callable_properties
        elif isinstance(self.api, Function):
            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api, OperatorFunction):
            mcslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.api, Typedef):
            pslot = self._handle_typedef_properties
            dsslot = True
        elif isinstance(self.api, Variable):
            acslot = True
            gcslot = True
            scslot = True
            pslot = self._handle_variable_properties
        elif isinstance(self.api, Enum):
            pslot = self._handle_enum_properties
        elif isinstance(self.api, EnumValue):
            pslot = self._handle_enum_member_properties

        if thcslot or thicslot or tcslot or cttcslot or cftcslot or fcslot or sccslot or mcslot or vccslot or acslot or gcslot or scslot or gctcslot or gcccslot or bigetbslot or birelbslot or birbslot or biwbslot or biscslot or bicbslot or pickslot or xaslot or dsslot:
            menu.append(None)

            if thcslot:
                self._add_directive(menu, '%TypeHeaderCode',
                        self.api.typeheadercode, self._typeheaderCodeSlot,
                        'thc')

            if tcslot:
                self._add_directive(menu, '%TypeCode', self.api.typecode,
                        self._typeCodeSlot, 'tc')

            if thicslot:
                self._add_directive(menu, '%TypeHintCode',
                        self.api.typehintcode, self._typehintCodeSlot, 'thic')

            if fcslot:
                self._add_directive(menu, '%FinalisationCode',
                        self.api.finalisationcode, self._finalCodeSlot, 'fc')

            if sccslot:
                self._add_directive(menu, '%ConvertToSubClassCode',
                        self.api.subclasscode, self._subclassCodeSlot, 'scc')

            if cttcslot:
                self._add_directive(menu, '%ConvertToTypeCode',
                        self.api.convtotypecode, self._convToTypeCodeSlot,
                        'cttc')

            if cftcslot:
                self._add_directive(menu, '%ConvertFromTypeCode',
                        self.api.convfromtypecode, self._convFromTypeCodeSlot,
                        'cftc')

            if mcslot:
                self._add_directive(menu, '%MethodCode', self.api.methcode,
                        self._methodCodeSlot, 'mc')

            if vccslot:
                self._add_directive(menu, '%VirtualCatcherCode',
                        self.api.virtcode, self._virtualCatcherCodeSlot,
                        'vcc')

            if acslot:
                self._add_directive(menu, '%AccessCode', self.api.accesscode,
                        self._accessCodeSlot, 'ac')

            if gcslot:
                self._add_directive(menu, '%GetCode', self.api.getcode,
                        self._getCodeSlot, 'gc')

            if scslot:
                self._add_directive(menu, '%SetCode', self.api.setcode,
                        self._setCodeSlot, 'sc')

            if gctcslot:
                self._add_directive(menu, '%GCTraverseCode',
                        self.api.gctraversecode, self._gcTraverseCodeSlot,
                        'gctc')

            if gcccslot:
                self._add_directive(menu, '%GCClearCode',
                        self.api.gcclearcode, self._gcClearCodeSlot, 'gccc')

            if bigetbslot:
                self._add_directive(menu, '%BIGetBufferCode',
                        self.api.bigetbufcode, self._biGetBufCodeSlot,
                        'bigetb')

            if birelbslot:
                self._add_directive(menu, '%BIReleaseBufferCode',
                        self.api.birelbufcode, self._biRelBufCodeSlot,
                        'birelb')

            if birbslot:
                self._add_directive(menu, '%BIGetReadBufferCode',
                        self.api.bireadbufcode, self._biReadBufCodeSlot,
                        'birb')

            if biwbslot:
                self._add_directive(menu, '%BIGetWriteBufferCode',
                        self.api.biwritebufcode, self._biWriteBufCodeSlot,
                        'biwb')

            if biscslot:
                self._add_directive(menu, '%BIGetSegCountCode',
                        self.api.bisegcountcode, self._biSegCountCodeSlot,
                        'bisc')

            if bicbslot:
                self._add_directive(menu, '%BIGetCharBufferCode',
                        self.api.bicharbufcode, self._biCharBufCodeSlot,
                        'bicb')

            if pickslot:
                self._add_directive(menu, '%PickleCode', self.api.picklecode,
                        self._pickleCodeSlot, 'pick')

            if dsslot:
                self._add_directive(menu, '%Docstring', self.api.docstring,
                        self._docstringSlot, 'ds')

        if isinstance(self.api, (Constructor, Function, Method)):
            menu.append(None)
            menu.append(("Accept all argument names", self._acceptNames))

        # Add the extra menu items.
        menu.append(None)
        menu.append(("Versions...", self._handle_versions,
                len(project.versions) != 0))
        menu.append(
                (self._flagged_text("Platform Tags...", self.api.platforms),
                        self._handle_platforms, len(project.platforms) != 0))
        menu.append(
                (self._flagged_text("Feature Tags...", self.api.features),
                        self._handle_features,
                        (len(project.features) != 0 or len(project.externalfeatures) != 0)))

        if pslot:
            menu.append(("Properties...", pslot))

        menu.append(None)
        menu.append(("Delete", self._deleteCode, (not self._editors)))

        return menu

    def _add_directive(self, menu, name, flag, slot, editor):
        """ Add the entry for a directive to a menu. """

        menu.append(
                (self._flagged_text(name + '...', flag), slot,
                        (editor not in self._editors)))

    @staticmethod
    def _flagged_text(text, flag):
        """ Return a (possibly) flagged version of a piece of text. """

        if flag:
            text += ' \N{small orange diamond}'

        return text

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

    def _handle_add_manual_code(self):
        """ Slot to handle the addition of manual code. """

        manual_code = ManualCode()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code", self.shell)

        if dialog.update():
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
        self._editors["mcb"] = ed

    def _mcBodyDone(self, text_changed, text):
        """ Slot to handle changed manual code body. """

        if text_changed:
            self.api.body = text
            self.shell.dirty = True

        del self._editors["mcb"]

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

            for target in self._targets:
                self.parent().api.content.remove(target.api)

    def _accessCodeSlot(self):
        """ Slot to handle %AccessCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._accessCodeDone)
        ed.edit(self.api.accesscode, "%AccessCode: " + self.api_as_str())
        self._editors["ac"] = ed

    def _accessCodeDone(self, text_changed, text):
        """ Slot to handle changed %AccessCode. """

        if text_changed:
            self.api.accesscode = text
            self.shell.dirty = True

        del self._editors["ac"]

    def _getCodeSlot(self):
        """ Slot to handle %GetCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._getCodeDone)
        ed.edit(self.api.getcode, "%GetCode: " + self.api_as_str())
        self._editors["gc"] = ed

    def _getCodeDone(self, text_changed, text):
        """ Slot to handle changed %GetCode. """

        if text_changed:
            self.api.getcode = text
            self.shell.dirty = True

        del self._editors["gc"]

    def _setCodeSlot(self):
        """ Slot to handle %SetCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._setCodeDone)
        ed.edit(self.api.setcode, "%SetCode: " + self.api_as_str())
        self._editors["sc"] = ed

    def _setCodeDone(self, text_changed, text):
        """ Slot to handle changed %SetCode. """

        if text_changed:
            self.api.setcode = text
            self.shell.dirty = True

        del self._editors["sc"]

    def _typehintCodeSlot(self):
        """ Slot to handle %TypeHintCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typehintCodeDone)
        ed.edit(self.api.typeheadercode, "%TypeHintCode: " + self.api_as_str())
        self._editors["thic"] = ed

    def _typehintCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeHintCode. """

        if text_changed:
            self.api.typehintcode = text
            self.shell.dirty = True

        del self._editors["thic"]

    def _typeheaderCodeSlot(self):
        """ Slot to handle %TypeHeaderCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typeheaderCodeDone)
        ed.edit(self.api.typeheadercode,
                "%TypeHeaderCode: " + self.api_as_str())
        self._editors["thc"] = ed

    def _typeheaderCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeHeaderCode. """

        if text_changed:
            self.api.typeheadercode = text
            self.shell.dirty = True

        del self._editors["thc"]

    def _typeCodeSlot(self):
        """ Slot to handle %TypeCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._typeCodeDone)
        ed.edit(self.api.typecode, "%TypeCode: " + self.api_as_str())
        self._editors["tc"] = ed

    def _typeCodeDone(self, text_changed, text):
        """ Slot to handle changed %TypeCode. """

        if text_changed:
            self.api.typecode = text
            self.shell.dirty = True

        del self._editors["tc"]

    def _convToTypeCodeSlot(self):
        """ Slot to handle %ConvertToTypeCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._convToTypeCodeDone)
        ed.edit(self.api.convtotypecode,
                "%ConvertToTypeCode: " + self.api_as_str())
        self._editors["cttc"] = ed

    def _convToTypeCodeDone(self, text_changed, text):
        """ Slot to handle changed %ConvertToTypeCode. """

        if text_changed:
            self.api.convtotypecode = text
            self.shell.dirty = True

        del self._editors["cttc"]

    def _convFromTypeCodeSlot(self):
        """ Slot to handle %ConvertFromTypeCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._convFromTypeCodeDone)
        ed.edit(self.api.convfromtypecode,
                "%ConvertFromTypeCode: " + self.api_as_str())
        self._editors["cftc"] = ed

    def _convFromTypeCodeDone(self, text_changed, text):
        """ Slot to handle changed %ConvertFromTypeCode. """

        if text_changed:
            self.api.convfromtypecode = text
            self.shell.dirty = True

        del self._editors["cftc"]

    def _gcTraverseCodeSlot(self):
        """ Slot to handle %GCTraverseCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._gcTraverseCodeDone)
        ed.edit(self.api.gctraversecode,
                "%GCTraverseCode: " + self.api_as_str())
        self._editors["gctc"] = ed

    def _gcTraverseCodeDone(self, text_changed, text):
        """ Slot to handle changed %GCTraverseCode. """

        if text_changed:
            self.api.gctraversecode = text
            self.shell.dirty = True

        del self._editors["gctc"]

    def _gcClearCodeSlot(self):
        """ Slot to handle %GCClearCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._gcClearCodeDone)
        ed.edit(self.api.gcclearcode, "%GCClearCode: " + self.api_as_str())
        self._editors["gccc"] = ed

    def _gcClearCodeDone(self, text_changed, text):
        """ Slot to handle changed %GCClearCode. """

        if text_changed:
            self.api.gcclearcode = text
            self.shell.dirty = True

        del self._editors["gccc"]

    def _biGetBufCodeSlot(self):
        """ Slot to handle %BIGetBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biGetBufCodeDone)
        ed.edit(self.api.bigetbufcode,
                "%BIGetBufferCode: " + self.api_as_str())
        self._editors["bigetb"] = ed

    def _biGetBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetBufferCode. """

        if text_changed:
            self.api.bigetbufcode = text
            self.shell.dirty = True

        del self._editors["bigetb"]

    def _biRelBufCodeSlot(self):
        """ Slot to handle %BIReleaseBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biRelBufCodeDone)
        ed.edit(self.api.birelbufcode,
                "%BIReleaseBufferCode: " + self.api_as_str())
        self._editors["birelb"] = ed

    def _biRelBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIReleaseBufferCode. """

        if text_changed:
            self.api.birelbufcode = text
            self.shell.dirty = True

        del self._editors["birelb"]

    def _biReadBufCodeSlot(self):
        """ Slot to handle %BIGetReadBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biReadBufCodeDone)
        ed.edit(self.api.bireadbufcode,
                "%BIGetReadBufferCode: " + self.api_as_str())
        self._editors["birb"] = ed

    def _biReadBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetReadBufferCode. """

        if text_changed:
            self.api.bireadbufcode = text
            self.shell.dirty = True

        del self._editors["birb"]

    def _biWriteBufCodeSlot(self):
        """ Slot to handle %BIGetWriteBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biWriteBufCodeDone)
        ed.edit(self.api.biwritebufcode,
                "%BIGetWriteBufferCode: " + self.api_as_str())
        self._editors["biwb"] = ed

    def _biWriteBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetWriteBufferCode. """

        if text_changed:
            self.api.biwritebufcode = text
            self.shell.dirty = True

        del self._editors["biwb"]

    def _biSegCountCodeSlot(self):
        """ Slot to handle %BIGetSegCountCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biSegCountCodeDone)
        ed.edit(self.api.bisegcountcode,
                "%BIGetSegCountCode: " + self.api_as_str())
        self._editors["bisc"] = ed

    def _biSegCountCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetSegCountCode. """

        if text_changed:
            self.api.bisegcountcode = text
            self.shell.dirty = True

        del self._editors["bisc"]

    def _biCharBufCodeSlot(self):
        """ Slot to handle %BIGetCharBufferCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._biCharBufCodeDone)
        ed.edit(self.api.bicharbufcode,
                "%BIGetCharBufferCode: " + self.api_as_str())
        self._editors["bicb"] = ed

    def _biCharBufCodeDone(self, text_changed, text):
        """ Slot to handle changed %BIGetCharBufferCode. """

        if text_changed:
            self.api.bicharbufcode = text
            self.shell.dirty = True

        del self._editors["bicb"]

    def _pickleCodeSlot(self):
        """ Slot to handle %PickleCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._pickleCodeDone)
        ed.edit(self.api.picklecode, "%PickleCode: " + self.api_as_str())
        self._editors["pick"] = ed

    def _pickleCodeDone(self, text_changed, text):
        """ Slot to handle changed %PickleCode. """

        if text_changed:
            self.api.picklecode = text
            self.shell.dirty = True

        del self._editors["pick"]

    def _finalCodeSlot(self):
        """ Slot to handle %FinalisationCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._finalCodeDone)
        ed.edit(self.api.finalisationcode,
                "%FinalisationCode: " + self.api_as_str())
        self._editors["fc"] = ed

    def _finalCodeDone(self, text_changed, text):
        """ Slot to handle changed %FinalisationCode. """

        if text_changed:
            self.api.finalisationcode = text
            self.shell.dirty = True

        del self._editors["fc"]

    def _subclassCodeSlot(self):
        """ Slot to handle %ConvertToSubClassCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._subclassCodeDone)
        ed.edit(self.api.subclasscode,
                "%ConvertToSubClassCode: " + self.api_as_str())
        self._editors["scc"] = ed

    def _subclassCodeDone(self, text_changed, text):
        """ Slot to handle changed %ConvertToSubClassCode. """

        if text_changed:
            self.api.subclasscode = text
            self.shell.dirty = True

        del self._editors["scc"]

    def _docstringSlot(self):
        """ Slot to handle %Docstring. """

        ed = ExternalEditor()
        ed.editDone.connect(self._docstringDone)
        ed.edit(self.api.docstring, "%Docstring: " + self.api_as_str())
        self._editors["ds"] = ed

    def _docstringDone(self, text_changed, text):
        """ Slot to handle changed %Docstring. """

        if text_changed:
            self.api.docstring = text
            self.shell.dirty = True

        del self._editors["ds"]

    def _methodCodeSlot(self):
        """ Slot to handle %MethodCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._methodCodeDone)
        ed.edit(self.api.methcode, "%MethodCode: " + self.api_as_str())
        self._editors["mc"] = ed

    def _methodCodeDone(self, text_changed, text):
        """ Slot to handle changed %MethodCode. """

        if text_changed:
            self.api.methcode = text
            self.shell.dirty = True

        del self._editors["mc"]

    def _virtualCatcherCodeSlot(self):
        """ Slot to handle %VirtualCatcherCode. """

        ed = ExternalEditor()
        ed.editDone.connect(self._virtualCatcherCodeDone)
        ed.edit(self.api.virtcode, "%VirtualCatcherCode: " + self.api_as_str())
        self._editors["vcc"] = ed

    def _virtualCatcherCodeDone(self, text_changed, text):
        """ Slot to handle changed %VirtualCatcherCode. """

        if text_changed:
            self.api.virtcode = text
            self.shell.dirty = True

        del self._editors["vcc"]

    def _handle_versions(self):
        """ Slot to handle the versions. """

        dialog = VersionsDialog(self.api, "Versions", self.shell)

        if dialog.update():
            # Apply the version range to all targets.
            for view in self._targets:
                if view.api is not self.api:
                    view.api.versions = list(self.api.versions)

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
