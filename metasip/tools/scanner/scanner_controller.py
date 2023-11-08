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


import glob
import hashlib
import os

from PyQt5.QtWidgets import QInputDialog

from ...dip.model import Instance, List, observe, unadapted
from ...dip.shell import IDirty
from ...dip.ui import Application, Controller

from ...interfaces.project import (ICallable, ICodeContainer, IConstructor,
        IEnum, IHeaderDirectory, IHeaderFile, IProject)
from ...logger import Logger
from ...Project import (HeaderDirectory, HeaderFile, HeaderFileVersion,
        ManualCode, Project, SipFile, VersionRange)

from .scanner_view import ScannerView


class ScannerController(Controller):
    """ The ScannerController implements the controller for the scanner tool
    GUI.
    """

    # The current header directory.
    current_header_directory = Instance(IHeaderDirectory)

    # The current header files.
    current_header_files = List(IHeaderFile)

    # The current project.
    current_project = Instance(IProject)

    # The current project specific user interface.
    current_project_ui = Instance(ScannerView)

    def activate_project(self, project):
        """ Activate a project. """

        self.current_project = project
        self.current_project_ui = project_ui = self._find_view(project)

        # Make sure the project's view is current.
        self.view.project_views.current_view = project_ui

        # Configure the versions.
        self._update_from_versions()
        self.model.working_version = project_ui.working_version

        # Configure the Scan form.
        self._update_from_headers()

        # Configure from the selection.
        project_ui.refresh_selection()

    def close_project(self, project):
        """ Close a project. """

        view = self.view

        project_views = view.project_views.views

        # Remove the observers.
        observe('headers', project, self.__on_headers_changed, remove=True)
        observe('versions', project, self.__on_versions_changed, remove=True)

        # Remove the project specific part of the GUI.
        project_views.remove(self._find_view(project))

        # Hide the GUI if there are no more projects.
        if len(project_views) == 0:
            view.current_view = view.no_project

    def open_project(self, project):
        """ Open a project. """

        view = self.view

        project_views = view.project_views.views

        # Show the GUI if it was previously hidden.
        if len(project_views) == 0:
            view.current_view = view.metasip_scanner_splitter

        # Create the project specific part of the GUI.
        project_views.append(ScannerView(self, project))

        # Observe any changes to the header directories and versions.
        observe('headers', project, self.__on_headers_changed)
        observe('versions', project, self.__on_versions_changed)

    def update_view(self):
        """ Reimplemented to update the state of the view after a change. """

        # This is called very early.
        if self.current_project_ui is None:
            return

        model = self.model
        view = self.view

        self._update_from_source_directory()

        # Update the working version.
        self.current_project_ui.set_working_version(model.working_version)

        # Configure the state of the file Update and Parse buttons and the
        # assigned module editor.
        module_enabled = False
        parse_enabled = False
        update_enabled = False

        if model.ignored:
            model.module = ''
            update_enabled = True
        else:
            module_enabled = True

            if self.is_valid(view.module):
                update_enabled = True

                if model.source_directory != '' and model.module != '' and len(self.current_header_files) == 1:
                    parse_enabled = True

        view.module.enabled = module_enabled
        view.parse.enabled = parse_enabled
        view.update_file.enabled = update_enabled

        super().update_view()

    def selection(self, selected_items):
        """ This is called by the project specific view when the selected items
        changes.
        """

        # Only multiple header files within the same directory are allowed.
        header_directory = None
        header_files = []

        if len(selected_items) == 1:
            selection = selected_items[0]

            if isinstance(selection, HeaderFile):
                header_files = [selection]
                header_directory = self.current_project.findHeaderDirectory(
                        selection)
            elif isinstance(selection, HeaderDirectory):
                header_directory = selection

        elif len(selected_items) > 1:
            hdir = None

            for selection in selected_items:
                if not isinstance(selection, HeaderFile):
                    break

                if hdir is None:
                    hdir = self.current_project.findHeaderDirectory(selection)
                elif hdir is not self.current_project.findHeaderDirectory(selection):
                    break
            else:
                header_files = selected_items
                header_directory = hdir

        model = self.model
        view = self.view

        if header_directory is not None:
            self.current_header_directory = header_directory
            model.header_directory_name = header_directory.name
            model.file_filter = header_directory.filefilter
            model.suffix = header_directory.inputdirsuffix
            model.parser_arguments = header_directory.parserargs
            view.directory_group.enabled = True
            view.delete.enabled = True
        else:
            self.current_header_directory = None
            model.header_directory_name = ''
            model.file_filter = ''
            model.suffix = ''
            model.parser_arguments = ''
            view.directory_group.enabled = False
            view.delete.enabled = False

        if len(header_files) != 0:
            # The delete button is enabled for a selected header directory, or
            # a single header file that is either ignored or unused.
            if len(header_files) > 1:
                view.delete.enabled = False
            else:
                hfile = header_files[0]
                view.delete.enabled = (hfile.ignored or len(hfile.versions) == 0)

            # Create an amalgamation of the selected header files.
            hfile = header_files[0]
            names = [hfile.name]
            ignored = hfile.ignored
            module = hfile.module

            if len(header_files) > 1:
                names.append("...")

            for hfile in header_files[1:]:
                # If the files have different values then fall back to the
                # defaults.
                if ignored != hfile.ignored:
                    ignored = False

                if module != hfile.module:
                    module = ''

            self.current_header_files = header_files
            model.header_file_name = (", ").join(names)
            model.ignored = ignored
            model.module = module
            view.file_group.enabled = True
        else:
            self.current_header_files = []
            model.header_file_name = ''
            model.ignored = False
            model.module = ''
            view.file_group.enabled = False

        self._update_from_source_directory()

    def _find_view(self, project):
        """ Find the project specific part of the GUI for a project. """

        for view in self.view.project_views.views:
            scanner_view = unadapted(view)
            if scanner_view.project is project:
                return scanner_view

        # This should never happen.
        return None

    @observe('view.delete.value')
    def __on_delete_changed(self, change):
        """ Invoked when the Delete button is pressed. """

        project = self.current_project

        if len(self.current_header_files) != 0:
            title = "Delete Header File"
            question = "Are you sure you want to delete this header file?"
        else:
            title = "Delete Header Directory"

            has_cache = ""
            for hfile in self.current_header_directory.content:
                if not hfile.ignored and hfile.module != '' and len(hfile.versions) != 0:
                    has_cache = " (which includes saved header file signatures)"
                    break

            question = "Are you sure you want to delete this header directory{0}?".format(has_cache)

        confirmed = Application.question(title, question, self.view.delete)

        if confirmed == 'yes':
            if len(self.current_header_files) != 0:
                self.current_header_directory.content.remove(
                        self.current_header_files[0])
            else:
                project.headers.remove(self.current_header_directory)

            IDirty(project).dirty = True

    @observe('view.hide_ignored.value')
    def __on_hide_ignored_changed(self, change):
        """ Invoked when the Hide Ignored button is pressed. """

        self.current_project_ui.hide_ignored(self.current_header_directory,
                hide=True)

    @observe('view.new.value')
    def __on_new_changed(self, change):
        """ Invoked when the New button is pressed. """

        project = self.current_project
        title = "New Header Directory"

        # Get the name of the header directory.
        (hname, ok) = QInputDialog.getText(unadapted(self.view.new),
                title, "Descriptive name")

        if ok:
            hname = hname.strip()

            if hname == '':
                Application.warning(title,
                        "The name of a header directory must not be blank.",
                        unadapted(self.view.new))
            elif hname in [hdir.name for hdir in project.headers]:
                Application.warning(title,
                        "'{0}' is already used as the name of a header directory.".format(hname),
                        unadapted(self.view_new))
            else:
                working_version = self._working_version_as_string()

                hdir = HeaderDirectory(name=hname, scan=[working_version])
                project.headers.append(hdir)

                IDirty(project).dirty = True

    @observe('view.parse.value')
    def __on_parse_changed(self, change):
        """ Invoked when the Parse button is pressed. """

        from ...CastXML import CastXMLParser

        project = self.current_project
        hdir = self.current_header_directory
        hfile = self.current_header_files[0]

        parser = CastXMLParser()

        name = os.path.join(self.model.source_directory, hdir.inputdirsuffix,
                hfile.name)

        if not os.access(name, os.R_OK):
            Application.warning("Parse", "Unable to read {0}.".format(name),
                    self.view.parse)
            return

        _, name, _ = self._read_header(name)

        phf = parser.parse(project, self.model.source_directory, hdir, hfile,
                name)

        if phf is None:
            Application.warning("Parse", parser.diagnostic, self.view.parse)
            return

        # Find the corresponding .sip file creating it if is a new header file.
        # FIXME: Assuming we ultimately want to be able to create a complete
        #        project without parsing .h files then we will need the ability
        #        (in the main editor) to manually create a SipFile instance.
        for mod in project.modules:
            if mod.name == hfile.module:
                for sfile in mod.content:
                    if sfile.name == hfile.name:
                        break
                else:
                    sfile = SipFile(name=hfile.name)
                    mod.content.append(sfile)

                self._merge_code(sfile, phf)

                break

        # The file version no longer needs parsing.
        working_version = self._working_version_as_string()

        for hfile_version in hfile.versions:
            if hfile_version.version == working_version:
                hfile_version.parse = False
                break

        IDirty(project).dirty = True

    def _merge_code(self, dsc, ssc):
        """ Merge source code into destination code. """

        working_version = self._working_version_as_string()

        # Go though each existing code item.
        for dsi in list(dsc.content):
            # Manual code is always retained.
            if isinstance(dsi, ManualCode):
                continue

            # Go through each potentially new code item.
            for ssi in list(ssc):
                if type(dsi) is type(ssi) and dsi.signature(working_version) == ssi.signature(working_version):
                    # Make sure the versions include the working version.
                    if working_version != '':
                        self._add_working_version(dsi)

                    # Discard the new code item.
                    ssc.remove(ssi)

                    # Merge any child code.
                    if isinstance(dsi, (ICodeContainer, IEnum)):
                        self._merge_code(dsi, ssi.content)

                    break
            else:
                # The existing one doesn't exist in the working version.
                if working_version == '':
                    # If it is ignored then forget about it because there are
                    # no other versions that might refer to it.
                    if dsi.status == 'ignored':
                        dsc.content.remove(dsi)
                    else:
                        dsi.status = 'removed'
                else:
                    version_status = self._remove_working_version(dsi)
                    if version_status == 'no_longer_working':
                        # It's removal needs checking.
                        if dsi.status == '':
                            dsi.status = 'unknown'
                    elif version_status == 'no_longer_any':
                        # Forget about it because there are no other versions
                        # that refer to it.
                        dsc.content.remove(dsi)

        # Anything left in the source code is new.

        if working_version == '':
            startversion = endversion = ''
        else:
            versions = self.current_project.versions
            working_idx = versions.index(working_version)

            # If the working version is the first then assume that the new item
            # will appear in earlier versions, otherwise it is restricted to
            # this version.
            startversion = '' if working_idx == 0 else working_version

            # If the working version is the latest then assume that the new
            # item will appear in later versions, otherwise it is restricted to
            # this version.
            try:
                endversion = versions[working_idx + 1]
            except IndexError:
                endversion = ''

        for ssi in ssc:
            if startversion != '' or endversion != '':
                ssi.versions.append(
                        VersionRange(startversion=startversion,
                                endversion=endversion))

            # Try and place the new item with any similar one.
            pos = -1
            for idx, code in enumerate(dsc.content):
                if type(code) is not type(ssi):
                    continue

                if isinstance(ssi, IConstructor):
                    pos = idx
                    break
                    
                if isinstance(ssi, ICallable) and code.name == ssi.name:
                    pos = idx
                    break
                    
            if pos >= 0:
                dsc.content.insert(pos, ssi)
            else:
                dsc.content.append(ssi)

    def _add_working_version(self, api_item):
        """ Add the working version to an item's version ranges. """

        # There is only something to do if the item is currently versioned.
        if len(api_item.versions) != 0:
            project = self.current_project

            # Construct the existing list of version ranges to a version map.
            vmap = project.vmap_create(False)
            project.vmap_or_version_ranges(vmap, api_item.versions)

            # Add the working version.
            working_idx = project.versions.index(self.model.working_version)
            vmap[working_idx] = True

            # Convert the version map back to a list of version ranges.
            api_item.versions = project.vmap_to_version_ranges(vmap)

    def _remove_working_version(self, api_item):
        """ Remove the working version from an item's version ranges.  Returns
        'wasnt_working' if the item wasn't in the working version,
        'no_longer_working' if the item is no longer in the working version and
        'no_longer_any' if the item is no longer in any version.
        """

        project = self.current_project

        # Construct the existing list of version ranges to a version map.
        if len(api_item.versions) == 0:
            vmap = project.vmap_create(True)
        else:
            vmap = project.vmap_create(False)
            project.vmap_or_version_ranges(vmap, api_item.versions)

        # Update the version map appropriately using the working version.
        # First take a shortcut to see if anything has changed.
        working_idx = project.versions.index(self.model.working_version)

        if not vmap[working_idx]:
            return 'wasnt_working'

        vmap[working_idx] = False

        # Convert the version map back to a list of version ranges.
        versions = project.vmap_to_version_ranges(vmap)

        if versions is None:
            return 'no_longer_any'

        api_item.versions = versions

        return 'no_longer_working'

    @observe('view.reset_workflow.value')
    def __on_reset_workflow_changed(self, change):
        """ Invoked when the Reset Workflow button is pressed. """

        project = self.current_project
        working_version = self._working_version_as_string()

        for hdir in project.headers:
            if working_version not in hdir.scan:
                hdir.scan.append(working_version)

        IDirty(project).dirty = True

    @observe('view.scan.value')
    def __on_scan_changed(self, change):
        """ Invoked when the Scan button is pressed. """

        project = self.current_project
        hdir = self.current_header_directory

        sd = os.path.abspath(self.model.source_directory)

        if hdir.inputdirsuffix != '':
            sd = os.path.join(sd, hdir.inputdirsuffix)

        Logger.log("Scanning header directory {0}".format(sd))

        if hdir.filefilter != '':
            sd = os.path.join(sd, hdir.filefilter)

        # Save the files that were in the directory.
        saved = list(hdir.content)

        for hpath in glob.iglob(sd):
            if not os.path.isfile(hpath):
                continue

            if os.access(hpath, os.R_OK):
                hfile = self._scan_header_file(hpath)

                for shf in saved:
                    if shf is hfile:
                        saved.remove(shf)
                        break
                else:
                    # It's a new header file.
                    hdir.content.append(hfile)
                    IDirty(project).dirty = True

                Logger.log("Scanned {0}".format(hpath))
            else:
                Logger.log("Skipping unreadable header file {0}".format(hpath))

        # Anything left in the saved list has gone missing or was already
        # missing.
        working_version = self._working_version_as_string()

        for hfile in saved:
            for hfile_version in hfile.versions:
                if hfile_version.version == working_version:
                    # If there is only one version left then remove the file
                    # itself.
                    if len(hfile.versions) == 1:
                        hdir.content.remove(hfile)
                        self._remove_from_module(hfile)
                    else:
                        # FIXME: Go through the corresponding SipFile and make
                        # sure that all top-level items have an upper version
                        # set.
                        hfile.versions.remove(hfile_version)

                    Logger.log(
                            "{0} is no longer in the header directory".format(
                                    hfile.name))

                    IDirty(project).dirty = True

                    break

        # This version no longer needs scanning.
        if working_version in hdir.scan:
            hdir.scan.remove(working_version)
            IDirty(project).dirty = True

    def _remove_from_module(self, hfile):
        """ Handle the removal of a header file from the project. """

        for mod in self.current_project.modules:
            if mod.name == hfile.module:
                for sfile in mod.content:
                    if sfile.name == hfile.name:
                        for code in list(sfile.content):
                            if code.status == 'ignored':
                                sfile.content.remove(code)
                            else:
                                code.status = 'removed'

    def _scan_header_file(self, hpath):
        """ Scan a header file and return the header file instance.  hpath is
        the full pathname of the header file.
        """

        # Calculate the MD5 signature ignoring any comments.  Note that nested
        # C style comments aren't handled very well.
        m = hashlib.md5()

        src, _, encoding = self._read_header(hpath)

        lnr = 1
        state = 'copy'
        copy = ""
        idx = 0

        for ch in src:
            # Get the previous character.
            if idx > 0:
                prev = src[idx - 1]
            else:
                prev = ""

            idx += 1

            # Line numbers must be accurate.
            if ch == "\n":
                lnr += 1

            # Handle the end of a C style comment.
            if state == 'ccmnt':
                if ch == "/" and prev == "*":
                    state = 'copy'

                continue

            # Handle the end of a C++ style comment.
            if state == 'cppcmnt':
                if ch == "\n":
                    state = 'copy'

                continue

            # We must be in the copy state.

            if ch == "*" and prev == "/":
                # The start of a C style comment.
                state = 'ccmnt'
                continue

            if ch == "/" and prev == "/":
                # The start of a C++ style comment.
                state = 'cppcmnt'
                continue

            # At this point we know the previous character wasn't part of a
            # comment.
            if prev:
                m.update(prev.encode(encoding))

        # Note that we didn't add the last character, but it would normally be
        # a newline.
        md5 = m.hexdigest()

        # See if we already know about the file.
        hdir = self.current_header_directory
        hfile_name = os.path.basename(hpath)

        for hfile in hdir.content:
            if hfile.name == hfile_name:
                break
        else:
            # It's a new file.
            hfile = HeaderFile(name=hfile_name)

        # See if we already know about this version.
        working_version = self._working_version_as_string()

        for hfile_version in hfile.versions:
            if hfile_version.version == working_version:
                # See if the version's contents have changed.
                if hfile_version.md5 != md5:
                    hfile_version.md5 = md5
                    hfile_version.parse = True

                    IDirty(self.current_project).dirty = True

                break
        else:
            # It's a new version.
            hfile_version = HeaderFileVersion(version=working_version, md5=md5)
            hfile.versions.append(hfile_version)

            # Check that the project has versions.
            if self.current_project.versions:
                # Find the immediately preceding version if there is one.
                versions_sorted = sorted(hfile.versions,
                        key=lambda v: self.current_project.versions.index(
                                v.version))

                prev_md5 = ''
                prev_parse = True
                for hfv in versions_sorted:
                    if hfv.version == working_version:
                        break

                    prev_md5 = hfv.md5
                    prev_parse = hfv.parse

                if prev_md5 == md5:
                    hfile_version.parse = prev_parse
            else:
                # It must be a new file of an unversioned project.
                hfile_version.parse = True

            IDirty(self.current_project).dirty = True

        return hfile

    @observe('view.show_ignored.value')
    def __on_show_ignored_changed(self, change):
        """ Invoked when the Show Ignored button is pressed. """

        self.current_project_ui.hide_ignored(self.current_header_directory,
                hide=False)

    @observe('view.update_directory.value')
    def __on_update_directory_changed(self, change):
        """ Invoked when the Update header directory button is pressed. """

        hdir = self.current_header_directory
        model = self.model

        hdir.filefilter = model.file_filter
        hdir.inputdirsuffix = model.suffix
        hdir.parserargs = model.parser_arguments

        IDirty(self.current_project).dirty = True

    @observe('view.update_file.value')
    def __on_update_file_changed(self, change):
        """ Invoked when the Update header file button is pressed. """

        model = self.model

        for hfile in self.current_header_files:
            hfile.ignored = model.ignored
            hfile.module = model.module

        IDirty(self.current_project).dirty = True

    def __on_headers_changed(self, change):
        """ Invoked when the list of project header directories changes. """

        if change.model is self.current_project:
            self._update_from_headers()

    def __on_versions_changed(self, change):
        """ Invoked when the list of project versions changes. """

        if change.model is self.current_project:
            # See if the current working version is being affected.
            if self.current_project_ui.working_version in change.old:
                # Determine a sensible new working version.
                if len(change.new) != 0:
                    working_version = change.new[0]
                elif len(change.model.versions) == 0:
                    working_version = None
                else:
                    working_version = change.model.versions[-1]

                self.current_project_ui.set_working_version(working_version)

            self._update_from_versions()

    def _update_from_headers(self):
        """ Update the GUI from the current project's list of header
        directories.
        """

        view = self.view

        enabled = (len(self.current_project.headers) != 0)

        view.scan_form.enabled = enabled
        view.reset_workflow.enabled = enabled

    def _update_from_source_directory(self):
        """ Update the GUI from the source directory. """

        model = self.model
        view = self.view

        view.scan.enabled = (model.source_directory != '' and self.current_header_directory is not None)

        view.parse.enabled = (model.source_directory != '' and model.module != '' and len(self.current_header_files) == 1)

    def _update_from_versions(self):
        """ Update the GUI from the current project's list of versions. """

        optionselector = self.view.working_version
        versions = self.current_project.versions

        if len(versions) == 0:
            optionselector.visible = False
        else:
            optionselector.options = reversed(versions)
            optionselector.visible = True

    def _working_version_as_string(self):
        """ Return the working version as a string.  This will be an empty
        string if versions haven't been explicitly defined.
        """

        working_version = self.model.working_version
        if working_version is None:
            working_version = ''

        return working_version

    @classmethod
    def _read_header(cls, name):
        """ Read the contents of a header file.  Handle the special case of the
        file just being a #include redirect to another header file.
        """

        contents, actual_name, encoding = cls._read_single_header(name)
        while actual_name != name:
            name = actual_name
            contents, actual_name, encoding = cls._read_single_header(name)

        return contents, actual_name, encoding

    @staticmethod
    def _read_single_header(name):
        """ Read the contents of a single header file. """

        f = open(name, 'r')
        contents = f.read()
        encoding = f.encoding
        f.close()

        lines = contents.strip().split('\n')
        if len(lines) == 1:
            words = lines[0].split()
            if len(words) == 2 and words[0] == '#include':
                include_name = words[1]
                if include_name.startswith('".') and include_name.endswith('"'):
                    name = os.path.dirname(name) + '/' + include_name[1:-1]

        return contents, name, encoding
