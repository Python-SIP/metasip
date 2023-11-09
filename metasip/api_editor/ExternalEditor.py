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


from PyQt6.QtCore import pyqtSignal, QEvent, QFile, QObject, QTextStream
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFileDialog,
        QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout)
from PyQt6.Qsci import QsciLexerCPP, QsciScintilla

from ..dip.settings import SettingsManager
from ..dip.ui import IDialog


class ExternalEditor(QObject):
    """
    This class represents an external editor.
    """

    editDone = pyqtSignal(bool, str)

    def edit(self, text, caption):
        """
        Start the external editor to edit some text.  The editDone() signal is
        emitted when the edit is finshed.  The signal passes a boolean that is
        set if the text has been modified and the text itself.

        text is the text to edit.
        caption is the window caption.
        """
        # Create the editor as a dialog.
        layout = QVBoxLayout()

        top_buttons = QHBoxLayout()

        read_file = QPushButton("Insert file", clicked=self._insert_file)
        top_buttons.addWidget(read_file)

        top_buttons.addStretch()
        layout.addLayout(top_buttons)

        self._editor = ed = QsciScintilla()

        ed.setUtf8(True)
        ed.setAutoIndent(True)
        ed.setIndentationWidth(4)
        ed.setIndentationsUseTabs(False)
        ed.setFolding(QsciScintilla.PlainFoldStyle)
        ed.setEdgeColumn(80)
        ed.setEdgeMode(QsciScintilla.EdgeLine)

        lexer = QsciLexerCPP(ed)
        ed.setLexer(lexer)

        # Use a mono-spaced font.
        s = 0
        while lexer.description(s) != '':
            f = lexer.font(s)
            f.setFamily('Courier')
            lexer.setFont(f)

            s += 1

        layout.addWidget(ed)

        bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        bbox.accepted.connect(self._on_accepted)
        bbox.rejected.connect(self._on_rejected)
        layout.addWidget(bbox)

        self._dialog = dlg = QDialog(windowTitle=caption,
                objectName='metasip.api_editor.external_editor')
        dlg.setLayout(layout)

        # Load the text.
        ed.setText(text)

        SettingsManager.restore(IDialog(dlg).all_views())
        dlg.installEventFilter(self)
        dlg.show()
        dlg.raise_()

    def eventFilter(self, obj, event):
        """ Reimplemented to handle any dialog close events. """

        if event.type() is QEvent.Type.Close:
            self._on_rejected()

        return super().eventFilter(obj, event)

    def _insert_file(self):
        """
        Invoked to insert the contents of a file.
        """
        fn, _ = QFileDialog.getOpenFileName(self._dialog, "Insert File")

        if fn == '':
            return

        f = QFile(fn)

        if not f.open(f.ReadOnly):
            QMessageBox.warning(self._dialog, "Insert File",
                    "Unable to open file")
            return

        ts = QTextStream(f)
        self._editor.insert(ts.readAll())
        del ts

        f.close()

    def _on_accepted(self):
        """ Invoked when the user accepts the edited text. """

        SettingsManager.save(IDialog(self._dialog).all_views())

        self.editDone.emit(True, self._editor.text())
        self._dialog.deleteLater()

    def _on_rejected(self):
        """ Invoked when the user rejects the edited text. """

        SettingsManager.save(IDialog(self._dialog).all_views())

        self.editDone.emit(False, '')
        self._dialog.deleteLater()
