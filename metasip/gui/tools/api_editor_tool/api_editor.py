# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt6.QtCore import QByteArray, QMimeData, Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (QApplication, QInputDialog, QMenu, QMessageBox,
        QProgressDialog, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from ....project import (Class, Constructor, Destructor, Method, Function,
        Variable, Enum, EnumValue, OperatorFunction, Access, OperatorMethod,
        ManualCode, Module, OpaqueClass, OperatorCast, Namespace, VersionRange,
        version_range)

from ...helpers import warning

from .dialogs import (ArgumentPropertiesDialog, CallablePropertiesDialog,
        ClassPropertiesDialog, EnumPropertiesDialog,
        EnumMemberPropertiesDialog, FeaturesDialog, ManualCodeDialog,
        ModulePropertiesDialog, MoveHeaderDialog, NamespacePropertiesDialog,
        OpaqueClassPropertiesDialog, PlatformsDialog, ProjectPropertiesDialog,
        VariablePropertiesDialog, VersionsDialog)

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
        self._project_item = None

        # Tweak the tree widget.
        self.setHeaderLabels(("Name", "Access", "Status", "Versions"))
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)

        self.dragged = None

    def api_item_status(self, api_item):
        """ Handle the change of status of an API item. """

        for item in self._all_items():
            if item.api_item is api_item:
                item.draw_status()
                break

    def api_item_versions(self, api_item):
        """ Handle the change of versions of an API item. """

        for item in self._all_items():
            if item.api_item is api_item:
                item.draw_versions()
                break

    def container_api_item_add(self, container, api_item):
        """ Handle the addition of an API item to a container. """

        for item in self._all_items():
            if item.api_item is container:
                item.api_item_add(api_item)
                break

    def container_api_item_delete(self, container, api_item):
        """ Handle the deletion of an API item from a container. """

        for item in self._all_items():
            if item.api_item is container:
                item.api_item_delete(api_item)
                break

    def module_add(self, module):
        """ Handle the addition of a module. """

        self._project_item.module_add(module)

    def module_delete(self, module):
        """ Handle the deletion of a module. """

        self._project_item.module_delete(module)

    def module_rename(self, module):
        """ A module has been renamed. """

        self._project_item.module_rename(module)

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('header')
        if state is not None:
            self.header().restoreState(state)

    def set_project(self):
        """ Set the current project. """

        self.clear()

        self._project_item = ProjectItem(self._shell, self)

    def root_module_updated(self):
        """ The name of the root module has been updated. """

        self._project_item.root_module_updated()

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('header', self.header().saveState())

    def contextMenuEvent(self, ev):
        """ Reimplemented to handle a context menu event. """

        # Find the item.
        itm = self.itemAt(ev.pos())

        if itm:
            # Get the list of siblings that are also selected.
            siblings = []

            parent = itm.parent()
            if parent is not None:
                for sib_idx in range(parent.childCount()):
                    sib = parent.child(sib_idx)

                    if sib is not itm and sib.isSelected() and not sib.isHidden():
                        siblings.append(sib)

            # Check it has a menu.
            opts = itm.get_menu(siblings)

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
        """ Reimplemented to start the drag of an item. """

        # Find the selected item.
        dragging = None

        it = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.Selected)
        itm = it.value()

        while itm is not None:
            # We can only drag one item.
            if dragging is not None:
                return

            dragging = itm

            it += 1
            itm = it.value()

        # Make sure there was something to drag.
        if dragging is None:
            return

        # Serialize the id() of the item being dragged.
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
        """ Return a 2-tuple of source and target items or None if the drop
        wasn't appropriate.
        """

        # Get the target.
        target = self.itemAt(ev.pos())

        # Check that the payload is an item.
        mime = ev.mimeData()
        if not mime.hasFormat(self.MIME_FORMAT):
            return None

        # Get the item from the payload.
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

    def acceptArgumentNames(self, api_item):
        """ Mark the arguments of all callables contained in a part of a
        project as being named.
        """

        updated_args = self._shell.project.acceptArgumentNames(api_item)

        callables = []
        for arg in updated_args:
            arg._gui.draw_name()

            callable = arg._gui.parent()
            if callable not in callables:
                callables.append(callable)

        for callable in callables:
            callable.draw_name()
            callable.draw_status()

    def _all_items(self, container=None):
        """ A generator for all API items. """

        if container is None:
            container = self._project_item

        for api_item in container.all_children():
            yield api_item

            for sub_api_item in self._all_items(api_item):
                yield sub_api_item


class DropSite():
    """ This mixin class implements a drop site.  Any derived class must also
    derive QTreeWidgetItem.
    """

    def __init__(self):
        """ Initialise the instance. """

        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsDropEnabled)

    def droppable(self, item):
        """ Return True if an item can be dropped. """

        raise NotImplementedError

    def drop(self, item):
        """ Handle the drop of an item. """

        raise NotImplementedError


# Each QTreeWidgetItem has a unique key used in the DND support.
_item_id = QTreeWidgetItem.ItemType.UserType


class EditorItem(QTreeWidgetItem):
    """ This class represents an item in the API editor. """

    def __init__(self, api_item, shell, parent, after=None):
        """ Initialise the item instance. """

        global _item_id
        item_id = _item_id
        _item_id += 1

        if after is parent:
            super().__init__(parent, None, item_id)
        elif after is None:
            super().__init__(parent, item_id)
        else:
            super().__init__(parent, after, item_id)

        self.api_item = api_item
        self.shell = shell

    def all_children(self):
        """ A generator for all the item's children. """

        for index in range(self.count()):
            yield self.child(index)

    def api_item_add(self, api_item):
        """ An API item has been added. """

        # The order of view items must match the order of API items.
        index = self.api_item.content.find(api_item)
        after = self if index == 0 else self.child(index - 1)
        self.get_child_factory()(api_item, self.shell, self, after)

    def api_item_delete(self, api_item):
        """ An API item has been deleted. """

        for sip_file_item in self.all_children:
            if sip_file_item.api_item is api_item:
                self.removeChild(sip_file_item)
                break

    def get_child_factory(self):
        """ Return the callable that will return a child instance. """

        raise NotImplementedError

    def get_menu(self, siblings):
        """ Return the list of context menu options or None if the item doesn't
        have a context menu.  Each element is a 3-tuple of the text of the
        option, the bound method that handles the option, and a flag that is
        True if the option should be enabled.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            this implementation always returns ``None``.
        """

        return None


class ProjectItem(EditorItem):
    """ This class implements a navigation item that represents a project. """

    def __init__(self, shell, parent):
        """ Initialise the project item. """

        super().__init__(shell.project, shell, parent)

        self.root_module_updated()
        self.setExpanded(True)

        project = self.api_item

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
            ModuleItem(module, self.shell, self)

            so_far += len(module.content)
            progress.setValue(so_far)
            QApplication.processEvents()

        self._sort()

    def get_menu(self, siblings):
        """ Return the list of context menu options.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            the menu options.
        """

        if len(siblings) != 0:
            return None

        return [("Add Ignored Namespace...", self._ignorednamespaceSlot),
                ("Properties...", self._handle_project_properties)]

    def module_add(self, module):
        """ Handle the addition of a module. """

        ModuleItem(module, self.shell, self)
        self._sort()

    def module_delete(self, module):
        """ Handle the deletion of a module. """

        for module_item_index in range(self.childCount()):
            module_item = self.child(module_item_index)
            if module_item.module is module:
                self.removeChild(module_item)
                break

    def module_rename(self, module):
        """ A module has been renamed. """

        for module_item_index in range(self.childCount()):
            module_item = self.child(module_item_index)
            if module_item.module is module:
                module_item.setText(ApiEditor.NAME, module.name)
                break

        self._sort()

    def root_module_updated(self):
        """ The name of the root module has been updated. """

        name = self.shell.project.rootmodule
        if name == '':
            name = "Modules"

        self.setText(ApiEditor.NAME, name)

    def _ignorednamespaceSlot(self):
        """ Handle adding a new ignored namespace. """

        project = self.shell.project
        title = "Add Ignored Namespace"

        # Get the name of the new ignored namespace.
        (ns, ok) = QInputDialog.getText(self.treeWidget(), title,
                "Ignored Namespace")

        if ok:
            ns = ns.strip()

            if ns == '':
                warning(title,
                        "The name of the ignored namespace must not be blank.",
                        parent=self.treeWidget())
            elif ns in project.ignorednamespaces:
                warning(title,
                        f"'{ns}' is already used as the name of an ignored namespace.",
                        parent=self.treeWidget())
            else:
                # Add the ignored namespace to the project.
                project.ignorednamespaces.append(ns)
                self.shell.dirty = True

    def _handle_project_properties(self):
        """ Handle the project's properties. """

        dialog = ProjectPropertiesDialog(self.shell.project,
                "Project Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True

    def _sort(self):
        """ Sort the modules. """

        self.sortChildren(ApiEditor.NAME, Qt.SortOrder.AscendingOrder)


class ModuleItem(EditorItem, DropSite):
    """ This class implements an editor item that represents a module. """

    def __init__(self, module, shell, parent):
        """ Initialise the module item. """

        super().__init__(module, shell, parent)

        self.setText(ApiEditor.NAME, module.name)

        for sip_file in module.content:
            SipFileItem(sip_file, self.shell, self)

    def droppable(self, item):
        """ Return True if an item can be dropped. """

        # We allow .sip files to be moved around anywhere.
        return isinstance(item, SipFileItem)

    def drop(self, item):
        """ Handle the drop of an item. """

        # The .sip file is always placed at the top.
        sf = item.api_item
        dst_api_item = self.api_item.content
        src_api_item = item.parent().api_item.content

        src_api_item.remove(sf)
        dst_api_item.insert(0, sf)

        self.shell.dirty = True

    def get_child_factory(self):
        """ Return the callable that will return a child instance. """

        return SipFileItem

    def get_menu(self, siblings):
        """ Return the list of context menu options.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            the menu options.
        """

        if len(siblings) != 0:
            return None

        return [("Properties...", self._handle_module_properties)]

    def _handle_module_properties(self):
        """ Handle the module's properties. """

        dialog = ModulePropertiesDialog(self.api_item, "Module Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True


class ContainerItem(EditorItem, DropSite):
    """ This class implements an editor item that represents a potential
    container for code items.
    """

    def __init__(self, container, shell, parent, after):
        """ Initialise the container item. """

        super().__init__(container, shell, parent, after)

        if hasattr(container, 'content'):
            for code in container.content:
                CodeItem(code, self.shell, self)

    def droppable(self, item):
        """ Return True if an item can be dropped. """

        # See if we are moving a sibling.
        if item.parent() is self.parent():
            return True

        # See if we are moving a child to the top.
        if item.parent() is self:
            return True

        return False

    def drop(self, item):
        """ Handle the drop of an item. """

        if item.parent() is self.parent():
            # We are moving a sibling after us.
            parent_content = self.parent().api_item.content
            api_item = item.api_item()

            parent_content.remove(api_item)

            new_idx = parent_content.index(self.api_item) + 1
            if new_idx < len(parent_content):
                parent_content.insert(new_idx, api_item)
            else:
                parent_content.append(api_item)

            self.shell.dirty = True

            return

        if item.parent() is self:
            # Dropping a child is interpreted as moving it to the top.
            my_content = self.api_item.content
            api_item = item.api_item

            my_content.remove(api_item)
            my_content.insert(0, api_item)

            self.shell.dirty = True

            return

    def get_child_factory(self):
        """ Return the callable that will return a child instance. """

        return CodeItem


class SipFileItem(ContainerItem):
    """ This class implements an editor item that represents a .sip file. """

    def __init__(self, sip_file, shell, parent, after=None):
        """ Initialise the .sip file item. """

        super().__init__(sip_file, shell, parent, after)

        self._targets = []
        self._editors = {}

        self.setText(ApiEditor.NAME, sip_file.name)

    def droppable(self, item):
        """ Return True if an item can be dropped. """

        # See if we are moving another .sip file.
        if isinstance(item, SipFileItem):
            return True

        # See if we are moving a child to the top.
        if item.parent() is self:
            return True

        return False

    def drop(self, item):
        """ Handle the drop of an item. """

        if isinstance(item, SipFileItem):
            # We are moving another .sip file after us.  First remove the item
            # from its container.
            item.parent().module.content.remove(item.api_item)

            # Now add it to our container.
            content = self.parent().api_item.content
            idx = content.index(self.api_item) + 1
            if idx < len(content):
                content.insert(idx, item.api_item)
            else:
                content.append(item.api_item)

            self.shell.dirty = True

            return

        if item.parent() is self:
            # Dropping a child is interpreted as moving it to the top.
            content = self.api_item.content

            content.remove(item.api_item)
            content.insert(0, item.api_item)

            self.shell.dirty = True

            return

    def get_menu(self, siblings):
        """ Return the list of context menu options.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            the menu options.
        """

        if len(siblings) != 0:
            return None

        multiple_modules = (len(self.treeWidget().project.modules) > 0)

        empty_sipfile = True
        for code in self.api_item.content:
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
                ("Accept argument names", self._acceptNames),
                None,
                ("Move to...", self._handle_move, multiple_modules),
                ("Delete", self._deleteFile, empty_sipfile)]

    def _handle_move(self):
        """ Move a .sip file to a different module. """

        src_module = self.parent().api_item

        dialog = MoveHeaderDialog(src_module, "Move Header File", self.shell)

        dst_module = dialog.get_destination_module()
        if dst_module is not None:
            # Mark as dirty before moving it.
            self.shell.dirty = True

            src_module.content.remove(self.api_item)
            dst_module.content.append(self.api_item)

    def _deleteFile(self):
        """ Delete an empty .sip file. """

        ans = QMessageBox.question(self.treeWidget(), "Delete header file",
                "Are you sure you want to delete this header file?",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

        if ans is QMessageBox.StandardButton.Yes:
            # Mark as dirty before removing it.
            self.shell.dirty = True

            self.parent().api_item.content.remove(self.api_item)

    def _acceptNames(self):
        """ Accept all argument names. """

        self.treeWidget().acceptArgumentNames(self.api_item)

    def _handle_add_manual_code(self):
        """ Slot to handle the creation of manual code. """

        manual_code = ManualCode()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code", self.shell)

        if dialog.update():
            self.api_item.content.insert(0, manual_code)
            self.shell.dirty = True

    def _exportedHeaderCodeSlot(self):
        """
        Slot to handle %ExportedHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._exportedHeaderCodeDone)
        ed.edit(self.api_item.exportedheadercode, "%ExportedHeaderCode: " + self.api_item.name)
        self._editors["ehc"] = ed

    def _exportedHeaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ExportedHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.exportedheadercode = text
            self.shell.dirty = True

        del self._editors["ehc"]

    def _moduleHeaderCodeSlot(self):
        """
        Slot to handle %ModuleHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._moduleHeaderCodeDone)
        ed.edit(self.api_item.moduleheadercode, "%ModuleHeaderCode: " + self.api_item.name)
        self._editors["mhc"] = ed

    def _moduleHeaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ModuleHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.moduleheadercode = text
            self.shell.dirty = True

        del self._editors["mhc"]

    def _moduleCodeSlot(self):
        """
        Slot to handle %ModuleCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._moduleCodeDone)
        ed.edit(self.api_item.modulecode, "%ModuleCode: " + self.api_item.name)
        self._editors["moc"] = ed

    def _moduleCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ModuleCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.modulecode = text
            self.shell.dirty = True

        del self._editors["moc"]

    def _preInitCodeSlot(self):
        """
        Slot to handle %PreInitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._preInitCodeDone)
        ed.edit(self.api_item.preinitcode, "%PreInitialisationCode: " + self.api_item.name)
        self._editors["pric"] = ed

    def _preInitCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PreInitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.preinitcode = text
            self.shell.dirty = True

        del self._editors["pric"]

    def _initCodeSlot(self):
        """
        Slot to handle %InitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._initCodeDone)
        ed.edit(self.api_item.initcode, "%InitialisationCode: " + self.api_item.name)
        self._editors["ic"] = ed

    def _initCodeDone(self, text_changed, text):
        """
        Slot to handle changed %InitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.initcode = text
            self.shell.dirty = True

        del self._editors["ic"]

    def _postInitCodeSlot(self):
        """
        Slot to handle %PostInitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._postInitCodeDone)
        ed.edit(self.api_item.postinitcode, "%PostInitialisationCode: " + self.api_item.name)
        self._editors["poic"] = ed

    def _postInitCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PostInitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.postinitcode = text
            self.shell.dirty = True

        del self._editors["poic"]

    def _exportedTypeHintCodeSlot(self):
        """
        Slot to handle %ExportedTypeHintCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._exportedTypeHintCodeDone)
        ed.edit(self.api_item.exportedtypehintcode, "%ExportedTypeHintCode: " + self.api_item.name)
        self._editors["ethc"] = ed

    def _exportedTypeHintCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ExportedTypeHintCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.exportedtypehintcode = text
            self.shell.dirty = True

        del self._editors["ethc"]

    def _typeHintCodeSlot(self):
        """
        Slot to handle %TypeHintCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typeHintCodeDone)
        ed.edit(self.api_item.typehintcode, "%TypeHintCode: " + self.api_item.name)
        self._editors["thc"] = ed

    def _typeHintCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeHintCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.typehintcode = text
            self.shell.dirty = True

        del self._editors["thc"]

    def _hideIgnoredSlot(self):
        """
        Hide all ignored scope elements.
        """
        self._setIgnoredVisibility(False)

    def _showIgnoredSlot(self):
        """
        Show all ignored scope elements.
        """
        self._setIgnoredVisibility(True)

    def _setIgnoredVisibility(self, visible):
        """
        Set the visibility of all ignored scope elements.

        visible is True if the elements should be visible.
        """
        it = QTreeWidgetItemIterator(self)
        itm = it.value()

        while itm:
            if isinstance(itm, CodeItem) and itm.code.status == "ignored":
                itm.setHidden(not visible)

            it += 1
            itm = it.value()


class Argument(EditorItem):
    """ This class implements a function argument. """

    def __init__(self, shell, parent, arg):
        """ Initialise the argument item. """

        super().__init__(arg, shell, parent)

        self.setFlags(Qt.ItemFlag.ItemIsEnabled)

        self.draw_name()

        # Stash this so that an argument can re-draw itself.
        arg._gui = self

    def draw_name(self):
        """ Draw the name column. """

        self.setText(ApiEditor.NAME,
                self.api_item.user(self.parent().api_item))

    def get_menu(self, siblings):
        """ Return the list of context menu options.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            the menu options.
        """

        if len(siblings) != 0:
            return None

        return [("Properties...", self._handle_argument_properties)]

    def _handle_argument_properties(self):
        """ Slot to handle the argument's properties. """

        dialog = ArgumentPropertiesDialog(self.api_item, "Argument Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True

            self.draw_name()
            self.parent().draw_name()
            self.parent().draw_status()


class CodeItem(ContainerItem):
    """ This class implements an editor item that represents code in a .sip
    file.
    """

    def __init__(self, code, shell, parent, after=None):
        """ Initialise the code item. """

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
            for a in code.args:
                Argument(self.shell, self, a)

    def draw_name(self):
        """ Update the item's name. """

        self.setText(ApiEditor.NAME, self.api_item.user())

    def _draw_access(self):
        """ Update the item's access. """

        # Not everything has an access specifier.
        try:
            access = self.api_item.access
        except AttributeError:
            access = ''

        self.setText(ApiEditor.ACCESS, access)

    def _has_unnamed_args(self):
        """ Returns ``True`` if the code has unnamed arguments. """

        # These types don't use named arguments.
        if isinstance(self.api_item, (OperatorMethod, OperatorCast, OperatorFunction)):
            return False

        # Ignore private items.
        try:
            private = (self.api_item.access == 'private')
        except AttributeError:
            private = False

        if private:
            return False

        for arg in self.api_item.args:
            if arg.unnamed and arg.default != '':
                return True

        return False

    def draw_status(self):
        """ Update the item's status. """

        status = []

        expand = False
        s = self.api_item.status

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

        if s != 'ignored' and hasattr(self.api_item, 'args') and self._has_unnamed_args():
            status.append("Unnamed arguments")
            expand = True

        self.setText(ApiEditor.STATUS, ", ".join(status))

        if expand:
            parent = self.parent()
            while parent is not None:
                if isinstance(parent, CodeItem):
                    if parent.api_item.status == 'ignored':
                        break

                parent.setExpanded(True)
                parent = parent.parent()

    def draw_versions(self):
        """ Update the item's versions. """

        ranges = [version_range(r) for r in self.api_item.versions]
        self.setText(ApiEditor.VERSIONS, ", ".join(ranges))

    def get_menu(self, siblings):
        """ Return the list of context menu options.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            the menu options.
        """

        project = self.shell.project

        # Save the list of targets for the menu action, including this one.
        self._targets = siblings[:]
        self._targets.append(self)

        menu = [("Checked", self._setStatusChecked, True, (self.api_item.status == "")),
                ("Todo", self._setStatusTodo, True, (self.api_item.status == "todo")),
                ("Unchecked", self._setStatusUnchecked, True, (self.api_item.status == "unknown")),
                ("Ignored", self._setStatusIgnored, True, (self.api_item.status == "ignored"))]

        # Handle the access specifiers.
        if isinstance(self.api_item, Access):
                menu.append(None)
                menu.append(("public", self._setAccessPublic, True, (self.api_item.access == "")))
                menu.append(("public slots", self._setAccessPublicSlots, True, (self.api_item.access == "public slots")))
                menu.append(("protected", self._setAccessProtected, True, (self.api_item.access == "protected")))
                menu.append(("protected slots", self._setAccessProtectedSlots, True, (self.api_item.access == "protected slots")))
                menu.append(("private", self._setAccessPrivate, True, (self.api_item.access == "private")))
                menu.append(("private slots", self._setAccessPrivateSlots, True, (self.api_item.access == "private slots")))
                menu.append(("signals", self._setAccessSignals, True, (self.api_item.access == "signals")))

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

        if isinstance(self.api_item, ManualCode):
            menu.append(("Modify manual code...", self._handle_modify_manual_code))
            menu.append(("Modify manual code body...", self._bodyManualCode, ("mcb" not in self._editors)))

            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api_item, Namespace):
            pslot = self._handle_namespace_properties
        elif isinstance(self.api_item, OpaqueClass):
            pslot = self._handle_opaque_class_properties
        elif isinstance(self.api_item, Namespace):
            thcslot = True
        elif isinstance(self.api_item, Class):
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
        elif isinstance(self.api_item, Constructor):
            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api_item, Destructor):
            mcslot = True
            vccslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.api_item, OperatorCast):
            mcslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.api_item, Method):
            mcslot = True

            if self.api_item.virtual:
                vccslot = True

            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api_item, OperatorMethod):
            mcslot = True

            if self.api_item.virtual:
                vccslot = True

            pslot = self._handle_callable_properties
        elif isinstance(self.api_item, Function):
            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.api_item, OperatorFunction):
            mcslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.api_item, Variable):
            acslot = True
            gcslot = True
            scslot = True
            pslot = self._handle_variable_properties
        elif isinstance(self.api_item, Enum):
            pslot = self._handle_enum_properties
        elif isinstance(self.api_item, EnumValue):
            pslot = self._handle_enum_member_properties

        if thcslot or thicslot or tcslot or cttcslot or cftcslot or fcslot or sccslot or mcslot or vccslot or acslot or gcslot or scslot or gctcslot or gcccslot or bigetbslot or birelbslot or birbslot or biwbslot or biscslot or bicbslot or pickslot or xaslot or dsslot:
            menu.append(None)

            if thcslot:
                self._add_directive(menu, '%TypeHeaderCode',
                        self.api_item.typeheadercode, self._typeheaderCodeSlot,
                        'thc')

            if tcslot:
                self._add_directive(menu, '%TypeCode', self.api_item.typecode,
                        self._typeCodeSlot, 'tc')

            if thicslot:
                self._add_directive(menu, '%TypeHintCode',
                        self.api_item.typehintcode, self._typehintCodeSlot, 'thic')

            if fcslot:
                self._add_directive(menu, '%FinalisationCode',
                        self.api_item.finalisationcode, self._finalCodeSlot, 'fc')

            if sccslot:
                self._add_directive(menu, '%ConvertToSubClassCode',
                        self.api_item.subclasscode, self._subclassCodeSlot, 'scc')

            if cttcslot:
                self._add_directive(menu, '%ConvertToTypeCode',
                        self.api_item.convtotypecode, self._convToTypeCodeSlot,
                        'cttc')

            if cftcslot:
                self._add_directive(menu, '%ConvertFromTypeCode',
                        self.api_item.convfromtypecode, self._convFromTypeCodeSlot,
                        'cftc')

            if mcslot:
                self._add_directive(menu, '%MethodCode', self.api_item.methcode,
                        self._methodCodeSlot, 'mc')

            if vccslot:
                self._add_directive(menu, '%VirtualCatcherCode',
                        self.api_item.virtcode, self._virtualCatcherCodeSlot,
                        'vcc')

            if acslot:
                self._add_directive(menu, '%AccessCode', self.api_item.accesscode,
                        self._accessCodeSlot, 'ac')

            if gcslot:
                self._add_directive(menu, '%GetCode', self.api_item.getcode,
                        self._getCodeSlot, 'gc')

            if scslot:
                self._add_directive(menu, '%SetCode', self.api_item.setcode,
                        self._setCodeSlot, 'sc')

            if gctcslot:
                self._add_directive(menu, '%GCTraverseCode',
                        self.api_item.gctraversecode, self._gcTraverseCodeSlot,
                        'gctc')

            if gcccslot:
                self._add_directive(menu, '%GCClearCode',
                        self.api_item.gcclearcode, self._gcClearCodeSlot, 'gccc')

            if bigetbslot:
                self._add_directive(menu, '%BIGetBufferCode',
                        self.api_item.bigetbufcode, self._biGetBufCodeSlot,
                        'bigetb')

            if birelbslot:
                self._add_directive(menu, '%BIReleaseBufferCode',
                        self.api_item.birelbufcode, self._biRelBufCodeSlot,
                        'birelb')

            if birbslot:
                self._add_directive(menu, '%BIGetReadBufferCode',
                        self.api_item.bireadbufcode, self._biReadBufCodeSlot,
                        'birb')

            if biwbslot:
                self._add_directive(menu, '%BIGetWriteBufferCode',
                        self.api_item.biwritebufcode, self._biWriteBufCodeSlot,
                        'biwb')

            if biscslot:
                self._add_directive(menu, '%BIGetSegCountCode',
                        self.api_item.bisegcountcode, self._biSegCountCodeSlot,
                        'bisc')

            if bicbslot:
                self._add_directive(menu, '%BIGetCharBufferCode',
                        self.api_item.bicharbufcode, self._biCharBufCodeSlot,
                        'bicb')

            if pickslot:
                self._add_directive(menu, '%PickleCode', self.api_item.picklecode,
                        self._pickleCodeSlot, 'pick')

            if dsslot:
                self._add_directive(menu, '%Docstring', self.api_item.docstring,
                        self._docstringSlot, 'ds')

        if isinstance(self.api_item, (Class, Constructor, Function, Method)):
            menu.append(None)
            menu.append(("Accept all argument names", self._acceptNames))

        # Add the extra menu items.
        menu.append(None)
        menu.append(("Versions...", self._handle_versions,
                len(project.versions) != 0))
        menu.append(
                (self._flagged_text("Platform Tags...", self.api_item.platforms),
                        self._handle_platforms, len(project.platforms) != 0))
        menu.append(
                (self._flagged_text("Feature Tags...", self.api_item.features),
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

        self.treeWidget().acceptArgumentNames(self.api_item)

    def _handle_add_manual_code(self):
        """ Slot to handle the addition of manual code. """

        manual_code = ManualCode()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code", self.shell)

        if dialog.update():
            parent_content = self.parent().api_item.content
            parent_content.insert(parent_content.index(self.api_item) + 1,
                    manual_code)
            self.shell.dirty = True

    def _handle_modify_manual_code(self):
        """ Slot to handle the update of the manual code. """

        dialog = ManualCodeDialog(self.api_item, "Modify Manual Code", self.shell)

        if dialog.update():
            self.shell.dirty = True

            self.draw_name()

    def _bodyManualCode(self):
        """
        Slot to handle the update of the manual code body.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._mcBodyDone)
        ed.edit(self.api_item.body, "Manual Code: " + self.api_item.precis)
        self._editors["mcb"] = ed

    def _mcBodyDone(self, text_changed, text):
        """
        Slot to handle changed manual code body.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.body = text
            self.shell.dirty = True

        del self._editors["mcb"]

    def _deleteCode(self):
        """
        Slot to handle the deletion of one or more code items.
        """
        what = "this part" if len(self._targets) == 1 else "these parts"
        ans = QMessageBox.question(self.treeWidget(), "Delete Code",
                "Are you sure you want to delete {0} of the API?".format(what),
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

        if ans is QMessageBox.StandardButton.Yes:
            # Mark as dirty before removing them.
            self.shell.dirty = True

            for target in self._targets:
                self.parent().api_item.content.remove(target.api_item)

    def _accessCodeSlot(self):
        """
        Slot to handle %AccessCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._accessCodeDone)
        ed.edit(self.api_item.accesscode, "%AccessCode: " + self.api_item.user())
        self._editors["ac"] = ed

    def _accessCodeDone(self, text_changed, text):
        """
        Slot to handle changed %AccessCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.accesscode = text
            self.shell.dirty = True

        del self._editors["ac"]

    def _getCodeSlot(self):
        """
        Slot to handle %GetCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._getCodeDone)
        ed.edit(self.api_item.getcode, "%GetCode: " + self.api_item.user())
        self._editors["gc"] = ed

    def _getCodeDone(self, text_changed, text):
        """
        Slot to handle changed %GetCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.getcode = text
            self.shell.dirty = True

        del self._editors["gc"]

    def _setCodeSlot(self):
        """
        Slot to handle %SetCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._setCodeDone)
        ed.edit(self.api_item.setcode, "%SetCode: " + self.api_item.user())
        self._editors["sc"] = ed

    def _setCodeDone(self, text_changed, text):
        """
        Slot to handle changed %SetCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.setcode = text
            self.shell.dirty = True

        del self._editors["sc"]

    def _typehintCodeSlot(self):
        """
        Slot to handle %TypeHintCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typehintCodeDone)
        ed.edit(self.api_item.typeheadercode, "%TypeHintCode: " + self.api_item.user())
        self._editors["thic"] = ed

    def _typehintCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeHintCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.typehintcode = text
            self.shell.dirty = True

        del self._editors["thic"]

    def _typeheaderCodeSlot(self):
        """
        Slot to handle %TypeHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typeheaderCodeDone)
        ed.edit(self.api_item.typeheadercode, "%TypeHeaderCode: " + self.api_item.user())
        self._editors["thc"] = ed

    def _typeheaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.typeheadercode = text
            self.shell.dirty = True

        del self._editors["thc"]

    def _typeCodeSlot(self):
        """
        Slot to handle %TypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typeCodeDone)
        ed.edit(self.api_item.typecode, "%TypeCode: " + self.api_item.user())
        self._editors["tc"] = ed

    def _typeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.typecode = text
            self.shell.dirty = True

        del self._editors["tc"]

    def _convToTypeCodeSlot(self):
        """
        Slot to handle %ConvertToTypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._convToTypeCodeDone)
        ed.edit(self.api_item.convtotypecode, "%ConvertToTypeCode: " + self.api_item.user())
        self._editors["cttc"] = ed

    def _convToTypeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertToTypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.convtotypecode = text
            self.shell.dirty = True

        del self._editors["cttc"]

    def _convFromTypeCodeSlot(self):
        """
        Slot to handle %ConvertFromTypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._convFromTypeCodeDone)
        ed.edit(self.api_item.convfromtypecode, "%ConvertFromTypeCode: " + self.api_item.user())
        self._editors["cftc"] = ed

    def _convFromTypeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertFromTypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.convfromtypecode = text
            self.shell.dirty = True

        del self._editors["cftc"]

    def _gcTraverseCodeSlot(self):
        """
        Slot to handle %GCTraverseCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._gcTraverseCodeDone)
        ed.edit(self.api_item.gctraversecode, "%GCTraverseCode: " + self.api_item.user())
        self._editors["gctc"] = ed

    def _gcTraverseCodeDone(self, text_changed, text):
        """
        Slot to handle changed %GCTraverseCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.gctraversecode = text
            self.shell.dirty = True

        del self._editors["gctc"]

    def _gcClearCodeSlot(self):
        """
        Slot to handle %GCClearCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._gcClearCodeDone)
        ed.edit(self.api_item.gcclearcode, "%GCClearCode: " + self.api_item.user())
        self._editors["gccc"] = ed

    def _gcClearCodeDone(self, text_changed, text):
        """
        Slot to handle changed %GCClearCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.gcclearcode = text
            self.shell.dirty = True

        del self._editors["gccc"]

    def _biGetBufCodeSlot(self):
        """
        Slot to handle %BIGetBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biGetBufCodeDone)
        ed.edit(self.api_item.bigetbufcode, "%BIGetBufferCode: " + self.api_item.user())
        self._editors["bigetb"] = ed

    def _biGetBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.bigetbufcode = text
            self.shell.dirty = True

        del self._editors["bigetb"]

    def _biRelBufCodeSlot(self):
        """
        Slot to handle %BIReleaseBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biRelBufCodeDone)
        ed.edit(self.api_item.birelbufcode, "%BIReleaseBufferCode: " + self.api_item.user())
        self._editors["birelb"] = ed

    def _biRelBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIReleaseBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.birelbufcode = text
            self.shell.dirty = True

        del self._editors["birelb"]

    def _biReadBufCodeSlot(self):
        """
        Slot to handle %BIGetReadBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biReadBufCodeDone)
        ed.edit(self.api_item.bireadbufcode, "%BIGetReadBufferCode: " + self.api_item.user())
        self._editors["birb"] = ed

    def _biReadBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetReadBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.bireadbufcode = text
            self.shell.dirty = True

        del self._editors["birb"]

    def _biWriteBufCodeSlot(self):
        """
        Slot to handle %BIGetWriteBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biWriteBufCodeDone)
        ed.edit(self.api_item.biwritebufcode, "%BIGetWriteBufferCode: " + self.api_item.user())
        self._editors["biwb"] = ed

    def _biWriteBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetWriteBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.biwritebufcode = text
            self.shell.dirty = True

        del self._editors["biwb"]

    def _biSegCountCodeSlot(self):
        """
        Slot to handle %BIGetSegCountCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biSegCountCodeDone)
        ed.edit(self.api_item.bisegcountcode, "%BIGetSegCountCode: " + self.api_item.user())
        self._editors["bisc"] = ed

    def _biSegCountCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetSegCountCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.bisegcountcode = text
            self.shell.dirty = True

        del self._editors["bisc"]

    def _biCharBufCodeSlot(self):
        """
        Slot to handle %BIGetCharBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biCharBufCodeDone)
        ed.edit(self.api_item.bicharbufcode, "%BIGetCharBufferCode: " + self.api_item.user())
        self._editors["bicb"] = ed

    def _biCharBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetCharBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.bicharbufcode = text
            self.shell.dirty = True

        del self._editors["bicb"]

    def _pickleCodeSlot(self):
        """
        Slot to handle %PickleCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._pickleCodeDone)
        ed.edit(self.api_item.picklecode, "%PickleCode: " + self.api_item.user())
        self._editors["pick"] = ed

    def _pickleCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PickleCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.picklecode = text
            self.shell.dirty = True

        del self._editors["pick"]

    def _finalCodeSlot(self):
        """
        Slot to handle %FinalisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._finalCodeDone)
        ed.edit(self.api_item.finalisationcode, "%FinalisationCode: " + self.api_item.user())
        self._editors["fc"] = ed

    def _finalCodeDone(self, text_changed, text):
        """
        Slot to handle changed %FinalisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.finalisationcode = text
            self.shell.dirty = True

        del self._editors["fc"]

    def _subclassCodeSlot(self):
        """
        Slot to handle %ConvertToSubClassCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._subclassCodeDone)
        ed.edit(self.api_item.subclasscode, "%ConvertToSubClassCode: " + self.api_item.user())
        self._editors["scc"] = ed

    def _subclassCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertToSubClassCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.subclasscode = text
            self.shell.dirty = True

        del self._editors["scc"]

    def _docstringSlot(self):
        """
        Slot to handle %Docstring.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._docstringDone)
        ed.edit(self.api_item.docstring, "%Docstring: " + self.api_item.user())
        self._editors["ds"] = ed

    def _docstringDone(self, text_changed, text):
        """
        Slot to handle changed %Docstring.

        text_changed is set if the code has changed.
        text is the changed docstring.
        """
        if text_changed:
            self.api_item.docstring = text
            self.shell.dirty = True

        del self._editors["ds"]

    def _methodCodeSlot(self):
        """
        Slot to handle %MethodCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._methodCodeDone)
        ed.edit(self.api_item.methcode, "%MethodCode: " + self.api_item.user())
        self._editors["mc"] = ed

    def _methodCodeDone(self, text_changed, text):
        """
        Slot to handle changed %MethodCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.methcode = text
            self.shell.dirty = True

        del self._editors["mc"]

    def _virtualCatcherCodeSlot(self):
        """
        Slot to handle %VirtualCatcherCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._virtualCatcherCodeDone)
        ed.edit(self.api_item.virtcode, "%VirtualCatcherCode: " + self.api_item.user())
        self._editors["vcc"] = ed

    def _virtualCatcherCodeDone(self, text_changed, text):
        """
        Slot to handle changed %VirtualCatcherCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.api_item.virtcode = text
            self.shell.dirty = True

        del self._editors["vcc"]

    def _handle_versions(self):
        """ Slot to handle the versions. """

        dialog = VersionsDialog(self.api_item, "Versions", self.shell)

        if dialog.update():
            # Apply the version range to all targets.
            for itm in self._targets:
                if itm.api_item is not self.api_item:
                    itm.api_item.versions = list(self.api_item.versions)

            self.shell.dirty = True

    def _handle_platforms(self):
        """ Slot to handle the platforms. """

        dialog = PlatformsDialog(self.api_item, "Platform Tags", self.shell)

        if dialog.update():
            self.shell.dirty = True

    def _handle_features(self):
        """ Slot to handle the features. """

        dialog = FeaturesDialog(self.api_item, "Feature Tags", self.shell)

        if dialog.update():
            self.shell.dirty = True

    def _handle_namespace_properties(self):
        """ Slot to handle the properties for namespaces. """

        dialog = NamespacePropertiesDialog(self.api_item, "Namespace Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _handle_opaque_class_properties(self):
        """ Slot to handle the properties for opaque classes. """

        dialog = OpaqueClassPropertiesDialog(self.api_item,
                "Opaque Class Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _handle_class_properties(self):
        """ Slot to handle the properties for classes. """

        dialog = ClassPropertiesDialog(self.api_item, "Class Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _handle_callable_properties(self):
        """ Slot to handle the properties for callables. """

        dialog = CallablePropertiesDialog(self.api_item, 'Placeholder', self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _handle_variable_properties(self):
        """ Slot to handle the properties for variables. """

        dialog = VariablePropertiesDialog(self.api_item, "Variable Properties",
                self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _handle_enum_properties(self):
        """ Slot to handle the properties for enums. """

        dialog = EnumPropertiesDialog(self.api_item, "Enum Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _handle_enum_member_properties(self):
        """ Slot to handle the properties for enum members. """

        dialog = EnumMemberPropertiesDialog(self.api_item,
                "Enum Member Properties", self.shell)

        if dialog.update():
            self.shell.dirty = True
            self.setText(ApiEditor.NAME, self.api_item.user())

    def _setStatusChecked(self):
        """
        Slot to handle the status being set to checked.
        """
        self._setStatus("")

    def _setStatusTodo(self):
        """
        Slot to handle the status being set to todo.
        """
        self._setStatus("todo")

    def _setStatusUnchecked(self):
        """
        Slot to handle the status being set to unchecked.
        """
        self._setStatus("unknown")

    def _setStatusIgnored(self):
        """
        Slot to handle the status being set to ignored.
        """
        self._setStatus("ignored")

    def _setStatus(self, new):
        """
        Set the status column.

        new is the new status.
        """
        for itm in self._targets:
            if itm.api_item.status != new:
                itm.api_item.status = new
                self.shell.dirty = True

                # FIXME: Observe the status attribute.
                itm.draw_status()

    def _setAccessPublic(self):
        """
        Slot to handle the access being set to public.
        """
        self._setAccess("")

    def _setAccessPublicSlots(self):
        """
        Slot to handle the access being set to public slots.
        """
        self._setAccess("public slots")

    def _setAccessProtected(self):
        """
        Slot to handle the access being set to protected.
        """
        self._setAccess("protected")

    def _setAccessProtectedSlots(self):
        """
        Slot to handle the access being set to protected slots.
        """
        self._setAccess("protected slots")

    def _setAccessPrivate(self):
        """
        Slot to handle the access being set to private.
        """
        self._setAccess("private")

    def _setAccessPrivateSlots(self):
        """
        Slot to handle the access being set to private slots.
        """
        self._setAccess("private slots")

    def _setAccessSignals(self):
        """
        Slot to handle the access being set to signals.
        """
        self._setAccess("signals")

    def _setAccess(self, new):
        """
        Set the access column.

        new is the new access.
        """
        for itm in self._targets:
            if itm.api_item.access != new:
                itm.api_item.access = new
                self.shell.dirty = True

                # FIXME: Observe the access attribute.
                itm._draw_access()
