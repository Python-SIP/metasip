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


""" This module implements the interface to an external editor. """


from PyQt4.QtCore import pyqtSignal, QFile, QObject, QTextStream
from PyQt4.QtGui import (QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
        QMessageBox, QPushButton, QVBoxLayout)
from PyQt4.Qsci import QsciLexerCPP, QsciScintilla


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

        lexer = QsciLexerCPP(ed)
        ed.setLexer(lexer)

        layout.addWidget(ed)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self._on_accepted)
        bbox.rejected.connect(self._on_rejected)
        layout.addWidget(bbox)

        self._dialog = dlg = QDialog(windowTitle=caption)
        dlg.setLayout(layout)

        # Load the text.
        ed.setText(text)

        dlg.show()
        dlg.raise_()

    def _insert_file(self):
        """
        Invoked to insert the contents of a file.
        """
        fn = QFileDialog.getOpenFileName(self._dialog, "Insert File")

        if fn.isNull():
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
        """
        Invoked when the user accepts the edited text.
        """
        self.editDone.emit(True, self._editor.text())
        self._dialog.deleteLater()

    def _on_rejected(self):
        """
        Invoked when the user rejects the edited text.
        """
        self.editDone.emit(False, '')
        self._dialog.deleteLater()
