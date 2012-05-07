# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import sys
import os

from PyQt4.QtCore import pyqtSignal, QByteArray, QMimeData, Qt
from PyQt4.QtGui import (QApplication, QDialog, QDrag, QFileDialog,
        QInputDialog, QMenu, QMessageBox, QProgressDialog, QTreeWidget,
        QTreeWidgetItem, QTreeWidgetItemIterator, QVBoxLayout)

from dip.shell import IDirty

from ..Project import (Class, Constructor, Destructor, Method, Function,
        Variable, Enum, EnumValue, OperatorFunction, Access, OperatorMethod,
        ManualCode, OpaqueClass, OperatorCast, Namespace, HeaderDirectory)
from ..GccXML import GccXMLParser as CppParser

from .ExternalEditor import ExternalEditor
from .ArgProperties import ArgPropertiesDialog
from .CallableProperties import CallablePropertiesDialog
from .ClassProperties import ClassPropertiesDialog
from .OpaqueClassProperties import OpaqueClassPropertiesDialog
from .VariableProperties import VariablePropertiesDialog
from .EnumProperties import EnumPropertiesDialog
from .EnumValueProperties import EnumValuePropertiesDialog
from .HeaderDirectoryProperties import HeaderDirectoryPropertiesDialog
from .ModuleProperties import ModulePropertiesDialog
from .ProjectProperties import ProjectPropertiesDialog
from .PlatformPicker import PlatformPickerDialog
from .FeaturePicker import FeaturePickerDialog
from .ManualCode import ManualCodeDialog
from .Generations import GenerationsDialog


class NavigationPane(QTreeWidget):
    """ This class represents a navigation pane in the GUI. """

    MIME_FORMAT = 'application/x-item'

    headerDirectoryScanned = pyqtSignal(HeaderDirectory)

    def __init__(self, gui, parent=None):
        """
        Initialise the navigation pane instance.

        gui is the GUI instance.
        parent is the optional parent widget.
        """
        super().__init__(parent)

        # Tweak the tree widget.
        self.setHeaderLabels(["Name", "Access", "Status", "Versions"])
        self.setSelectionMode(self.ExtendedSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.InternalMove)

        self.gui = gui
        self.dragged = None

        # Create the (initially empty) project item.
        self._navroot = _ProjectItem(self)

    def set_dirty(self):
        """ Mark the project as having been modified. """

        IDirty(self.gui.project).dirty = True

    def loadGUILayout(self, settings):
        """
        Load the GUI layout from the user settings.

        settings is the user settings.
        """
        colws = settings.value('widths')
        colw = [int(w) for w in colws.split()]

        # Allow for a different number of columns (in case any get added or
        # removed during development).
        nr_cols = min(len(colw), self.columnCount())

        for c in range(nr_cols):
            self.setColumnWidth(c, colw[c])

    def saveGUILayout(self, settings):
        """
        Save the GUI layout to the user settings.

        settings is the user settings.
        """
        colws = [str(self.columnWidth(c)) for c in range(self.columnCount())]
        settings.setValue('widths', ' '.join(colws))

    def draw(self):
        """ Draw the current project. """

        # Progress will be reported against known header files (plus one for
        # the unknown and ignored header files) so count them all.
        nr_steps = 1
        for module in self.gui.project.modules:
            nr_steps += len(module.content)

        # Display the progress dialog.
        progress = QProgressDialog( "Processing...", None, 0, nr_steps)
        progress.setWindowTitle(self.gui.project.name)
        progress.setValue(0)

        self._navroot.draw(progress)

    def refreshProjectName(self):
        """
        Draw the current project name.
        """
        self._navroot.refreshProjectName()

    def clearProject(self):
        """
        Clear a navigation pane so it is ready for a new project.
        """
        self._navroot.clearProject()

    def contextMenuEvent(self, ev):
        """
        Reimplemented to handle a context menu event.

        ev is the event.
        """
        # Find the item.
        itm = self.itemAt(ev.pos())

        if itm:
            # Get the list of siblings that are also selected.
            slist = []

            parent = itm.parent()
            if parent is not None:
                for sib_idx in range(parent.childCount()):
                    sib = parent.child(sib_idx)

                    if sib is not itm and sib.isSelected() and not sib.isHidden():
                        slist.append(sib)

            # Check it has a menu.
            opts = itm.getMenu(slist)

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

                menu.exec_(ev.globalPos())

                ev.accept()
                return

        super(NavigationPane, self).contextMenuEvent(ev)

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
        data = QByteArray(str(id(dragging)))
        mime = QMimeData()
        mime.setData(self.MIME_FORMAT, data)

        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec_()

    def dragEnterEvent(self, ev):
        """
        Reimplemented to validate a drag enter.
        """
        if self._source_target(ev) is None:
            ev.ignore()
        else:
            ev.accept()

    def dragMoveEvent(self, ev):
        """
        Reimplemented to validate a drag move.
        """
        if self._source_target(ev) is None:
            ev.ignore()
        else:
            ev.setDropAction(Qt.MoveAction)
            ev.accept()

    def dropEvent(self, ev):
        """
        Reimplemented to handle a drop.
        """
        source_target = self._source_target(ev)

        if source_target is None:
            ev.ignore()
        else:
            source, target = source_target
            if source is target:
                ev.ignore()
            else:
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
            if id(itm) == source_id:
                source = itm
                break

            it+=1
            itm = it.value()

        if source is None:
            return None

        # If the source is the target (ie. we are at the start of the drag)
        # say that the drop is Ok, otherwise other drag events might not be
        # generated.  We will properly check later when the drop is done.
        if source is target:
            return source, target

        # Ask the target if it can handle the source.
        if not (isinstance(target, _DropSite) and target.droppable(source)):
            return None

        return source, target

    def acceptArgumentNames(self, prj_item):
        """
        Mark the arguments of all callables contained in a part of a project
        as being named.

        prj_item is the part of the project.
        """
        updated_args = self.gui.project.acceptArgumentNames(prj_item)
        self._updateArgs(updated_args)

        if len(updated_args) != 0:
            self.set_dirty()

    def nameArgumentsFromConventions(self, prj_item):
        """
        Name the arguments of all callables contained in a part of the project
        according to the conventions.

        prj_item is the part of the project.
        """
        btn = QMessageBox.question(self, "Naming Conventions",
                "Do you want to apply the naming conventions arguments rather "
                "than just see what would be changed?",
                QMessageBox.Yes, QMessageBox.No|QMessageBox.Default,
                QMessageBox.Cancel)

        if btn == QMessageBox.Cancel:
            return

        invalid, updated_args = self.gui.project.nameArgumentsFromConventions(
                prj_item, update=(btn == QMessageBox.Yes))

        self._updateArgs(updated_args)

        if len(updated_args) != 0:
            self.set_dirty()

        if len(invalid) > 0:
            self._stringDialog("Callables with Invalid Arguments", invalid)

    def updateArgumentsFromWebXML(self, module):
        """
        Update any unnamed arguments of all callables contained in a module
        from WebXML.

        module is the module.
        """
        undocumented, updated_args = self.gui.project.updateArgumentsFromWebXML(
                self.gui, module)

        # Update the affected names.
        for arg in updated_args:
            arg._gui.drawName()

        # Show any undocumented callables.
        if len(undocumented) > 0:
            self._stringDialog("Undocumented Callables", undocumented)

    @staticmethod
    def _updateArgs(updated_args):
        """
        Update the GUI for those arguments that have been updated.

        updated_args is the list of updated Argument instances.
        """
        callables = []
        for arg in updated_args:
            arg._gui.drawName()

            callable = arg._gui.parent()
            if callable not in callables:
                callables.append(callable)

        for callable in callables:
            callable.drawName()
            callable.drawStatus()

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


class _DropSite(object):
    """
    This mixin class implements a drop site.  Any derived class must also
    derive QTreeWidgetItem.
    """
    def __init__(self):
        """
        Initialise the instance.
        """
        self.setFlags(self.flags() | Qt.ItemIsDropEnabled)

    def droppable(self, source):
        """
        Determine if an item can be dropped.

        source is the QTreeWidgetItem sub-class instance being dropped.
        """
        raise NotImplementedError

    def drop(self, source):
        """
        Handle the drop of an item.

        source is the QTreeWidgetItem sub-class instance being dropped.
        """
        raise NotImplementedError


class _SimpleItem(QTreeWidgetItem):
    """
    This class represents a simple item (ie. no context menu) in the navigation
    pane.
    """
    def __init__(self, parent, after=None):
        """
        Initialise the item instance.

        parent is the parent.
        after is the sibling after which this should be placed.  If it is None
        then it should be placed at the end.  If it is the parent then it
        should be placed at the start.
        """
        if after is parent:
            super(_SimpleItem, self).__init__(parent, None)
        elif after is None:
            super(_SimpleItem, self).__init__(parent)
        else:
            super(_SimpleItem, self).__init__(parent, after)

        self.pane = self.treeWidget()
        self.drawAll()

    def set_dirty(self):
        """ Mark the project as having been modified. """

        self.pane.set_dirty()

    def drawAll(self):
        """ Draw all columns of the item. """

        self.drawName()
        self.drawAccess()
        self.drawStatus()
        self.drawGenerations()

    def drawName(self):
        """ Draw the name column of the item. """

        n = self.getName()

        if n:
            self.setText(0, n)

    def getName(self):
        """ Return the value of the name of the item. """

        raise NotImplementedError

    def drawAccess(self):
        """ Draw the access column of the item. """

        a = self.getAccess()

        if a is not None:
            self.setText(1, a)

    def getAccess(self):
        """ Return the value of the access of the item. """

        return None

    def drawStatus(self):
        """ Draw the status column of the item. """

        s = self.getStatus()

        if s is not None:
            self.setText(2, s)

    def getStatus(self):
        """ Return the value of the status of the item. """

        return None

    def drawGenerations(self):
        """ Draw the generations column of the item. """

        g = self.getGenerations()

        if g:
            (sgen, egen) = g
            self.setText(3, self.pane.gui.project.versionRange(sgen, egen))

    def getGenerations(self):
        """ Return the value of the generations of the item. """

        return None

    def getMenu(self, slist):
        """
        Return the list of context menu options or None if the item doesn't
        have a context menu.  Each element is a tuple of the text of the
        option, the bound method that handles the option, and a flag that is
        True if the option should be enabled.

        slist is a list of siblings of the item that is also selected.
        """
        return None


class _FixedItem(_SimpleItem):
    """
    This class is a base class for items that implement fixed parts of a
    project's structure.
    """
    def __init__(self, parent, after=None):
        """
        Initialise the item instance.

        parent is the parent.
        after is the sibling after which this should be placed.  If it is None
        then it should be placed at the end.  If it is the parent then it
        should be placed at the start.
        """
        super(_FixedItem, self).__init__(parent, after)

        self.setFlags(Qt.ItemIsEnabled)


class _ProjectItem(_FixedItem):
    """ This class implements a navigation item that represents a project. """

    def __init__(self, parent):
        """
        Initialise the item instance.

        parent is the parent.
        """
        self._prjname = ""

        super(_ProjectItem, self).__init__(parent)

        self._mods = _ModuleGroupItem(self, "Modules")
        self._hdrs = _HeaderDirectoryGroupItem(self, "Header Directories")

        self._mods.setExpanded(True)
        self._hdrs.setExpanded(True)
        self.setExpanded(True)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self._prjname

    def refreshProjectName(self):
        """
        Return the value of the name column.
        """
        self._prjname = self.pane.gui.project.descriptiveName()
        self.drawName()

    def draw(self, progress):
        """ Draw the current project.

        :param progress:
            is the progress dialog to update.
        """

        self.refreshProjectName()

        so_far = self._mods.draw(progress)
        self._hdrs.draw()
        so_far += 1

        # This will terminate the progress dialog.
        progress.setValue(so_far)

    def clearProject(self):
        """
        Clear the item ready for another project.
        """
        self._mods.takeChildren()
        self._hdrs.takeChildren()

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        if slist:
            return None

        return [("Baseline Version...", self._baselineSlot),
                ("Add Platform Tag...", self._platformSlot),
                ("Add Feature Tag...", self._featureSlot),
                ("Add External Module...", self._externalmoduleSlot),
                ("Add Ignored Namespace...", self._ignorednamespaceSlot),
                ("Properties...", self._propertiesSlot)]


    def _baselineSlot(self):
        """
        Handle baselining a version.
        """
        # Get the name of the new version.
        (vers, ok) = QInputDialog.getText(self.pane, "Baseline Version",
                "Version name")

        if ok:
            vers = str(vers).strip()

            # TODO - check the version is valid (eg. no embedded spaces) and
            # not already in use.
            if vers:
                # Add the version to the project
                self.pane.gui.project.addVersion(vers)

    def _platformSlot(self):
        """
        Handle adding a new platform tag.
        """
        # Get the name of the new platform.
        (plat, ok) = QInputDialog.getText(self.pane, "Platform Tag",
                "Platform tag")

        if ok:
            plat = str(plat).strip()

            # TODO - check the platform is valid (eg. no embedded spaces) and
            # not already in use.
            if plat:
                # Add the platform to the project
                self.pane.gui.project.addPlatform(plat)

    def _featureSlot(self):
        """
        Handle adding a new feature tag.
        """
        # Get the name of the new feature.
        (feat, ok) = QInputDialog.getText(self.pane, "Feature Tag",
                "Feature tag")

        if ok:
            feat = str(feat).strip()

            # TODO - check the feature is valid (eg. no embedded spaces) and
            # not already in use.
            if feat:
                # Add the feature to the project
                self.pane.gui.project.addFeature(feat)

    def _externalmoduleSlot(self):
        """
        Handle adding a new external module.
        """
        # Get the name of the new external module.
        (xm, ok) = QInputDialog.getText(self.pane, "External Module",
                "External Module")

        if ok:
            xm = str(xm).strip()

            # TODO - check the module is valid (eg. no embedded spaces) and not
            # already in use.
            if xm:
                # Add the external module to the project
                self.pane.gui.project.addExternalModule(xm)

    def _ignorednamespaceSlot(self):
        """
        Handle adding a new ignored namespace.
        """
        # Get the name of the new ignored namespace.
        (ns, ok) = QInputDialog.getText(self.pane, "Ignored Namespace",
                "Ignored Namespace")

        if ok:
            ns = str(ns).strip()

            if ns:
                # Add the ignored namespace to the project
                self.pane.gui.project.addIgnoredNamespace(ns)

    def _propertiesSlot(self):
        """
        Handle the project's properties.
        """
        prj = self.pane.gui.project
        dlg = ProjectPropertiesDialog(prj, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            version = prj.workingversion

            (prj.rootmodule, version.inputdir, version.webxmldir, prj.platforms, prj.features, prj.externalfeatures, prj.externalmodules, prj.ignorednamespaces, prj.sipcomments) = dlg.fields()

            self.set_dirty()


class _ModuleGroupItem(_FixedItem):
    """
    This class implements a navigation item that represents a module group.
    """
    def __init__(self, parent, text):
        """
        Initialise the item instance.

        parent is the parent.
        text is the text to use.
        """
        self._text = text

        _FixedItem.__init__(self, parent)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self._text

    def draw(self, progress):
        """ Draw the current project.

        :param progress:
            is the progress dialog to update.
        :return:
            the updated count of processed items.
        """

        so_far = 0

        for mod in self.pane.gui.project.modules:
            _ModuleItem(self, mod, progress, so_far)
            so_far += len(mod.content)

        return so_far

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        if slist:
            return None

        return [("Add Module...", self._addModuleSlot)]

    def _addModuleSlot(self):
        """
        Handle adding a module to the project.
        """
        # Get the name of the module.
        (mname, ok) = QInputDialog.getText(self.pane, "Add Module",
                "Module name")

        if ok:
            mname = str(mname).strip()

            # TODO - check the name is valid (eg. no embedded spaces) and not
            # already in use.
            if mname:
                # Add the module to the project and the GUI.
                mod = self.pane.gui.project.newModule(mname)
                _ModuleItem(self, mod)


class _ModuleItem(_FixedItem, _DropSite):
    """
    This class implements a navigation item that represents a module.
    """
    def __init__(self, parent, mod, progress=None, so_far=0):
        """ Initialise the item instance.

        :param parent:
            is the parent.
        :param mod:
            is the module instance.
        :param progress:
            is the optional progress dialog to update.
        :param so_far:
            is the optional count of items processed so far.
        """
        self.module = mod

        _FixedItem.__init__(self, parent)
        _DropSite.__init__(self)

        self._drawHeaders(progress, so_far)

        self.pane.headerDirectoryScanned.connect(self._refresh)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self.module.name

    def _refresh(self, hdir):
        """
        Draw the parts of the project affected by a change in header files.

        hdir is the header directory instance to refresh.
        """
        # See if we have any header files in the directory.
        for idx in range(self.childCount()):
            if self.child(idx).headerfile in hdir:
                # We remove everything - it's easier.
                self.takeChildren()
                self._drawHeaders()

                break

    def _drawHeaders(self, progress=None, so_far=0):
        """
        Draw the header files group for the module.
        """
        for hf in self.module.content:
            _ModuleHeaderFileItem(self, hf)

            if progress is not None:
                so_far += 1
                progress.setValue(so_far)
                QApplication.processEvents()

    def droppable(self, source):
        """
        Determine if an item can be dropped.
        """
        # Any header file can be dropped here.
        return isinstance(source, _HeaderFileItem)

    def drop(self, source, after=None):
        """
        Handle the item being dropped here.

        source is the item being dropped.
        after is the optional child on which the item was actually dropped.
        """
        # Remove the item from its old parent (either a _HeaderFileGroupItem or
        # a _ModuleItem).
        source.parent().removeHeaderFileItem(source)

        # Create a new item and add it to this one.
        if after is None:
            at = 0
            after = self
        else:
            at = self.module.index(after.headerfile) + 1

        hf = source.headerfile

        hf.status = ''
        self.module.insert(at, hf)

        _ModuleHeaderFileItem(self, hf, after)

        self.set_dirty()

    def removeHeaderFileItem(self, itm):
        """
        Remove a header file item.

        itm is the item to remove.
        """
        self.module.remove(itm.headerfile)
        self.removeChild(itm)

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        if slist:
            return None

        # See if any need updating.
        update = False
        for idx in range(self.childCount()):
            if self.child(idx).headerfile.parse == 'needed':
                update = True
                break

        return [("Parse Updated Headers...", self._parseUpdatedHeadersSlot, update),
                ("Update argument names from WebXML", self._updateFromWebXML),
                ("Properties...", self._propertiesSlot)]

    def _updateFromWebXML(self):
        """ Update argument names from WebXML to all unnamed arguments. """

        self.pane.updateArgumentsFromWebXML(self.module)

    def _propertiesSlot(self):
        """ Handle the module's properties. """

        mod = self.module
        dlg = ModulePropertiesDialog(self.pane.gui.project, mod, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (mod.outputdirsuffix, mod.imports, mod.directives, mod.version) = dlg.fields()

            self.set_dirty()

    def _parseUpdatedHeadersSlot(self):
        """
        Handle parsing any updated headers.
        """
        for idx in range(self.childCount()):
            itm = self.child(idx)

            if itm.headerfile.parse == "needed":
                if not itm.parseHeaderFile():
                    return


class _HeaderDirectoryGroupItem(_FixedItem):
    """
    This class implements a navigation item that represents a header directory
    group.
    """
    def __init__(self, parent, text):
        """
        Initialise the item instance.

        parent is the parent.
        text is the text to use.
        """
        self._text = text

        _FixedItem.__init__(self, parent)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self._text

    def draw(self):
        """ Draw the current project. """

        for hdir in self.pane.gui.project.headers:
            _HeaderDirectoryItem(self, hdir).draw()

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        if slist:
            return None

        return [("Add Header Directory...", self._addHeaderDirectorySlot)]

    def _addHeaderDirectorySlot(self):
        """
        Handle adding a header file directory to the project.
        """
        # Get the name of the header directory.
        (hname, ok) = QInputDialog.getText(self.pane, "Add Header directory",
                "Descriptive name")

        if ok:
            hname = str(hname).strip()

            # TODO - check the name is not already in use.
            if hname:
                # Add the header directory to the project and the GUI.
                hdir = self.pane.gui.project.newHeaderDirectory(hname)
                _HeaderDirectoryItem(self, hdir)


class _HeaderDirectoryItem(_FixedItem):
    """
    This class implements a navigation item that represents a header file
    directory.
    """
    def __init__(self, parent, hdir):
        """
        Initialise the item instance.

        parent is the parent.
        hdir is the header directory instance.
        """
        self._hdir = hdir

        _FixedItem.__init__(self, parent)

        self._unknown = _HeaderFileGroupItem(self, hdir, "unknown", "Unknown")
        self._ignored = _HeaderFileGroupItem(self, hdir, "ignored", "Ignored")

        # Open the unknown branch if it contains anything.
        for hf in hdir.content:
            if hf.status == "unknown":
                self._unknown.setExpanded(True)
                self.setExpanded(True)
                break

        self.pane.headerDirectoryScanned.connect(self._refresh)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self._hdir.name

    def draw(self):
        """
        Draw the current project.
        """
        sortunknown = False
        sortignored = False

        for hf in self._hdir.content:
            if hf.status == "unknown":
                _HeaderFileItem(self._unknown, hf)
                sortunknown = True
            elif hf.status == "ignored":
                _HeaderFileItem(self._ignored, hf)
                sortignored = True

        if sortunknown:
            self._unknown.sortChildren(0, Qt.AscendingOrder)
            self._unknown.setExpanded(True)
            self.setExpanded(True)

        if sortignored:
            self._ignored.sortChildren(0, Qt.AscendingOrder)

    def _refresh(self, hdir):
        """
        Draw the parts of the project affected by a change in header files.

        hdir is the header directory instance to refresh.
        """
        if hdir is self._hdir:
            self._unknown.takeChildren()
            self._ignored.takeChildren()
            self.draw()

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        if slist:
            return None

        # Only enable the scan if the main project directory has been set.
        scan = (self.pane.gui.project.workingversion.inputdir != "")

        return [("Scan Header Directory", self._scanHeaderDirectorySlot, scan),
                ("Properties...", self._propertiesSlot)]

    def _scanHeaderDirectorySlot(self):
        """
        Handle scanning the header directory.
        """
        sd = os.path.join(
                os.path.expanduser(
                        self.pane.gui.project.workingversion.inputdir),
                self._hdir.inputdirsuffix)

        self._hdir.scan(sd)
        self.pane.headerDirectoryScanned.emit(self._hdir)

    def _propertiesSlot(self):
        """
        Handle the header directory's properties.
        """
        hdir = self._hdir
        dlg = HeaderDirectoryPropertiesDialog(hdir, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (hdir.inputdirsuffix, hdir.filefilter, hdir.parserargs) = dlg.fields()

            self.set_dirty()


class _HeaderFileGroupItem(_FixedItem, _DropSite):
    """
    This class implements a navigation item that represents a header file
    group.
    """
    def __init__(self, parent, hdir, status, text):
        """
        Initialise the item instance.

        parent is the parent.
        hdir is the header directory.
        status is the header file status being applied.
        text is the item text.
        """
        self._text = text

        _FixedItem.__init__(self, parent)
        _DropSite.__init__(self)

        self._hdir = hdir
        self._status = status

    def getName(self):
        """
        Return the value of the name column.
        """
        return self._text

    def droppable(self, source):
        """
        Determine if an item can be dropped here.
        """
        if not isinstance(source, _HeaderFileItem):
            return False

        hf = source.headerfile

        # The header file must be part of the header directory.
        if hf not in self._hdir:
            return False

        # A header file cannot be moved within the same group.
        if hf.status == self._status:
            return False

        return True

    def drop(self, source):
        """
        Handle the item being dropped here.
        """
        hf = source.headerfile

        source.parent().removeHeaderFileItem(source)

        hf.status = self._status

        _HeaderFileItem(self, hf)
        self.sortChildren(0, Qt.AscendingOrder)

        self.set_dirty()

    def removeHeaderFileItem(self, itm):
        """
        Remove a header file item.

        itm is the item to remove.
        """
        self.removeChild(itm)


class _HeaderFileItem(_SimpleItem):
    """
    This class implements a navigation item that represents a header file.
    """
    def __init__(self, parent, hf, after=None):
        """
        Initialise the item instance.

        parent is the parent.
        hf is the header file instance.
        after is the sibling after which this should be placed.  If it is None
        then it should be placed at the end.  If it is the parent then it
        should be placed at the start.
        droptypes is the list of types of item that can be dropped.
        """
        self.headerfile = hf

        super(_HeaderFileItem, self).__init__(parent, after)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self.headerfile.name


class _ModuleHeaderFileItem(_HeaderFileItem, _DropSite):
    """
    This class implements a navigation item that represents a header file in a
    particular module.
    """
    def __init__(self, parent, hf, after=None):
        """
        Initialise the item instance.

        parent is the parent.
        hf is the header file instance.
        after is the sibling after which this should be placed.  If it is None
        then it should be placed at the end.  If it is the parent then it
        should be placed at the start.
        """
        _HeaderFileItem.__init__(self, parent, hf, after)
        _DropSite.__init__(self)

        self._targets = []
        self._editors = {}

        self._draw()

        if hf.parse or self.isExpanded():
            parent.setExpanded(True)

    def getGenerations(self):
        """
        Return the value of the generations column.
        """
        return (self.headerfile.sgen, self.headerfile.egen)

    def getStatus(self):
        """
        Return the value of the status column.
        """
        if self.headerfile.parse == "needed":
            text = "Needs parsing"
        else:
            text = ""

        return text

    def _draw(self):
        """
        Draw the current project.
        """
        for cd in self.headerfile.content:
            _CodeItem(self, cd)

        self.drawStatus()

    def droppable(self, source):
        """
        Determine if an item can be dropped here.
        """
        # Header files are handled by the parent.
        if isinstance(source, _HeaderFileItem):
            return self.parent().droppable(source)

        if not isinstance(source, _CodeItem):
            return False

        # We can only move code around its siblings.
        return (source.parent() is self)

    def drop(self, source, after=None):
        """
        Handle the item being dropped here.

        source is the item being dropped.
        after is the optional child on which the item was dropped.
        """
        # Header files are handled by the parent.
        if isinstance(source, _HeaderFileItem):
            self.parent().drop(source, self)
            return

        # Handle the move of child code.
        cd = source.code
        hf = self.headerfile

        hf.remove(cd)
        self.removeChild(source)

        if after is None:
            at = 0
        else:
            at = hf.index(after.code) + 1

        hf.insert(at, cd)
        self.insertChild(at, source)

        self.set_dirty()

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        # Save the list of targets for the menu action, including this one.
        self._targets = slist[:]
        self._targets.append(self)

        versions = ("Versions...", self._generationsSlot,
                len(self.pane.gui.project.versions) != 0)

        if slist:
            return [versions]

        return [("Parse Header...", self.parseHeaderFile),
                None,
                ("Hide Ignored", self._hideIgnoredSlot),
                ("Show Ignored", self._showIgnoredSlot),
                None,
                ("Add manual code...", self._addManualCode),
                None,
                ("%ExportedHeaderCode", self._exportedHeaderCodeSlot, ("ehc" not in self._editors)),
                ("%ModuleHeaderCode", self._moduleHeaderCodeSlot, ("mhc" not in self._editors)),
                ("%ModuleCode", self._moduleCodeSlot, ("moc" not in self._editors)),
                ("%PreInitialisationCode", self._preInitCodeSlot, ("pric" not in self._editors)),
                ("%InitialisationCode", self._initCodeSlot, ("ic" not in self._editors)),
                ("%PostInitialisationCode", self._postInitCodeSlot, ("poic" not in self._editors)),
                None,
                ("Apply argument naming conventions...", self._nameFromConventions),
                ("Accept argument names", self._acceptNames),
                None,
                versions]

    def _generationsSlot(self):
        """
        Slot to handle the generations.
        """
        dlg = GenerationsDialog(self.pane.gui.project, self.headerfile.sgen, self.headerfile.egen, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (sgen, egen) = dlg.fields()

            for itm in self._targets:
                itm.headerfile.sgen = sgen
                itm.headerfile.egen = egen

                itm.drawGenerations()

            self.set_dirty()

    def _nameFromConventions(self):
        """ Apply the argument naming conventions to all unnamed arguments. """

        self.pane.nameArgumentsFromConventions(self.headerfile)

    def _acceptNames(self):
        """ Accept all argument names. """

        self.pane.acceptArgumentNames(self.headerfile)

    def _addManualCode(self):
        """
        Slot to handle the creation of manual code.
        """
        dlg = ManualCodeDialog("", self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (precis, ) = dlg.fields()

            if precis:
                mc = ManualCode(precis=precis)

                self.headerfile.insert(0, mc)

                _CodeItem(self, mc, self)

                self.set_dirty()

    def _exportedHeaderCodeSlot(self):
        """
        Slot to handle %ExportedHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._exportedHeaderCodeDone)
        ed.edit(self.headerfile.exportedheadercode, "%ExportedHeaderCode: " + self.getName())
        self._editors["ehc"] = ed

    def _exportedHeaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ExportedHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.headerfile.exportedheadercode = text
            self.set_dirty()

        del self._editors["ehc"]

    def _moduleHeaderCodeSlot(self):
        """
        Slot to handle %ModuleHeaderCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._moduleHeaderCodeDone)
        ed.edit(self.headerfile.moduleheadercode, "%ModuleHeaderCode: " + self.getName())
        self._editors["mhc"] = ed

    def _moduleHeaderCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ModuleHeaderCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.headerfile.moduleheadercode = text
            self.set_dirty()

        del self._editors["mhc"]

    def _moduleCodeSlot(self):
        """
        Slot to handle %ModuleCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._moduleCodeDone)
        ed.edit(self.headerfile.modulecode, "%ModuleCode: " + self.getName())
        self._editors["moc"] = ed

    def _moduleCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ModuleCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.headerfile.modulecode = text
            self.set_dirty()

        del self._editors["moc"]

    def _preInitCodeSlot(self):
        """
        Slot to handle %PreInitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._preInitCodeDone)
        ed.edit(self.headerfile.preinitcode, "%PreInitialisationCode: " + self.getName())
        self._editors["pric"] = ed

    def _preInitCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PreInitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.headerfile.preinitcode = text
            self.set_dirty()

        del self._editors["pric"]

    def _initCodeSlot(self):
        """
        Slot to handle %InitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._initCodeDone)
        ed.edit(self.headerfile.initcode, "%InitialisationCode: " + self.getName())
        self._editors["ic"] = ed

    def _initCodeDone(self, text_changed, text):
        """
        Slot to handle changed %InitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.headerfile.initcode = text
            self.set_dirty()

        del self._editors["ic"]

    def _postInitCodeSlot(self):
        """
        Slot to handle %PostInitialisationCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._postInitCodeDone)
        ed.edit(self.headerfile.postinitcode, "%PostInitialisationCode: " + self.getName())
        self._editors["poic"] = ed

    def _postInitCodeDone(self, text_changed, text):
        """
        Slot to handle changed %PostInitialisationCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.headerfile.postinitcode = text
            self.set_dirty()

        del self._editors["poic"]

    def parseHeaderFile(self):
        """
        Parse a header file and add it to the project.  Return True if there
        was no error.
        """
        gui = self.pane.gui
        hdir = gui.project.findHeaderDirectory(self.headerfile)

        parser = CppParser()

        phf = parser.parse(gui.project, hdir, self.headerfile)

        if phf is None:
            QMessageBox.critical(self.pane, "Parse Header File",
                                 parser.diagnostic,
                                 QMessageBox.Ok|QMessageBox.Default,
                                 QMessageBox.NoButton)

            return False

        hdir.addParsedHeaderFile(self.headerfile, phf)

        # Update the display.
        self.takeChildren()
        self._draw()

        return True

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
            if isinstance(itm, _CodeItem) and itm.code.status == "ignored":
                itm.setHidden(not visible)

            it += 1
            itm = it.value()


class _Argument(_FixedItem):
    """
    This class implements a function argument.
    """
    def __init__(self, parent, arg):
        """
        Initialise the item instance.

        parent is the parent.
        arg is the argument instance.
        """
        self.arg = arg

        # Stash this so that an argument can re-draw itself.
        arg._gui = self

        _FixedItem.__init__(self, parent)

    def getName(self):
        """
        Return the value of the name column.
        """
        return self.arg.user(self.parent().code)

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        if slist:
            return None

        return [("Properties...", self._propertiesSlot)]

    def _propertiesSlot(self):
        """
        Slot to handle the argument's properties.
        """
        arg = self.arg
        dlg = ArgPropertiesDialog(arg, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (arg.name, arg.unnamed, arg.pytype, arg.annos) = dlg.fields()

            self.set_dirty()

            self.drawName()
            self.parent().drawName()
            self.parent().drawStatus()


class _CodeItem(_SimpleItem, _DropSite):
    """
    This class implements a navigation item that represents code in a header
    file.
    """
    def __init__(self, parent, cd, after=None):
        """
        Initialise the item instance.

        parent is the parent.
        cd is the code instance.
        after is the sibling after which this should be placed.  If it is None
        then it should be placed at the end.  If it is the parent then it
        should be placed at the start.
        """
        self.code = cd

        _SimpleItem.__init__(self, parent, after)
        _DropSite.__init__(self)

        self._targets = []

        if cd.status == "ignored":
            self.setHidden(True)

        # Create any children.
        unnamed_args = False

        if hasattr(cd, "args"):
            if isinstance(cd, (OperatorMethod, OperatorCast, OperatorFunction)):
                access = 'private'
            else:
                try:
                    access = cd.access
                except AttributeError:
                    access = ''

            for a in cd.args:
                _Argument(self, a)

                if access != 'private' and a.unnamed and a.default != '':
                    unnamed_args = True
        elif isinstance(cd, (Class, Enum, Namespace)):
            for c in cd.content:
                _CodeItem(self, c)

        # The parent should be open if it is not ignored and we are, or we are
        # todo or unknown.
        if (not isinstance(parent, _CodeItem) or parent.code.status != "ignored") and (cd.status in ("todo", "unknown") or (cd.status == "" and unnamed_args) or self.isExpanded()):
            parent.setExpanded(True)

        self._editors = {}

    def getName(self):
        """
        Return the value of the name column.
        """
        return self.code.user()

    def getAccess(self):
        """
        Return the value of the access column.
        """
        # Not everything has an access specifier.
        try:
            a = self.code.access
        except AttributeError:
            a = ""

        return a

    def getStatus(self):
        """
        Return the value of the status column.
        """
        s = self.code.status
        status = []

        if s == "todo":
            text = "Todo"
        elif s == "unknown":
            text = "Unchecked"
        elif s == "ignored":
            text = "Ignored"
        else:
            text = ""

        if text:
            status.append(text)

        if hasattr(self.code, 'args'):
            if isinstance(self.code, (OperatorMethod, OperatorCast, OperatorFunction)):
                access = 'private'
            else:
                try:
                    access = self.code.access
                except AttributeError:
                    access = ''

            for a in self.code.args:
                if access != 'private' and a.unnamed and a.default != '':
                    status.append("Unnamed arguments")
                    break

        return ", ".join(status)

    def getGenerations(self):
        """
        Return the value of the generations column.
        """
        return (self.code.sgen, self.code.egen)

    def droppable(self, source):
        """
        Determine if an item can be dropped here.
        """
        if not isinstance(source, _CodeItem):
            return False

        # We can only move code around its siblings or onto its parent.
        owner = source.parent()

        return (owner is self.parent() or owner is self)

    def drop(self, source, after=None):
        """
        Handle the item being dropped here.

        source is the item being dropped.
        after is the optional child on which the item was dropped.
        """
        owner = source.parent()

        if after is not None or owner is self:
            # Either a child has been dropped on us to move it to the start,
            # or we've been called by a child to place a sibling immediately
            # after it.
            cd = self.code

            cd.remove(source.code)
            owner.removeChild(source)

            if after:
                at = cd.index(after.code) + 1
            else:
                at = 0

            cd.insert(at, source.code)
            owner.insertChild(at, source)

            self.set_dirty()
        else:
            # Get the parent to handle the move.
            self.parent().drop(source, self)

    def getMenu(self, slist):
        """
        Return the item's context menu.

        slist is a list of siblings of the item that is also selected.
        """
        # Save the list of targets for the menu action, including this one.
        self._targets = slist[:]
        self._targets.append(self)

        menu = [("Checked", self._setStatusChecked, True, (self.code.status == "")),
                ("Todo", self._setStatusTodo, True, (self.code.status == "todo")),
                ("Unchecked", self._setStatusUnchecked, True, (self.code.status == "unknown")),
                ("Ignored", self._setStatusIgnored, True, (self.code.status == "ignored"))]

        if slist:
            menu.append(None)
            menu.append(("Versions...", self._generationsSlot, len(self.pane.gui.project.versions) != 0))

            return menu

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

        # Handle the manual code part of the menu.
        menu.append(None)
        menu.append(("Add manual code...", self._addManualCode))

        # See what extra menu items are needed.
        thcslot = False
        tcslot = False
        cttcslot = False
        mcslot = False
        vccslot = False
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
            menu.append(("Modify manual code...", self._precisManualCode))
            menu.append(("Modify manual code body...", self._bodyManualCode, ("mcb" not in self._editors)))

            mcslot = True
            pslot = self._callablePropertiesSlot
            dsslot = True
        elif isinstance(self.code, OpaqueClass):
            pslot = self._opaqueClassPropertiesSlot
        elif isinstance(self.code, Namespace):
            thcslot = True
        elif isinstance(self.code, Class):
            thcslot = True
            tcslot = True
            cttcslot = True
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
            pslot = self._classPropertiesSlot
            dsslot = True
        elif isinstance(self.code, Constructor):
            mcslot = True
            pslot = self._callablePropertiesSlot
            dsslot = True
        elif isinstance(self.code, Destructor):
            mcslot = True
            vccslot = True
            pslot = self._callablePropertiesSlot
        elif isinstance(self.code, OperatorCast):
            mcslot = True
            pslot = self._callablePropertiesSlot
        elif isinstance(self.code, Method):
            mcslot = True

            if self.code.virtual:
                vccslot = True

            pslot = self._callablePropertiesSlot
            dsslot = True
        elif isinstance(self.code, OperatorMethod):
            mcslot = True

            if self.code.virtual:
                vccslot = True

            pslot = self._callablePropertiesSlot
        elif isinstance(self.code, Function):
            mcslot = True
            pslot = self._callablePropertiesSlot
            dsslot = True
        elif isinstance(self.code, OperatorFunction):
            mcslot = True
            pslot = self._callablePropertiesSlot
        elif isinstance(self.code, Variable):
            acslot = True
            gcslot = True
            scslot = True
            pslot = self._variablePropertiesSlot
        elif isinstance(self.code, Enum):
            pslot = self._enumPropertiesSlot
        elif isinstance(self.code, EnumValue):
            pslot = self._enumValuePropertiesSlot

        if thcslot or tcslot or cttcslot or sccslot or mcslot or vccslot or acslot or gcslot or scslot or gctcslot or gcccslot or bigetbslot or birelbslot or birbslot or biwbslot or biscslot or bicbslot or pickslot or xaslot or dsslot:
            menu.append(None)

            if thcslot:
                menu.append(("%TypeHeaderCode", self._typeheaderCodeSlot, ("thc" not in self._editors)))

            if tcslot:
                menu.append(("%TypeCode", self._typeCodeSlot, ("tc" not in self._editors)))

            if cttcslot:
                menu.append(("%ConvertToTypeCode", self._convTypeCodeSlot, ("cttc" not in self._editors)))

            if sccslot:
                menu.append(("%ConvertToSubClassCode", self._subclassCodeSlot, ("scc" not in self._editors)))

            if mcslot:
                menu.append(("%MethodCode", self._methodCodeSlot, ("mc" not in self._editors)))

            if vccslot:
                menu.append(("%VirtualCatcherCode", self._virtualCatcherCodeSlot, ("vcc" not in self._editors)))

            if acslot:
                menu.append(("%AccessCode", self._accessCodeSlot, ("ac" not in self._editors)))

            if gcslot:
                menu.append(("%GetCode", self._getCodeSlot, ("gc" not in self._editors)))

            if scslot:
                menu.append(("%SetCode", self._setCodeSlot, ("sc" not in self._editors)))

            if gctcslot:
                menu.append(("%GCTraverseCode", self._gcTraverseCodeSlot, ("gctc" not in self._editors)))

            if gcccslot:
                menu.append(("%GCClearCode", self._gcClearCodeSlot, ("gccc" not in self._editors)))

            if bigetbslot:
                menu.append(("%BIGetBufferCode", self._biGetBufCodeSlot, ("bigetb" not in self._editors)))

            if birelbslot:
                menu.append(("%BIReleaseBufferCode", self._biRelBufCodeSlot, ("birelb" not in self._editors)))

            if birbslot:
                menu.append(("%BIGetReadBufferCode", self._biReadBufCodeSlot, ("birb" not in self._editors)))

            if biwbslot:
                menu.append(("%BIGetWriteBufferCode", self._biWriteBufCodeSlot, ("biwb" not in self._editors)))

            if biscslot:
                menu.append(("%BIGetSegCountCode", self._biSegCountCodeSlot, ("bisc" not in self._editors)))

            if bicbslot:
                menu.append(("%BIGetCharBufferCode", self._biCharBufCodeSlot, ("bicb" not in self._editors)))

            if pickslot:
                menu.append(("%PickleCode", self._pickleCodeSlot, ("pick" not in self._editors)))

            if dsslot:
                menu.append(("%Docstring", self._docstringSlot, ("ds" not in self._editors)))

        if isinstance(self.code, (Class, Constructor, Function, Method)):
            menu.append(None)
            menu.append(("Apply argument naming conventions...", self._nameFromConventions))
            menu.append(("Accept all argument names", self._acceptNames))

        # Add the extra menu items.
        menu.append(None)
        menu.append(("Versions...", self._generationsSlot,
                len(self.pane.gui.project.versions) != 0))
        menu.append(("Platform Tags...", self._platformTagsSlot,
                len(self.pane.gui.project.platforms) != 0))
        menu.append(("Feature Tags...", self._featureTagsSlot,
                (len(self.pane.gui.project.features) != 0 or len(self.pane.gui.project.externalfeatures) != 0)))

        if pslot:
            menu.append(("Properties...", pslot))

        menu.append(None)
        menu.append(("Delete", self._deleteCode, (not self._editors)))

        return menu

    def _nameFromConventions(self):
        """ Apply the argument naming conventions to all unnamed arguments. """

        self.pane.nameArgumentsFromConventions(self.code)

    def _acceptNames(self):
        """ Accept all argument names. """

        self.pane.acceptArgumentNames(self.code)

    def _getScope(self):
        """
        Return the object that is the containing scope of this item.
        """
        prnt = self.parent()

        if isinstance(prnt, _CodeItem):
            scope = prnt.code
        else:
            scope = prnt.headerfile

        return scope

    def _addManualCode(self):
        """
        Slot to handle the creation of manual code.
        """
        dlg = ManualCodeDialog("", self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (precis, ) = dlg.fields()

            if precis:
                mc = ManualCode(precis=precis)

                self.set_dirty()

                scope = self._getScope()
                scope.insert(scope.index(self.code) + 1, mc)

                _CodeItem(self.parent(), mc, self)

    def _precisManualCode(self):
        """
        Slot to handle the update of the manual code.
        """
        dlg = ManualCodeDialog(self.code.precis, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (precis, ) = dlg.fields()

            if self.code.precis != precis:
                self.code.precis = precis
                self.drawName()

            self.set_dirty()

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
        Slot to handle the deletion of a code item.
        """
        ans = QMessageBox.question(self.pane, "Delete Code",
"Are you sure you want to delete this code?",
                                   QMessageBox.Yes,
                                   QMessageBox.No|QMessageBox.Default|QMessageBox.Escape)

        if ans == QMessageBox.Yes:
            self._getScope().remove(self.code)
            self.parent().removeChild(self)
            self.set_dirty()

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

    def _convTypeCodeSlot(self):
        """
        Slot to handle %ConvertToTypeCode.
        """
        ed = ExternalEditor()
        ed.editDone.connect(self._convTypeCodeDone)
        ed.edit(self.code.convtotypecode, "%ConvertToTypeCode: " + self.code.user())
        self._editors["cttc"] = ed

    def _convTypeCodeDone(self, text_changed, text):
        """
        Slot to handle changed %ConvertToTypeCode.

        text_changed is set if the code has changed.
        text is the code.
        """
        if text_changed:
            self.code.convtotypecode = text
            self.set_dirty()

        del self._editors["cttc"]

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

    def _generationsSlot(self):
        """
        Slot to handle the generations.
        """
        dlg = GenerationsDialog(self.pane.gui.project, self.code.sgen, self.code.egen, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (sgen, egen) = dlg.fields()

            for itm in self._targets:
                itm.code.sgen = sgen
                itm.code.egen = egen

                itm.drawGenerations()

            self.set_dirty()

    def _platformTagsSlot(self):
        """
        Slot to handle the platform tags.
        """
        code = self.code
        dlg = PlatformPickerDialog(self.pane.gui.project, code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.platforms, ) = dlg.fields()

            self.set_dirty()

    def _featureTagsSlot(self):
        """
        Slot to handle the feature tags.
        """
        code = self.code
        dlg = FeaturePickerDialog(self.pane.gui.project, code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.features, ) = dlg.fields()

            self.set_dirty()

    def _opaqueClassPropertiesSlot(self):
        """
        Slot to handle the properties for opaque classes.
        """
        code = self.code
        dlg = OpaqueClassPropertiesDialog(code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.annos, ) = dlg.fields()

            self.set_dirty()

            self.setText(0, self.code.user())

    def _classPropertiesSlot(self):
        """
        Slot to handle the properties for classes.
        """
        code = self.code
        dlg = ClassPropertiesDialog(code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.pybases, code.annos) = dlg.fields()

            self.set_dirty()

            self.setText(0, self.code.user())

    def _callablePropertiesSlot(self):
        """
        Slot to handle the properties for callables.
        """
        code = self.code
        dlg = CallablePropertiesDialog(code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (pytype, pyargs, code.annos) = dlg.fields()

            if hasattr(code, "pytype") and code.pytype is not None:
                code.pytype = pytype

            if hasattr(code, "pyargs"):
                code.pyargs = pyargs

            self.set_dirty()

            self.setText(0, self.code.user())

    def _variablePropertiesSlot(self):
        """
        Slot to handle the properties for variables.
        """
        code = self.code
        dlg = VariablePropertiesDialog(code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.annos, ) = dlg.fields()

            self.set_dirty()

            self.setText(0, self.code.user())

    def _enumPropertiesSlot(self):
        """
        Slot to handle the properties for enums.
        """
        code = self.code
        dlg = EnumPropertiesDialog(code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.annos, ) = dlg.fields()

            self.set_dirty()

            self.setText(0, self.code.user())

    def _enumValuePropertiesSlot(self):
        """
        Slot to handle the properties for enum values.
        """
        code = self.code
        dlg = EnumValuePropertiesDialog(self.code, self.pane)

        if dlg.exec_() == QDialog.Accepted:
            (code.annos, ) = dlg.fields()

            self.set_dirty()

            self.setText(0, self.code.user())

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
                itm.drawStatus()

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
        if self.code.access != new:
            self.code.access = new
            self.set_dirty()
            self.drawAccess()
