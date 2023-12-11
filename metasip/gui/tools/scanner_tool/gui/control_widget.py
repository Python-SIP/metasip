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

from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
        QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel,
        QLineEdit, QMessageBox, QPushButton, QStyle, QToolButton, QVBoxLayout,
        QWidget)

from .....project import HeaderDirectory, HeaderFile, HeaderFileVersion


class ControlWidget(QWidget):
    """ This class is a widget that implements the control part of a scanner's
    GUI.
    """

    def __init__(self, tool):
        """ Initialise the widget. """

        super().__init__()

        self._tool = tool
        self._header_directory = None
        self._header_file = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        layout.addLayout(form)

        self._working_version = QComboBox(
                currentTextChanged=self._handle_working_version)
        form.addRow("Working version", self._working_version)

        h_box = QHBoxLayout()
        form.addRow("Source directory", h_box)

        self._source_directory = QLineEdit(
                textChanged=self._configure_parse_button)
        h_box.addWidget(self._source_directory)

        button = QToolButton(
                icon=QApplication.style().standardIcon(
                        QStyle.StandardPixmap.SP_DirIcon),
                clicked=self._handle_browse_source_directory)
        h_box.addWidget(button)

        group_box = QGroupBox("Header Directory")
        layout.addWidget(group_box)

        v_box = QVBoxLayout()
        group_box.setLayout(v_box)

        self._header_directory_form = QFormLayout()
        v_box.addLayout(self._header_directory_form)

        self._header_directory_name = QLabel()
        self._header_directory_form.addRow("Name", self._header_directory_name)

        self._header_suffix = QLineEdit()
        self._header_directory_form.addRow("Suffix", self._header_suffix)

        self._header_filter = QLineEdit()
        self._header_directory_form.addRow("File filter", self._header_filter)

        self._header_parser_args = QLineEdit()
        self._header_directory_form.addRow("Parser arguments",
                self._header_parser_args)

        self._showing_ignored = QCheckBox("Show ignored header files?",
                stateChanged=self._handle_showing_ignored)
        v_box.addWidget(self._showing_ignored)

        grid = QGridLayout()
        v_box.addLayout(grid)

        self._scan_button = QPushButton("Scan",
                clicked=self._handle_scan_header_directory)
        grid.addWidget(self._scan_button, 0, 0)

        self._update_directory_button = QPushButton("Update",
                clicked=self._handle_update_header_directory_properties)
        grid.addWidget(self._update_directory_button, 0, 1)

        self._new_button = QPushButton("New...",
                clicked=self._handle_new_header_directory)
        grid.addWidget(self._new_button, 1, 0)

        self._delete_button = QPushButton("Delete...",
                clicked=self._handle_delete_header_directory)
        grid.addWidget(self._delete_button, 1, 1)

        group_box = QGroupBox("Header File")
        layout.addWidget(group_box)

        v_box = QVBoxLayout()
        group_box.setLayout(v_box)

        self._header_file_form = QFormLayout()
        v_box.addLayout(self._header_file_form)

        self._header_file_name = QLabel()
        self._header_file_form.addRow("Name", self._header_file_name)

        self._ignored = QCheckBox(
                stateChanged=self._handle_header_file_ignored)
        self._header_file_form.addRow("Ignored?", self._ignored)

        self._module = QComboBox()
        self._header_file_form.addRow("Module", self._module)

        grid = QGridLayout()
        v_box.addLayout(grid)

        self._parse_button = QPushButton("Parse",
                clicked=self._handle_parse_header_file)
        grid.addWidget(self._parse_button, 0, 0)

        self._update_file_button = QPushButton("Update",
                clicked=self._handle_update_header_file_properties)
        grid.addWidget(self._update_file_button, 0, 1)

        button = QPushButton("Reset workflow",
                clicked=self._handle_reset_workflow)
        layout.addWidget(button)

        layout.addStretch()

    def module_rename(self, old_name, new_name):
        """ A module has been renamed. """

        index = self._module.findText(old_name)
        self._module.setItemText(index, new_name)

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('source_directory')
        if state is not None:
            self._source_directory.setText(state)

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('source_directory', self._source_directory.text())

    def set_header_file(self, header_file, header_directory, showing_ignored):
        """ Set the current header file. """

        self._header_file = header_file
        self._header_directory = header_directory

        if header_directory is None:
            self._header_directory_name.setText(None)
            self._header_suffix.clear()
            self._header_filter.clear()
            self._header_parser_args.clear()
            self._showing_ignored.setChecked(False)

            enabled = False
        else:
            self._header_directory_name.setText(header_directory.name)
            self._header_suffix.setText(header_directory.inputdirsuffix)
            self._header_filter.setText(header_directory.filefilter)
            self._header_parser_args.setText(header_directory.parserargs)
            self._showing_ignored.setChecked(showing_ignored)

            enabled = True

        self._enable_layout(self._header_directory_form, enabled)
        self._showing_ignored.setEnabled(enabled)
        self._scan_button.setEnabled(enabled)
        self._update_directory_button.setEnabled(enabled)
        self._delete_button.setEnabled(enabled)

        if header_file is None:
            self._header_file_name.setText(None)
            self._module.clear()
            self._ignored.setChecked(False)

            enabled = False
        else:
            self._header_file_name.setText(header_file.name)
            self._ignored.setChecked(header_file.ignored)
            self._set_module_selector(header_file.ignored)

            enabled = True

        self._enable_layout(self._header_file_form, enabled)
        self._configure_parse_button()
        self._update_file_button.setEnabled(enabled)

    def set_project(self):
        """ Set the current project. """

        self.set_header_file(None, None, False)
        self._init_version_selector()

    def set_working_version(self, working_version):
        """ Set the current working version. """

        if working_version is None:
            self._working_version.clear()
            enabled = False
        else:
            self._working_version.setCurrentText(working_version)
            enabled = True

        self._working_version.setEnabled(enabled)

    def version_add_delete(self):
        """ A version has been added or deleted. """

        project = self._tool.shell.project

        if len(project.versions) == 0:
            working_version = None
        else:
            # Try and maintain the current working version.
            working_version = self._working_version.currentText()

            self._init_version_selector()

            if working_version not in project.versions:
                working_version = project.versions[-1]

        self._tool.set_working_version(working_version)

    def version_rename(self, old_name, new_name):
        """ A version has been renamed. """

        index = self._working_version.findText(old_name)
        self._working_version.setItemText(index, new_name)

    def _configure_parse_button(self):
        """ Configure the 'Parse' button. """

        # The button is enabled if there is a source directory and the selected
        # header file is assigned to a module.
        enabled = (self._source_directory.text() != '' and self._header_file is not None and self._header_file.module != '')

        self._parse_button.setEnabled(enabled)

    @staticmethod
    def _enable_layout(layout, enabled):
        """ Enable or disable all the items in a layout. """

        for item_nr in range(layout.count()):
            widget = layout.itemAt(item_nr).widget()
            if widget is not None:
                widget.setEnabled(enabled)

    def _handle_browse_source_directory(self):
        """ Handle the button to browse for a source directory. """

        source_directory = QFileDialog.getExistingDirectory(self,
                "Source Directory", self._source_directory.text())

        if source_directory:
            self._source_directory.setText(source_directory)

    def _handle_delete_header_directory(self):
        """ Handle the button to delete a header directory. """

        button = QMessageBox.question(self, "Delete Header Directory",
                "Are you sure you want to delete this header directory?")

        if button is QMessageBox.StandardButton.Yes:
            self._tool.shell.project.headers.remove(self._header_directory)
            self._tool.header_directory_removed(self._header_directory)
            self._tool.shell.dirty = True

    def _handle_header_file_ignored(self, state):
        """ Handle the checkbox to toggle an ignored header file. """

        self._set_module_selector(bool(state))

    def _handle_new_header_directory(self):
        """ Handle the button to add a header directory. """

        name, ok = QInputDialog.getText(self, "New Header Directory",
                "Descriptive name")

        if ok:
            working_version = self._working_version.currentText()
            header_directory = HeaderDirectory(name=name,
                    scan=[working_version])
            self._tool.shell.project.headers.append(header_directory)
            self._tool.header_directory_added(header_directory,
                    working_version)
            self._tool.shell.dirty = True

    def _handle_parse_header_file(self):
        """ Handle the button to parse a header file. """

        # TODO

    def _handle_reset_workflow(self):
        """ Handle the button to reset the workflow. """

        working_version = self._working_version.currentText()

        for header_directory in self._tool.shell.project.headers:
            if working_version == '':
                header_directory.scan = ['']
            elif working_version not in header_directory.scan:
                header_directory.scan.append(working_version)

            self._tool.header_directory_status(header_directory)

        self._tool.shell.dirty = True

    def _handle_scan_header_directory(self):
        """ Handle the button to scan a header directory. """

        shell = self._tool.shell
        project = shell.project
        header_directory = self._header_directory

        source_directory = os.path.abspath(self._source_directory.text())

        if header_directory.inputdirsuffix != '':
            source_directory = os.path.join(source_directory,
                    header_directory.inputdirsuffix)

        shell.log(f"Scanning header directory '{source_directory}'")

        if header_directory.filefilter != '':
            source_directory = os.path.join(source_directory,
                    header_directory.filefilter)

        # Save the files that were in the directory.
        saved = list(header_directory.content)

        for header_path in glob.iglob(source_directory):
            if not os.path.isfile(header_path):
                continue

            if os.access(header_path, os.R_OK):
                header_file = self._scan_header_file(header_path)

                for saved_header_file in saved:
                    if saved_header_file is header_file:
                        saved.remove(saved_header_file)
                        break
                else:
                    # It's a new header file.
                    header_directory.content.append(header_file)
                    shell.dirty = True

                shell.log(f"Scanned '{header_path}'")
            else:
                shell.log(f"Skipping unreadable header file '{header_path}'")

        # Anything left in the saved list has gone missing or was already
        # missing.
        working_version = self._working_version.currentText()

        for header_file in saved:
            for header_file_version in header_file.versions:
                if header_file_version.version == working_version:
                    header_file.versions.remove(header_file_version)

                    # If there is only one version left then remove the file
                    # itself.
                    if len(header_file.versions) == 0:
                        header_directory.content.remove(header_file)
                        self._remove_from_module(header_file)
                    else:
                        # FIXME: Go through the corresponding SipFile and make
                        # sure that all top-level items have an upper version
                        # set.
                        pass

                    shell.log(f"'{header_file.name}' is no longer in the header directory")

                    self._tool.header_file_removed(header_file)
                    shell.dirty = True
                    break

        # This version no longer needs scanning.
        if working_version in header_directory.scan:
            header_directory.scan.remove(working_version)
            self._tool.header_directory_status(header_directory)
            shell.dirty = True

    def _handle_showing_ignored(self, state):
        """ Handle the checkbox to toggle ignored header files. """

        self._tool.set_header_files_visibility(self._header_directory,
                bool(state))

    def _handle_working_version(self, new_working_version):
        """ Handle the user changing the working version. """

        self._tool.set_working_version(new_working_version)

    def _handle_update_header_directory_properties(self):
        """ Handle the button to update a header directory's properties. """

        self._header_directory.filefilter = self._header_filter.text()
        self._header_directory.inputdirsuffix = self._header_suffix.text()
        self._header_directory.parserargs = self._header_parser_args.text()

        self._tool.shell.dirty = True

    def _handle_update_header_file_properties(self):
        """ Handle the button to update a header file's properties. """

        header_file = self._header_file

        header_file.ignored = self._ignored.isChecked()

        # Make sure the rest is consistent.
        if header_file.ignored:
            header_file.module = ''
            header_file.versions = []
        else:
            header_file.module = self._module.currentText()

            # We may just have un-ignored the header file.
            if len(header_file.versions) == 0:
                header_file.versions.append(
                        HeaderFileVersion(parse=True,
                                version=self._working_version.currentText()))

        self._configure_parse_button()
        self._tool.header_file_status(header_file)
        self._tool.shell.dirty = True

    def _init_version_selector(self):
        """ Initialise the version selector. """

        blocked = self._working_version.blockSignals(True)
        self._working_version.clear()
        self._working_version.addItems(self._tool.shell.project.versions)
        self._working_version.blockSignals(blocked)

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

        with open(name, 'r') as f:
            contents = f.read()
            encoding = f.encoding

        lines = contents.strip().split('\n')
        if len(lines) == 1:
            words = lines[0].split()
            if len(words) == 2 and words[0] == '#include':
                include_name = words[1]
                if include_name.startswith('".') and include_name.endswith('"'):
                    name = os.path.dirname(name) + '/' + include_name[1:-1]

        return contents, name, encoding

    def _remove_from_module(self, header_file):
        """ Handle the removal of a header file from the project. """

        # Find the corresponding .sip file.
        for mod in self.current_project.modules:
            if mod.name == header_file.module:
                for sip_file in mod.content:
                    if sip_file.name == header_file.name:
                        for code in list(sip_file.content):
                            if code.status == 'ignored':
                                # Remove any ignored API elements.
                                sip_file.content.remove(code)
                            else:
                                # Mark any non-ignored API elements so that the
                                # user can decide what to do.
                                code.status = 'removed'

    def _scan_header_file(self, header_path):
        """ Scan a header file and return the header file instance. """

        shell = self._tool.shell

        # Calculate the MD5 signature ignoring any comments.  Note that nested
        # C style comments aren't handled very well.
        m = hashlib.md5()

        src, _, encoding = self._read_header(header_path)

        lnr = 1
        state = 'copy'
        copy = ''
        idx = 0

        for ch in src:
            # Get the previous character.
            if idx > 0:
                prev = src[idx - 1]
            else:
                prev = ''

            idx += 1

            # Line numbers must be accurate.
            if ch == '\n':
                lnr += 1

            # Handle the end of a C style comment.
            if state == 'ccmnt':
                if ch == '/' and prev == '*':
                    state = 'copy'

                continue

            # Handle the end of a C++ style comment.
            if state == 'cppcmnt':
                if ch == '\n':
                    state = 'copy'

                continue

            # We must be in the copy state.

            if ch == '*' and prev == '/':
                # The start of a C style comment.
                state = 'ccmnt'
                continue

            if ch == '/' and prev == '/':
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
        header_directory = self._header_directory
        header_file_name = os.path.basename(header_path)

        for header_file in header_directory.content:
            if header_file.name == header_file_name:
                new_header_file = False
                break
        else:
            # It's a new file.
            header_file = HeaderFile(name=header_file_name)
            new_header_file = True

        # See if we already know about this version.
        working_version = self._working_version.currentText()

        for header_file_version in header_file.versions:
            if header_file_version.version == working_version:
                # See if the version's contents have changed.
                if header_file_version.md5 != md5:
                    header_file_version.md5 = md5
                    header_file_version.parse = True
                    self._tool.header_file_status(header_file)
                    shell.dirty = True

                break
        else:
            # It's a new version.
            header_file_version = HeaderFileVersion(version=working_version,
                    md5=md5)
            header_file.versions.append(header_file_version)

            # Check that the project has versions.
            if len(shell.project.versions) != 0:
                # Find the immediately preceding version if there is one.
                versions_sorted = sorted(header_file.versions,
                        key=lambda v: shell.project.versions.index(v.version))

                prev_md5 = ''
                prev_parse = True
                for hfv in versions_sorted:
                    if hfv.version == working_version:
                        break

                    prev_md5 = hfv.md5
                    prev_parse = hfv.parse

                if prev_md5 == md5:
                    header_file_version.parse = prev_parse
            else:
                # It must be a new file of an unversioned project.
                header_file_version.parse = True

            if new_header_file:
                self._tool.header_file_added(header_file, header_directory,
                        working_version)
            else:
                self._tool.header_file_status(header_file)

            shell.dirty = True

        return header_file

    def _set_module_selector(self, ignored):
        """ Set the module selector for a header file. """

        self._module.clear()

        if not ignored:
            self._module.addItems(
                    sorted([m.name for m in self._tool.shell.project.modules]))

            # See if we have just un-ignored the file.
            module_name = self._header_file.module

            if module_name == '':
                # If there is a module with the same name of the header
                # directory then assume that's where the file is going.
                for module in self._tool.shell.project.modules:
                    if module.name == self._header_directory.name:
                        module_name = module.name
                        break

            self._module.setCurrentText(module_name)
