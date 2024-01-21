# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QMessageBox


def question(title, text, detail=None, parent=None):
    """ Display a question to the user and return True if the answer was in the
    affirmative.
    """

    return QMessageBox.question(parent, title, text) is QMessageBox.StandardButton.Yes
