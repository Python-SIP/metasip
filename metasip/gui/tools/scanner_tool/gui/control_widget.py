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


from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
        QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
        QStyle, QToolButton, QVBoxLayout, QWidget)


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

        self._source_directory = QLineEdit()
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

        grid = QGridLayout()
        v_box.addLayout(grid)

        self._scan_button = QPushButton("Scan",
                clicked=self._handle_scan_header_directory)
        grid.addWidget(self._scan_button, 0, 0)

        self._update_directory_button = QPushButton("Update",
                clicked=self._handle_update_header_directory_properties)
        grid.addWidget(self._update_directory_button, 0, 1)

        self._hide_button = QPushButton("Hide ignored",
                clicked=self._handle_hide_ignored_header_files)
        grid.addWidget(self._hide_button, 1, 0)

        self._show_button = QPushButton("Show ignored",
                clicked=self._handle_show_ignored_header_files)
        grid.addWidget(self._show_button, 1, 1)

        self._new_button = QPushButton("New...",
                clicked=self._handle_new_header_directory)
        grid.addWidget(self._new_button, 2, 0)

        self._delete_button = QPushButton("Delete...",
                clicked=self._handle_delete_header_directory)
        grid.addWidget(self._delete_button, 2, 1)

        group_box = QGroupBox("Header File")
        layout.addWidget(group_box)

        v_box = QVBoxLayout()
        group_box.setLayout(v_box)

        self._header_file_form = QFormLayout()
        v_box.addLayout(self._header_file_form)

        self._header_file_name = QLabel()
        self._header_file_form.addRow("Name", self._header_file_name)

        self._module = QComboBox()
        self._header_file_form.addRow("Module", self._module)

        self._ignored = QCheckBox()
        self._header_file_form.addRow("Ignored?", self._ignored)

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

    def set_header_file(self, header_file, header_directory):
        """ Set the current header file. """

        self._header_file = header_file
        self._header_directory = header_directory

        if header_directory is None:
            self._header_directory_name.setText(None)
            self._header_suffix.clear()
            self._header_filter.clear()
            self._header_parser_args.clear()

            enabled = False
        else:
            self._header_directory_name.setText(header_directory.name)
            self._header_suffix.setText(header_directory.inputdirsuffix)
            self._header_filter.setText(header_directory.filefilter)
            self._header_parser_args.setText(header_directory.parserargs)

            enabled = True

        self._enable_layout(self._header_directory_form, enabled)
        self._scan_button.setEnabled(enabled)
        self._update_directory_button.setEnabled(enabled)
        self._hide_button.setEnabled(enabled)
        self._show_button.setEnabled(enabled)
        self._delete_button.setEnabled(enabled)

        if header_file is None:
            self._header_file_name.setText(None)
            self._module.clear()
            self._ignored.setChecked(False)

            enabled = False
        else:
            self._header_file_name.setText(header_file.name)
            self._module.addItems(
                    sorted([m.name for m in self._tool.shell.project.modules]))
            self._module.setCurrentText(header_file.module)
            self._ignored.setChecked(header_file.ignored)

            enabled = True

        self._enable_layout(self._header_file_form, enabled)
        self._parse_button.setEnabled(enabled)
        self._update_file_button.setEnabled(enabled)

    def set_project(self):
        """ Set the current project. """

        self.set_header_file(None, None)
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

    @staticmethod
    def _enable_layout(layout, enabled):
        """ Enable or disable all the items in a layout. """

        for item_nr in range(layout.count()):
            widget = layout.itemAt(item_nr).widget()
            if widget is not None:
                widget.setEnabled(enabled)

    def _handle_browse_source_directory(self):
        """ Handle the button to browse for a source directory. """

        # TODO

    def _handle_delete_header_directory(self):
        """ Handle the button to delete a header directory. """

        # TODO

    def _handle_hide_ignored_header_files(self):
        """ Handle the button to hide ignored header files. """

        # TODO

    def _handle_new_header_directory(self):
        """ Handle the button to add a header directory. """

        # TODO

    def _handle_parse_header_file(self):
        """ Handle the button to parse a header file. """

        # TODO

    def _handle_reset_workflow(self):
        """ Handle the button to reset the workflow. """

        # TODO

    def _handle_scan_header_directory(self):
        """ Handle the button to scan a header directory. """

        # TODO

    def _handle_show_ignored_header_files(self):
        """ Handle the button to show ignored header files. """

        # TODO

    def _handle_working_version(self, new_working_version):
        """ Handle the user changing the working version. """

        self._tool.set_working_version(new_working_version)

    def _handle_update_header_directory_properties(self):
        """ Handle the button to update a header directory's properties. """

        # TODO

    def _handle_update_header_file_properties(self):
        """ Handle the button to update a header file's properties. """

        # TODO

    def _init_version_selector(self):
        """ Initialise the version selector. """

        self._working_version.clear()
        self._working_version.addItems(self._tool.shell.project.versions)
