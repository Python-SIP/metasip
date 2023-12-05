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
from PyQt6.QtWidgets import (QApplication, QDialog, QInputDialog, QMenu,
        QMessageBox, QProgressDialog, QTreeWidget, QTreeWidgetItem,
        QTreeWidgetItemIterator, QVBoxLayout)

from ....dip.model import observe

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

    def __init__(self, tool):
        """ Initialise the editor. """

        super().__init__()

        self._tool = tool

        # Tweak the tree widget.
        self.setHeaderLabels(("Name", "Access", "Status", "Versions"))
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)

        self.dragged = None

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('header')
        if state is not None:
            self.header().restoreState(state)

    def set_project(self):
        """ Set the current project. """

        self.clear()

        ProjectItem(self._tool.shell.project, self)

    def set_dirty(self):
        """ Mark the project as having been modified. """

        self._tool.shell.dirty = True

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('header', self.header().saveState())

    def contextMenuEvent(self, ev):
        """
        Reimplemented to handle a context menu event.

        ev is the event.
        """
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
        """
        Reimplemented to start the drag of an item.
        """
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
        """
        Reimplemented to validate a drag enter.
        """
        if ev.source() is self:
            ev.accept()
        else:
            ev.ignore()

    def dragMoveEvent(self, ev):
        """
        Reimplemented to validate a drag move.
        """
        if ev.source() is self:
            ev.accept()
        else:
            ev.ignore()

    def dropEvent(self, ev):
        """
        Reimplemented to handle a drop.
        """
        source_target = self._source_target(ev)

        if source_target is None:
            ev.ignore()
        else:
            source, target = source_target
            target.drop(source)
            ev.accept()

    def _source_target(self, ev):
        """
        Return a tuple of source and target items or None if the drop wasn't
        appropriate.
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

    def acceptArgumentNames(self, prj_item):
        """
        Mark the arguments of all callables contained in a part of a project
        as being named.

        prj_item is the part of the project.
        """
        self._updateArgs(
                self._tool.shell.project.acceptArgumentNames(prj_item))

    @staticmethod
    def _updateArgs(updated_args):
        """
        Update the GUI for those arguments that have been updated.

        updated_args is the list of updated Argument instances.
        """
        callables = []
        for arg in updated_args:
            arg._gui.draw_name()

            callable = arg._gui.parent()
            if callable not in callables:
                callables.append(callable)

        for callable in callables:
            callable.draw_name()
            callable.draw_status()

    def _stringDialog(self, caption, strings):
        """
        Show a dialog containing a list of strings.

        caption is the dialog's caption.
        strings is the list of strings.
        """
        dlg = QDialog(self)
        dlg.setWindowTitle(caption)

        box = QListBox(dlg)

        for itm in strings:
            box.insertItem(itm)

        layout = QVBoxLayout(dlg)
        layout.addWidget(box)

        dlg.show()


class DropSite():
    """ This mixin class implements a drop site.  Any derived class must also
    derive QTreeWidgetItem.
    """

    def __init__(self):
        """ Initialise the instance. """

        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsDropEnabled)

    def droppable(self, source):
        """ Determine if an item can be dropped.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        :return:
            ``True`` if the source can be dropped.
        """

        raise NotImplementedError

    def drop(self, source):
        """ Handle the drop of an item.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        """

        raise NotImplementedError


# Each QTreeWidgetItem has a unique key used in the DND support.
_item_id = QTreeWidgetItem.ItemType.UserType


class EditorItem(QTreeWidgetItem):
    """ This class represents an item in the API editor. """

    def __init__(self, parent, after=None):
        """ Initialise the item instance.

        :param parent:
            is the parent.
        :param after:
            is the sibling after which this should be placed.  If it is
            ``None`` then it should be placed at the end.  If it is the parent
            then it should be placed at the start.
        """

        global _item_id
        item_id = _item_id
        _item_id += 1

        if after is parent:
            super().__init__(parent, None, item_id)
        elif after is None:
            super().__init__(parent, item_id)
        else:
            super().__init__(parent, after, item_id)

    def get_menu(self, siblings):
        """ Return the list of context menu options or None if the item doesn't
        have a context menu.  Each element is a tuple of the text of the
        option, the bound method that handles the option, and a flag that is
        True if the option should be enabled.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            this implementation always returns ``None``.
        """

        return None

    def set_dirty(self):
        """ Mark the project as having been modified. """

        self.treeWidget().set_dirty()


class ProjectItem(EditorItem):
    """ This class implements a navigation item that represents a project. """

    def __init__(self, project, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._project = project

        # TODO - use the name of the root module instead. If there is none then
        # omit this root item.  Get rid of descriptive_name() etc.
        self.setText(ApiEditor.NAME, project.descriptive_name())
        observe('name', project,
                lambda c: self.setText(ApiEditor.NAME,
                        c.model.descriptive_name()))

        self.setExpanded(True)

        # Progress will be reported against .sip files so count them all.
        nr_steps = 0
        for module in project.modules:
            nr_steps += len(module.content)

        # Display the progress dialog.
        progress = QProgressDialog( "Building the GUI...", None, 0, nr_steps)
        progress.setWindowTitle(project.name)
        progress.setValue(0)

        so_far = 0
        for mod in project.modules:
            ModuleItem(mod, self, progress, so_far)
            so_far += len(mod.content)

        observe('modules', project, self.__on_modules_changed)

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

    def _ignorednamespaceSlot(self):
        """ Handle adding a new ignored namespace. """

        project = self._project
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
                self.set_dirty()

    def _handle_project_properties(self):
        """ Handle the project's properties. """

        dialog = ProjectPropertiesDialog(self._project, "Project Properties",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()

    def __on_modules_changed(self, change):
        """ Invoked when the list of modules changes. """

        for mod in change.old:
            for idx in range(self.childCount()):
                itm = self.child(idx)
                if itm.module is mod:
                    self.removeChild(itm)
                    break

        for mod in change.new:
            ModuleItem(mod, self)

        self._sort()

    def _sort(self):
        """ Sort the modules. """

        self.sortChildren(ApiEditor.NAME, Qt.SortOrder.AscendingOrder)


class ModuleItem(EditorItem, DropSite):
    """ This class implements an editor item that represents a module. """

    def __init__(self, module, parent, progress=None, so_far=0):
        """ Initialise the item instance.

        :param module:
            is the module instance.
        :param parent:
            is the parent.
        :param progress:
            is the optional progress dialog to update.
        :param so_far:
            is the optional count of items processed so far.
        """

        EditorItem.__init__(self, parent)
        DropSite.__init__(self)

        self.module = module

        self.setText(ApiEditor.NAME, module.name)

        for sf in module.content:
            SipFileItem(sf, self)

            if progress is not None:
                so_far += 1
                progress.setValue(so_far)
                QApplication.processEvents()

        observe('name', module, self.__on_name_changed)
        observe('content', module, self.__on_content_changed)

    def droppable(self, source):
        """ Determine if an item can be dropped.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        :return:
            ``True`` if the source can be dropped.
        """

        # We allow .sip files to be moved around anywhere.
        return isinstance(source, SipFileItem)

    def drop(self, source):
        """ Handle the drop of an item.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        """

        # The .sip file is always placed at the top.
        sf = source.sipfile
        dst_sipfiles = self.module.content
        src_sipfiles = source.parent().module.content

        src_sipfiles.remove(sf)
        dst_sipfiles.insert(0, sf)

        self.set_dirty()

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

        dialog = ModulePropertiesDialog(self.module, "Module Properties",
                self.treeWidget(), project=self.treeWidget().project)

        if dialog.update():
            self.set_dirty()

    def __on_name_changed(self, change):
        """ Invoked when the name changes. """

        self.setText(ApiEditor.NAME, change.new)
        self.parent().sortChildren(ApiEditor.NAME, Qt.SortOrder.AscendingOrder)

    def __on_content_changed(self, change):
        """ Invoked when the content changes. """

        for sf in change.old:
            for idx in range(self.childCount()):
                itm = self.child(idx)
                if itm.sipfile is sf:
                    self.removeChild(itm)
                    break

        # The order of view items must match the order of model items.
        module_content = change.model.content
        idx_list = [module_content.index(sf) for sf in change.new]
        idx_list.sort()

        for idx in idx_list:
            after = self if idx == 0 else self.child(idx - 1)

            SipFileItem(module_content[idx], self, after)


class ContainerItem(EditorItem, DropSite):
    """ This class implements an editor item that represents a potential
    container for code items.
    """

    def __init__(self, container, parent, after):
        """ Initialise the item instance.

        :param container:
            is the potential container instance.
        :param parent:
            is the parent.
        :param after:
            is the sibling after which this should be placed.  If it is
            ``None`` then it should be placed at the end.  If it is the parent
            then it should be placed at the start.
        """

        EditorItem.__init__(self, parent, after)
        DropSite.__init__(self)

        if hasattr(container, 'content'):
            for code in container.content:
                CodeItem(code, self)

            observe('content', container, self.__on_content_changed)

    def droppable(self, source):
        """ Determine if an item can be dropped.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        :return:
            ``True`` if the source can be dropped.
        """

        # See if we are moving a sibling.
        if source.parent() is self.parent():
            return True

        # See if we are moving a child to the top.
        if source.parent() is self:
            return True

        return False

    def drop(self, source):
        """ Handle the drop of an item.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        """

        if source.parent() is self.parent():
            # We are moving a sibling after us.
            parent_content = self.parent_project_item().content
            project_item = source.project_item()

            parent_content.remove(project_item)

            new_idx = parent_content.index(self.project_item()) + 1
            if new_idx < len(parent_content):
                parent_content.insert(new_idx, project_item)
            else:
                parent_content.append(project_item)

            self.set_dirty()

            return

        if source.parent() is self:
            # Dropping a child is interpreted as moving it to the top.
            my_content = self.project_item().content
            project_item = source.project_item()

            my_content.remove(project_item)
            my_content.insert(0, project_item)

            self.set_dirty()

            return

    def parent_project_item(self):
        """ Return the parent project item that contains our project item. """

        raise NotImplementedError

    def project_item(self):
        """ Return our project item. """

        raise NotImplementedError

    def __on_content_changed(self, change):
        """ Invoked when the content changes. """

        for code in change.old:
            for idx in range(self.childCount()):
                itm = self.child(idx)
                if itm.code is code:
                    self.removeChild(itm)
                    break

        # The order of editor items must match the order of model items.
        container_content = change.model.content
        idx_list = [container_content.index(code) for code in change.new]
        idx_list.sort()

        for idx in idx_list:
            after = self if idx == 0 else self.child(idx - 1)

            CodeItem(container_content[idx], self, after)


class SipFileItem(ContainerItem):
    """ This class implements an editor item that represents a .sip file. """

    def __init__(self, sipfile, parent, after=None):
        """ Initialise the item instance.

        :param sipfile:
            is the .sip file instance.
        :param parent:
            is the parent.
        :param after:
            is the sibling after which this should be placed.  If it is
            ``None`` then it should be placed at the end.  If it is the parent
            then it should be placed at the start.
        """

        super().__init__(sipfile, parent, after)

        self.sipfile = sipfile

        self._targets = []
        self._editors = {}

        self.setText(ApiEditor.NAME, sipfile.name)

    def droppable(self, source):
        """ Determine if an item can be dropped.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        :return:
            ``True`` if the source can be dropped.
        """

        # See if we are moving another .sip file.
        if isinstance(source, SipFileItem):
            return True

        # See if we are moving a child to the top.
        if source.parent() is self:
            return True

        return False

    def drop(self, source):
        """ Handle the drop of an item.

        :param source:
            is the QTreeWidgetItem sub-class instance being dropped.
        """

        if isinstance(source, SipFileItem):
            # We are moving another .sip file after us.  First remove the item
            # from its container.
            source.parent().module.content.remove(source.sipfile)

            # Now add it to our container.
            content = self.parent().module.content
            idx = content.index(self.sipfile) + 1
            if idx < len(content):
                content.insert(idx, source.sipfile)
            else:
                content.append(source.sipfile)

            self.set_dirty()

            return

        if source.parent() is self:
            # Dropping a child is interpreted as moving it to the top.
            content = self.sipfile.content
            code = source.code

            content.remove(code)
            content.insert(0, code)

            self.set_dirty()

            return

    def parent_project_item(self):
        """ Return the parent project item that contains our project item. """

        return self.parent().module

    def project_item(self):
        """ Return our project item. """

        return self.sipfile

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
        for code in self.sipfile.content:
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

        src_module = self.parent_project_item()

        dialog = MoveHeaderDialog(src_module, "Move Header File",
                self.treeWidget(), project=self.treeWidget().project)

        dst_module = dialog.get_destination_module()
        if dst_module is not None:
            # Mark as dirty before moving it.
            self.set_dirty()

            src_module.content.remove(self.sipfile)
            dst_module.content.append(self.sipfile)

    def _deleteFile(self):
        """ Delete an empty .sip file. """

        ans = QMessageBox.question(self.treeWidget(), "Delete header file",
                "Are you sure you want to delete this header file?",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

        if ans is QMessageBox.StandardButton.Yes:
            # Mark as dirty before removing it.
            self.set_dirty()

            self.parent_project_item().content.remove(self.sipfile)

    def _acceptNames(self):
        """ Accept all argument names. """

        self.treeWidget().acceptArgumentNames(self.sipfile)

    def _handle_add_manual_code(self):
        """ Slot to handle the creation of manual code. """

        manual_code = ManualCode()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code",
                self.treeWidget())

        if dialog.update():
            self.sipfile.content.insert(0, manual_code)
            self.set_dirty()

    def _exportedHeaderCodeSlot(self):
        """
        Slot to handle %ExportedHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._exportedHeaderCodeDone)
        ed.edit(self.sipfile.exportedheadercode, "%ExportedHeaderCode: " + self.sipfile.name)
        self._editors["ehc"] = ed

    def _exportedHeaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ExportedHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.exportedheadercode = text
            self.set_dirty()

        del self._editors["ehc"]

    def _moduleHeaderCodeSlot(self):
        """
        Slot to handle %ModuleHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._moduleHeaderCodeDone)
        ed.edit(self.sipfile.moduleheadercode, "%ModuleHeaderCode: " + self.sipfile.name)
        self._editors["mhc"] = ed

    def _moduleHeaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ModuleHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.moduleheadercode = text
            self.set_dirty()

        del self._editors["mhc"]

    def _moduleCodeSlot(self):
        """
        Slot to handle %ModuleCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._moduleCodeDone)
        ed.edit(self.sipfile.modulecode, "%ModuleCode: " + self.sipfile.name)
        self._editors["moc"] = ed

    def _moduleCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ModuleCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.modulecode = text
            self.set_dirty()

        del self._editors["moc"]

    def _preInitCodeSlot(self):
        """
        Slot to handle %PreInitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._preInitCodeDone)
        ed.edit(self.sipfile.preinitcode, "%PreInitialisationCode: " + self.sipfile.name)
        self._editors["pric"] = ed

    def _preInitCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PreInitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.preinitcode = text
            self.set_dirty()

        del self._editors["pric"]

    def _initCodeSlot(self):
        """
        Slot to handle %InitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._initCodeDone)
        ed.edit(self.sipfile.initcode, "%InitialisationCode: " + self.sipfile.name)
        self._editors["ic"] = ed

    def _initCodeDone(self, text_changed, text):
        """
        Slot to handle changed %InitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.initcode = text
            self.set_dirty()

        del self._editors["ic"]

    def _postInitCodeSlot(self):
        """
        Slot to handle %PostInitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._postInitCodeDone)
        ed.edit(self.sipfile.postinitcode, "%PostInitialisationCode: " + self.sipfile.name)
        self._editors["poic"] = ed

    def _postInitCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PostInitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.postinitcode = text
            self.set_dirty()

        del self._editors["poic"]

    def _exportedTypeHintCodeSlot(self):
        """
        Slot to handle %ExportedTypeHintCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._exportedTypeHintCodeDone)
        ed.edit(self.sipfile.exportedtypehintcode, "%ExportedTypeHintCode: " + self.sipfile.name)
        self._editors["ethc"] = ed

    def _exportedTypeHintCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ExportedTypeHintCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.exportedtypehintcode = text
            self.set_dirty()

        del self._editors["ethc"]

    def _typeHintCodeSlot(self):
        """
        Slot to handle %TypeHintCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typeHintCodeDone)
        ed.edit(self.sipfile.typehintcode, "%TypeHintCode: " + self.sipfile.name)
        self._editors["thc"] = ed

    def _typeHintCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeHintCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.sipfile.typehintcode = text
            self.set_dirty()

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

    def __init__(self, parent, arg):
        """
        Initialise the item instance.

        parent is the parent.
        arg is the argument instance.
        """
        self.arg = arg

        super().__init__(parent)

        self.setFlags(Qt.ItemFlag.ItemIsEnabled)

        self.draw_name()

        # Stash this so that an argument can re-draw itself.
        arg._gui = self

    def draw_name(self):
        """ Draw the name column. """

        self.setText(ApiEditor.NAME, self.arg.user(self.parent().code))

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

        dialog = ArgumentPropertiesDialog(self.arg, "Argument Properties",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()

            self.draw_name()
            self.parent().draw_name()
            self.parent().draw_status()


class CodeItem(ContainerItem):
    """ This class implements an editor item that represents code in a .sip
    file.
    """

    def __init__(self, code, parent, after=None):
        """ Initialise the item instance.

        :param code:
            is the code instance.
        :param parent:
            is the parent.
        :param after:
            is the sibling after which this should be placed.  If it is
            ``None`` then it should be placed at the end.  If it is the parent
            then it should be placed at the start.
        """

        self.code = code

        super().__init__(code, parent, after)

        self._targets = []
        self._editors = {}

        self.draw_name()
        self._draw_access()
        self.draw_status()
        self._draw_versions()

        if code.status == 'ignored':
            self.setHidden(True)

        # Create any children.
        if hasattr(code, 'args'):
            for a in code.args:
                Argument(self, a)

        observe('status', code, self.__on_status_changed)
        observe('versions', code, self.__on_versions_changed)

    def parent_project_item(self):
        """ Return the parent project item that contains our project item. """

        return self.parent().project_item()

    def project_item(self):
        """ Return our project item. """

        return self.code

    def draw_name(self):
        """ Update the item's name. """

        self.setText(ApiEditor.NAME, self.code.user())

    def _draw_access(self):
        """ Update the item's access. """

        # Not everything has an access specifier.
        try:
            access = self.code.access
        except AttributeError:
            access = ''

        self.setText(ApiEditor.ACCESS, access)

    def _has_unnamed_args(self):
        """ Returns ``True`` if the code has unnamed arguments. """

        # These types don't use named arguments.
        if isinstance(self.code, (OperatorMethod, OperatorCast, OperatorFunction)):
            return False

        # Ignore private items.
        try:
            private = (self.code.access == 'private')
        except AttributeError:
            private = False

        if private:
            return False

        for arg in self.code.args:
            if arg.unnamed and arg.default != '':
                return True

        return False

    def draw_status(self):
        """ Update the item's status. """

        status = []

        expand = False
        s = self.code.status

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

        if s != 'ignored' and hasattr(self.code, 'args') and self._has_unnamed_args():
            status.append("Unnamed arguments")
            expand = True

        self.setText(ApiEditor.STATUS, ", ".join(status))

        if expand:
            parent = self.parent()
            while parent is not None:
                if isinstance(parent, CodeItem):
                    if parent.code.status == 'ignored':
                        break

                parent.setExpanded(True)
                parent = parent.parent()

    def __on_status_changed(self, change):
        """ Invoked when the code's status changes. """

        self.draw_status()

    def _draw_versions(self):
        """ Update the item's versions. """

        ranges = [version_range(r) for r in self.code.versions]
        self.setText(ApiEditor.VERSIONS, ", ".join(ranges))

    def __on_versions_changed(self, change):
        """ Invoked when the code's versions changes. """

        self._draw_versions()

    def get_menu(self, siblings):
        """ Return the list of context menu options.

        :param siblings:
            is a list of siblings of the item that is also selected.
        :return:
            the menu options.
        """

        project = self.treeWidget().project

        # Save the list of targets for the menu action, including this one.
        self._targets = siblings[:]
        self._targets.append(self)

        menu = [("Checked", self._setStatusChecked, True, (self.code.status == "")),
                ("Todo", self._setStatusTodo, True, (self.code.status == "todo")),
                ("Unchecked", self._setStatusUnchecked, True, (self.code.status == "unknown")),
                ("Ignored", self._setStatusIgnored, True, (self.code.status == "ignored"))]

        # Handle the access specifiers.
        if isinstance(self.code, Access):
                menu.append(None)
                menu.append(("public", self._setAccessPublic, True, (self.code.access == "")))
                menu.append(("public slots", self._setAccessPublicSlots, True, (self.code.access == "public slots")))
                menu.append(("protected", self._setAccessProtected, True, (self.code.access == "protected")))
                menu.append(("protected slots", self._setAccessProtectedSlots, True, (self.code.access == "protected slots")))
                menu.append(("private", self._setAccessPrivate, True, (self.code.access == "private")))
                menu.append(("private slots", self._setAccessPrivateSlots, True, (self.code.access == "private slots")))
                menu.append(("signals", self._setAccessSignals, True, (self.code.access == "signals")))

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

        if isinstance(self.code, ManualCode):
            menu.append(("Modify manual code...", self._handle_modify_manual_code))
            menu.append(("Modify manual code body...", self._bodyManualCode, ("mcb" not in self._editors)))

            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.code, Namespace):
            pslot = self._handle_namespace_properties
        elif isinstance(self.code, OpaqueClass):
            pslot = self._handle_opaque_class_properties
        elif isinstance(self.code, Namespace):
            thcslot = True
        elif isinstance(self.code, Class):
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
        elif isinstance(self.code, Constructor):
            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.code, Destructor):
            mcslot = True
            vccslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.code, OperatorCast):
            mcslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.code, Method):
            mcslot = True

            if self.code.virtual:
                vccslot = True

            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.code, OperatorMethod):
            mcslot = True

            if self.code.virtual:
                vccslot = True

            pslot = self._handle_callable_properties
        elif isinstance(self.code, Function):
            mcslot = True
            pslot = self._handle_callable_properties
            dsslot = True
        elif isinstance(self.code, OperatorFunction):
            mcslot = True
            pslot = self._handle_callable_properties
        elif isinstance(self.code, Variable):
            acslot = True
            gcslot = True
            scslot = True
            pslot = self._handle_variable_properties
        elif isinstance(self.code, Enum):
            pslot = self._handle_enum_properties
        elif isinstance(self.code, EnumValue):
            pslot = self._handle_enum_member_properties

        if thcslot or thicslot or tcslot or cttcslot or cftcslot or fcslot or sccslot or mcslot or vccslot or acslot or gcslot or scslot or gctcslot or gcccslot or bigetbslot or birelbslot or birbslot or biwbslot or biscslot or bicbslot or pickslot or xaslot or dsslot:
            menu.append(None)

            if thcslot:
                self._add_directive(menu, '%TypeHeaderCode',
                        self.code.typeheadercode, self._typeheaderCodeSlot,
                        'thc')

            if tcslot:
                self._add_directive(menu, '%TypeCode', self.code.typecode,
                        self._typeCodeSlot, 'tc')

            if thicslot:
                self._add_directive(menu, '%TypeHintCode',
                        self.code.typehintcode, self._typehintCodeSlot, 'thic')

            if fcslot:
                self._add_directive(menu, '%FinalisationCode',
                        self.code.finalisationcode, self._finalCodeSlot, 'fc')

            if sccslot:
                self._add_directive(menu, '%ConvertToSubClassCode',
                        self.code.subclasscode, self._subclassCodeSlot, 'scc')

            if cttcslot:
                self._add_directive(menu, '%ConvertToTypeCode',
                        self.code.convtotypecode, self._convToTypeCodeSlot,
                        'cttc')

            if cftcslot:
                self._add_directive(menu, '%ConvertFromTypeCode',
                        self.code.convfromtypecode, self._convFromTypeCodeSlot,
                        'cftc')

            if mcslot:
                self._add_directive(menu, '%MethodCode', self.code.methcode,
                        self._methodCodeSlot, 'mc')

            if vccslot:
                self._add_directive(menu, '%VirtualCatcherCode',
                        self.code.virtcode, self._virtualCatcherCodeSlot,
                        'vcc')

            if acslot:
                self._add_directive(menu, '%AccessCode', self.code.accesscode,
                        self._accessCodeSlot, 'ac')

            if gcslot:
                self._add_directive(menu, '%GetCode', self.code.getcode,
                        self._getCodeSlot, 'gc')

            if scslot:
                self._add_directive(menu, '%SetCode', self.code.setcode,
                        self._setCodeSlot, 'sc')

            if gctcslot:
                self._add_directive(menu, '%GCTraverseCode',
                        self.code.gctraversecode, self._gcTraverseCodeSlot,
                        'gctc')

            if gcccslot:
                self._add_directive(menu, '%GCClearCode',
                        self.code.gcclearcode, self._gcClearCodeSlot, 'gccc')

            if bigetbslot:
                self._add_directive(menu, '%BIGetBufferCode',
                        self.code.bigetbufcode, self._biGetBufCodeSlot,
                        'bigetb')

            if birelbslot:
                self._add_directive(menu, '%BIReleaseBufferCode',
                        self.code.birelbufcode, self._biRelBufCodeSlot,
                        'birelb')

            if birbslot:
                self._add_directive(menu, '%BIGetReadBufferCode',
                        self.code.bireadbufcode, self._biReadBufCodeSlot,
                        'birb')

            if biwbslot:
                self._add_directive(menu, '%BIGetWriteBufferCode',
                        self.code.biwritebufcode, self._biWriteBufCodeSlot,
                        'biwb')

            if biscslot:
                self._add_directive(menu, '%BIGetSegCountCode',
                        self.code.bisegcountcode, self._biSegCountCodeSlot,
                        'bisc')

            if bicbslot:
                self._add_directive(menu, '%BIGetCharBufferCode',
                        self.code.bicharbufcode, self._biCharBufCodeSlot,
                        'bicb')

            if pickslot:
                self._add_directive(menu, '%PickleCode', self.code.picklecode,
                        self._pickleCodeSlot, 'pick')

            if dsslot:
                self._add_directive(menu, '%Docstring', self.code.docstring,
                        self._docstringSlot, 'ds')

        if isinstance(self.code, (Class, Constructor, Function, Method)):
            menu.append(None)
            menu.append(("Accept all argument names", self._acceptNames))

        # Add the extra menu items.
        menu.append(None)
        menu.append(("Versions...", self._handle_versions,
                len(project.versions) != 0))
        menu.append(
                (self._flagged_text("Platform Tags...", self.code.platforms),
                        self._handle_platforms, len(project.platforms) != 0))
        menu.append(
                (self._flagged_text("Feature Tags...", self.code.features),
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

        self.treeWidget().acceptArgumentNames(self.code)

    def _handle_add_manual_code(self):
        """ Slot to handle the addition of manual code. """

        manual_code = ManualCode()

        dialog = ManualCodeDialog(manual_code, "Add Manual Code",
                self.treeWidget())

        if dialog.update():
            parent_content = self.parent_project_item().content
            parent_content.insert(parent_content.index(self.code) + 1,
                    manual_code)
            self.set_dirty()

    def _handle_modify_manual_code(self):
        """ Slot to handle the update of the manual code. """

        dialog = ManualCodeDialog(self.code, "Modify Manual Code",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()

            self.draw_name()

    def _bodyManualCode(self):
        """
        Slot to handle the update of the manual code body.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._mcBodyDone)
        ed.edit(self.code.body, "Manual Code: " + self.code.precis)
        self._editors["mcb"] = ed

    def _mcBodyDone(self, text_changed, text):
        """
        Slot to handle changed manual code body.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.body = text
            self.set_dirty()

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
            self.set_dirty()

            for target in self._targets:
                self.parent_project_item().content.remove(target.code)

    def _accessCodeSlot(self):
        """
        Slot to handle %AccessCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._accessCodeDone)
        ed.edit(self.code.accesscode, "%AccessCode: " + self.code.user())
        self._editors["ac"] = ed

    def _accessCodeDone(self, text_changed, text):
        """
        Slot to handle changed %AccessCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.accesscode = text
            self.set_dirty()

        del self._editors["ac"]

    def _getCodeSlot(self):
        """
        Slot to handle %GetCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._getCodeDone)
        ed.edit(self.code.getcode, "%GetCode: " + self.code.user())
        self._editors["gc"] = ed

    def _getCodeDone(self, text_changed, text):
        """
        Slot to handle changed %GetCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.getcode = text
            self.set_dirty()

        del self._editors["gc"]

    def _setCodeSlot(self):
        """
        Slot to handle %SetCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._setCodeDone)
        ed.edit(self.code.setcode, "%SetCode: " + self.code.user())
        self._editors["sc"] = ed

    def _setCodeDone(self, text_changed, text):
        """
        Slot to handle changed %SetCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.setcode = text
            self.set_dirty()

        del self._editors["sc"]

    def _typehintCodeSlot(self):
        """
        Slot to handle %TypeHintCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typehintCodeDone)
        ed.edit(self.code.typeheadercode, "%TypeHintCode: " + self.code.user())
        self._editors["thic"] = ed

    def _typehintCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeHintCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.typehintcode = text
            self.set_dirty()

        del self._editors["thic"]

    def _typeheaderCodeSlot(self):
        """
        Slot to handle %TypeHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typeheaderCodeDone)
        ed.edit(self.code.typeheadercode, "%TypeHeaderCode: " + self.code.user())
        self._editors["thc"] = ed

    def _typeheaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.typeheadercode = text
            self.set_dirty()

        del self._editors["thc"]

    def _typeCodeSlot(self):
        """
        Slot to handle %TypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._typeCodeDone)
        ed.edit(self.code.typecode, "%TypeCode: " + self.code.user())
        self._editors["tc"] = ed

    def _typeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %TypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.typecode = text
            self.set_dirty()

        del self._editors["tc"]

    def _convToTypeCodeSlot(self):
        """
        Slot to handle %ConvertToTypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._convToTypeCodeDone)
        ed.edit(self.code.convtotypecode, "%ConvertToTypeCode: " + self.code.user())
        self._editors["cttc"] = ed

    def _convToTypeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertToTypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.convtotypecode = text
            self.set_dirty()

        del self._editors["cttc"]

    def _convFromTypeCodeSlot(self):
        """
        Slot to handle %ConvertFromTypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._convFromTypeCodeDone)
        ed.edit(self.code.convfromtypecode, "%ConvertFromTypeCode: " + self.code.user())
        self._editors["cftc"] = ed

    def _convFromTypeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertFromTypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.convfromtypecode = text
            self.set_dirty()

        del self._editors["cftc"]

    def _gcTraverseCodeSlot(self):
        """
        Slot to handle %GCTraverseCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._gcTraverseCodeDone)
        ed.edit(self.code.gctraversecode, "%GCTraverseCode: " + self.code.user())
        self._editors["gctc"] = ed

    def _gcTraverseCodeDone(self, text_changed, text):
        """
        Slot to handle changed %GCTraverseCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.gctraversecode = text
            self.set_dirty()

        del self._editors["gctc"]

    def _gcClearCodeSlot(self):
        """
        Slot to handle %GCClearCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._gcClearCodeDone)
        ed.edit(self.code.gcclearcode, "%GCClearCode: " + self.code.user())
        self._editors["gccc"] = ed

    def _gcClearCodeDone(self, text_changed, text):
        """
        Slot to handle changed %GCClearCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.gcclearcode = text
            self.set_dirty()

        del self._editors["gccc"]

    def _biGetBufCodeSlot(self):
        """
        Slot to handle %BIGetBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biGetBufCodeDone)
        ed.edit(self.code.bigetbufcode, "%BIGetBufferCode: " + self.code.user())
        self._editors["bigetb"] = ed

    def _biGetBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.bigetbufcode = text
            self.set_dirty()

        del self._editors["bigetb"]

    def _biRelBufCodeSlot(self):
        """
        Slot to handle %BIReleaseBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biRelBufCodeDone)
        ed.edit(self.code.birelbufcode, "%BIReleaseBufferCode: " + self.code.user())
        self._editors["birelb"] = ed

    def _biRelBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIReleaseBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.birelbufcode = text
            self.set_dirty()

        del self._editors["birelb"]

    def _biReadBufCodeSlot(self):
        """
        Slot to handle %BIGetReadBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biReadBufCodeDone)
        ed.edit(self.code.bireadbufcode, "%BIGetReadBufferCode: " + self.code.user())
        self._editors["birb"] = ed

    def _biReadBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetReadBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.bireadbufcode = text
            self.set_dirty()

        del self._editors["birb"]

    def _biWriteBufCodeSlot(self):
        """
        Slot to handle %BIGetWriteBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biWriteBufCodeDone)
        ed.edit(self.code.biwritebufcode, "%BIGetWriteBufferCode: " + self.code.user())
        self._editors["biwb"] = ed

    def _biWriteBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetWriteBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.biwritebufcode = text
            self.set_dirty()

        del self._editors["biwb"]

    def _biSegCountCodeSlot(self):
        """
        Slot to handle %BIGetSegCountCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biSegCountCodeDone)
        ed.edit(self.code.bisegcountcode, "%BIGetSegCountCode: " + self.code.user())
        self._editors["bisc"] = ed

    def _biSegCountCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetSegCountCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.bisegcountcode = text
            self.set_dirty()

        del self._editors["bisc"]

    def _biCharBufCodeSlot(self):
        """
        Slot to handle %BIGetCharBufferCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._biCharBufCodeDone)
        ed.edit(self.code.bicharbufcode, "%BIGetCharBufferCode: " + self.code.user())
        self._editors["bicb"] = ed

    def _biCharBufCodeDone(self, text_changed, text):
        """
        Slot to handle changed %BIGetCharBufferCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.bicharbufcode = text
            self.set_dirty()

        del self._editors["bicb"]

    def _pickleCodeSlot(self):
        """
        Slot to handle %PickleCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._pickleCodeDone)
        ed.edit(self.code.picklecode, "%PickleCode: " + self.code.user())
        self._editors["pick"] = ed

    def _pickleCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PickleCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.picklecode = text
            self.set_dirty()

        del self._editors["pick"]

    def _finalCodeSlot(self):
        """
        Slot to handle %FinalisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._finalCodeDone)
        ed.edit(self.code.finalisationcode, "%FinalisationCode: " + self.code.user())
        self._editors["fc"] = ed

    def _finalCodeDone(self, text_changed, text):
        """
        Slot to handle changed %FinalisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.finalisationcode = text
            self.set_dirty()

        del self._editors["fc"]

    def _subclassCodeSlot(self):
        """
        Slot to handle %ConvertToSubClassCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._subclassCodeDone)
        ed.edit(self.code.subclasscode, "%ConvertToSubClassCode: " + self.code.user())
        self._editors["scc"] = ed

    def _subclassCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertToSubClassCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.subclasscode = text
            self.set_dirty()

        del self._editors["scc"]

    def _docstringSlot(self):
        """
        Slot to handle %Docstring.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._docstringDone)
        ed.edit(self.code.docstring, "%Docstring: " + self.code.user())
        self._editors["ds"] = ed

    def _docstringDone(self, text_changed, text):
        """
        Slot to handle changed %Docstring.

        text_changed is set if the code has changed.
        text is the changed docstring.
        """
        if text_changed:
            self.code.docstring = text
            self.set_dirty()

        del self._editors["ds"]

    def _methodCodeSlot(self):
        """
        Slot to handle %MethodCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._methodCodeDone)
        ed.edit(self.code.methcode, "%MethodCode: " + self.code.user())
        self._editors["mc"] = ed

    def _methodCodeDone(self, text_changed, text):
        """
        Slot to handle changed %MethodCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.methcode = text
            self.set_dirty()

        del self._editors["mc"]

    def _virtualCatcherCodeSlot(self):
        """
        Slot to handle %VirtualCatcherCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._virtualCatcherCodeDone)
        ed.edit(self.code.virtcode, "%VirtualCatcherCode: " + self.code.user())
        self._editors["vcc"] = ed

    def _virtualCatcherCodeDone(self, text_changed, text):
        """
        Slot to handle changed %VirtualCatcherCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.virtcode = text
            self.set_dirty()

        del self._editors["vcc"]

    def _handle_versions(self):
        """ Slot to handle the versions. """

        dialog = VersionsDialog(self.code, "Versions", self.treeWidget(),
                project=self.treeWidget().project)

        if dialog.update():
            # Apply the version range to all targets.
            for itm in self._targets:
                if itm.code is not self.code:
                    itm.code.versions = list(self.code.versions)

            self.set_dirty()

    def _handle_platforms(self):
        """ Slot to handle the platforms. """

        dialog = PlatformsDialog(self.code, "Platform Tags", self.treeWidget(),
                project=self.treeWidget().project)

        if dialog.update():
            self.set_dirty()

    def _handle_features(self):
        """ Slot to handle the features. """

        dialog = FeaturesDialog(self.code, "Feature Tags", self.treeWidget(),
                project=self.treeWidget().project)

        if dialog.update():
            self.set_dirty()

    def _handle_namespace_properties(self):
        """ Slot to handle the properties for namespaces. """

        dialog = NamespacePropertiesDialog(self.code, "Namespace Properties",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

    def _handle_opaque_class_properties(self):
        """ Slot to handle the properties for opaque classes. """

        dialog = OpaqueClassPropertiesDialog(self.code,
                "Opaque Class Properties", self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

    def _handle_class_properties(self):
        """ Slot to handle the properties for classes. """

        dialog = ClassPropertiesDialog(self.code, "Class Properties",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

    def _handle_callable_properties(self):
        """ Slot to handle the properties for callables. """

        dialog = CallablePropertiesDialog(self.code, 'Placeholder',
                self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

    def _handle_variable_properties(self):
        """ Slot to handle the properties for variables. """

        dialog = VariablePropertiesDialog(self.code, "Variable Properties",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

    def _handle_enum_properties(self):
        """ Slot to handle the properties for enums. """

        dialog = EnumPropertiesDialog(self.code, "Enum Properties",
                self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

    def _handle_enum_member_properties(self):
        """ Slot to handle the properties for enum members. """

        dialog = EnumMemberPropertiesDialog(self.code,
                "Enum Member Properties", self.treeWidget())

        if dialog.update():
            self.set_dirty()
            self.setText(ApiEditor.NAME, self.code.user())

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
            if itm.code.status != new:
                itm.code.status = new
                self.set_dirty()

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
            if itm.code.access != new:
                itm.code.access = new
                self.set_dirty()

                # FIXME: Observe the access attribute.
                itm._draw_access()
