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


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem

from dip.model import observe


class ScannerView(QTreeWidget):
    """ ScannerView is an internal class that implements the project specific
    part of the scanner tool GUI.
    """

    # The column numbers.
    (NAME, STATUS) = range(2)

    def __init__(self, controller, project):
        """ Initialise the view. """

        super().__init__(objectName='metasip.scanner.explorer')

        self.setHeaderLabels(["Name", "Status"])

        self.setSelectionMode(self.ExtendedSelection)
        self.itemSelectionChanged.connect(self.refresh_selection)

        self._controller = controller
        self.project = project
        self.source_directory = ''

        try:
            self.working_version = project.versions[-1]
        except IndexError:
            self.working_version = None

        ProjectItem(project, self)

        self._update_working_version()

    def hide_ignored(self, header_directory, hide):
        """ Show or hide all the ignored files in a header directory. """

        for itm in self._items():
            if itm.get_project_item() is header_directory:
                for hfile_idx in range(itm.childCount()):
                    hfile_itm = itm.child(hfile_idx)

                    if hfile_itm.get_working_file() is not None and hfile_itm.text(ScannerView.STATUS) == "Ignored":
                        hfile_itm.setHidden(hide)

                break

    def set_working_version(self, working_version):
        """ Set the working version. """

        if self.working_version != working_version:
            self.working_version = working_version
            self._update_working_version()

    def refresh_selection(self):
        """ Invoked when the item selection changes. """

        self._controller.selection(
                [itm.get_project_item() for itm in self.selectedItems()])

    def _update_working_version(self):
        """ Update the working version for all items. """

        for itm in self._items():
            itm.update_working_version()

    def _items(self, root=None):
        """ A generator for all the items in the tree depth first. """

        if root is None:
            root = self.invisibleRootItem()

        for i in range(root.childCount()):
            child = root.child(i)

            for itm in self._items(child):
                yield itm

            yield child


class ScannerItem(QTreeWidgetItem):
    """ ScannerItem is an internal base class for all items in the scanner tool
    tree.
    """

    def update_working_version(self):
        """ Update in the light of the working versions.  This default
        implementation does nothing.
        """

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        raise NotImplementedError

    def sort(self):
        """ Sort the item's children. """

        self.sortChildren(ScannerView.NAME, Qt.AscendingOrder)


class ProjectItem(ScannerItem):
    """ ProjectItem is an internal class that represents a project in the
    scanner tool GUI.
    """

    def __init__(self, project, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self.setText(ScannerView.NAME, project.descriptive_name())
        observe('name', project,
                lambda c: self.setText(ScannerView.NAME,
                        c.model.descriptive_name()))

        self.setExpanded(True)

        for hdir in project.headers:
            HeaderDirectoryItem(hdir, self)

        observe('headers', project, self.__on_headers_changed)

        self.sort()

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        return self.treeWidget().project

    def __on_headers_changed(self, change):
        """ Invoked when the list of header directories changes. """

        for hdir in change.old:
            for idx in range(self.childCount()):
                itm = self.child(idx)
                if itm.get_project_item() is hdir:
                    self.removeChild(itm)
                    break

        for hdir in change.new:
            HeaderDirectoryItem(hdir, self)

        self.sort()


class HeaderDirectoryItem(ScannerItem):
    """ HeaderDirectoryItem is an internal class that represents a header
    directory in the scanner tool GUI.
    """

    def __init__(self, header_directory, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._header_directory = header_directory

        self._draw_status()
        observe('scan', header_directory, lambda c: self._draw_status())

        self.setText(ScannerView.NAME, header_directory.name)

        for header_file in header_directory.content:
            HeaderFileItem(header_file, self)

        observe('content', header_directory, self.__on_content_changed)

        self.sort()

    def update_working_version(self):
        """ Update in the light of the working version. """

        self._draw_status()

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        return self._header_directory

    def _draw_status(self):
        """ Draw the status column. """

        working_version = self.treeWidget().working_version
        if working_version is None:
            needs_scanning = (len(self._header_directory.scan) != 0)
        else:
            needs_scanning = (working_version in self._header_directory.scan)

        self.setText(ScannerView.STATUS,
                "Needs scanning" if needs_scanning else "")

    def __on_content_changed(self, change):
        """ Invoked when the list of header files changes. """

        for hfile in change.old:
            for idx in range(self.childCount()):
                itm = self.child(idx)
                if itm.get_project_item() is hfile:
                    self.removeChild(itm)
                    break

        for hfile in change.new:
            HeaderFileItem(hfile, self)

        self.sort()


class HeaderFileItem(ScannerItem):
    """ HeaderFileItem is an internal class that represents a header file in
    the scanner tool GUI.
    """

    def __init__(self, header_file, parent):
        """ Initialise the item. """

        super().__init__(parent)

        self._header_file = header_file

        self._draw_status()

        # Make the necessary observations so that we can keep the status up to
        # date.
        observe('ignored', header_file, self.__on_ignored_changed)
        observe('module', header_file, self.__on_module_changed)
        observe('versions', header_file, self.__on_versions_changed)

        for hfile_version in header_file.versions:
            observe('parse', hfile_version, self.__on_parse_changed)

        # Draw the rest of the item.
        self.setText(ScannerView.NAME, header_file.name)

    def update_working_version(self):
        """ Update in the light of the working version. """

        self._draw_status()

    def get_project_item(self):
        """ Return the item's corresponding project item. """

        return self._header_file

    def get_working_file(self):
        """ Get the version of the header file corresponding to the working
        version, if there is one.
        """

        working_version = self.treeWidget().working_version
        hfile_versions = self._header_file.versions

        if working_version is None:
            working_file = None if len(hfile_versions) == 0 else hfile_versions[0]
        else:
            for working_file in hfile_versions:
                if working_file.version == working_version:
                    break
            else:
                working_file = None

        return working_file

    def _draw_status(self):
        """ Draw the status column. """

        # Get the working version of the file, if any.
        working_file = self.get_working_file()

        self.setHidden(working_file is None)

        # Determine the status.
        expand = False

        if self._header_file.ignored:
            status = "Ignored"
            self.setHidden(True)
        elif self._header_file.module == '':
            status = "Needs assigning"
            expand = True
        elif len(self._header_file.versions) == 0:
            # This happens when all the versions containing this header file
            # have been deleted.
            status = "Unused"
            expand = True
            self.setHidden(False)
        elif working_file is not None and working_file.parse:
            status = "Needs parsing"
            expand = True
        else:
            status = ''

        self.setText(ScannerView.STATUS, status)

        if expand:
            self.parent().setExpanded(True)

    def __on_ignored_changed(self, change):
        """ Invoked when a header file's ignored state changes. """

        self._draw_status()

    def __on_module_changed(self, change):
        """ Invoked when a header file's assigned module changes. """

        self._draw_status()

    def __on_versions_changed(self, change):
        """ Invoked when a header file's list of versions changes. """

        for hfile_version in change.old:
            observe('parse', hfile_version, self.__on_parse_changed,
                    remove=True)

        for hfile_version in change.new:
            observe('parse', hfile_version, self.__on_parse_changed)

        self._draw_status()

    def __on_parse_changed(self, change):
        """ Invoked when a header file version's parse state changes. """

        self._draw_status()
