# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QMessageBox


def warning(title, text, detail=None, parent=None):
    """ Display a warning message to the user. """

    message_box = QMessageBox(QMessageBox.Icon.Warning, title, text,
            parent=parent)

    if detail:
        message_box.setDetailedText(detail)

    message_box.exec()
