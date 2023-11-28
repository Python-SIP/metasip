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

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        layout.addLayout(form)

        self._working_version = QComboBox()
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

        form = QFormLayout()
        v_box.addLayout(form)

        self._header_directory_name = QLabel()
        form.addRow("Name", self._header_directory_name)

        self._header_suffix = QLineEdit()
        form.addRow("Suffix", self._header_suffix)

        self._header_filter = QLineEdit()
        form.addRow("File filter", self._header_filter)

        self._header_parser_args = QLineEdit()
        form.addRow("Parser arguments", self._header_parser_args)

        grid = QGridLayout()
        v_box.addLayout(grid)

        button = QPushButton("Scan",
                clicked=self._handle_scan_header_directory)
        grid.addWidget(button, 0, 0)

        button = QPushButton("Update",
                clicked=self._handle_update_header_directory_properties)
        grid.addWidget(button, 0, 1)

        button = QPushButton("Hide ignored",
                clicked=self._handle_hide_ignored_header_files)
        grid.addWidget(button, 1, 0)

        button = QPushButton("Show ignored",
                clicked=self._handle_show_ignored_header_files)
        grid.addWidget(button, 1, 1)

        group_box = QGroupBox("Header File")
        layout.addWidget(group_box)

        v_box = QVBoxLayout()
        group_box.setLayout(v_box)

        form = QFormLayout()
        v_box.addLayout(form)

        self._header_file_name = QLabel()
        form.addRow("Name", self._header_file_name)

        self._module = QComboBox()
        form.addRow("Module", self._module)

        self._ignored = QCheckBox()
        form.addRow("Ignored?", self._ignored)

        grid = QGridLayout()
        v_box.addLayout(grid)

        button = QPushButton("Parse", clicked=self._handle_parse_header_file)
        grid.addWidget(button, 0, 0)

        button = QPushButton("Update",
                clicked=self._handle_update_header_file_properties)
        grid.addWidget(button, 0, 1)

        h_box = QHBoxLayout()
        layout.addLayout(h_box)

        button = QPushButton("New...",
                clicked=self._handle_new_header_directory)
        h_box.addWidget(button)

        button = QPushButton("Delete...",
                clicked=self._handle_delete_header_directory)
        h_box.addWidget(button)

        button = QPushButton("Reset workflow",
                clicked=self._handle_reset_workflow)
        h_box.addWidget(button)

        layout.addStretch()

    def rename_version(self, old_name, new_name):
        """ Rename a version. """

        index = self._working_version.findText(old_name)
        self._working_version.setItemText(index, new_name)

    def restore_state(self, settings):
        """ Restore the widget's state. """

        state = settings.value('source_directory')
        if state is not None:
            self._source_directory.setText(state)

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('source_directory', self._source_directory.text())

    def set_project(self):
        """ Set the current project. """

        # TODO
        self.update_versions()

    def update_versions(self):
        """ Update the versions. """

        project = self._tool.shell.project

        if len(project.versions) == 0:
            self._working_version.clear()
            working_version = ''
            enabled = False
        else:
            # Try and maintain the current working version.
            working_version = self._working_version.currentText()

            self._working_version.clear()
            self._working_version.addItems(project.versions)

            if working_version not in project.versions:
                working_version = project.versions[-1]

            enabled = True

        self._working_version.setCurrentText(working_version)
        self._working_version.setEnabled(enabled)

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

    def _handle_update_header_directory_properties(self):
        """ Handle the button to update a header directory's properties. """

        # TODO

    def _handle_update_header_file_properties(self):
        """ Handle the button to update a header file's properties. """

        # TODO
