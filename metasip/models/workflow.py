# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class Workflow:
    """ This class is a mixin for APIs that are subject to a workflow. """

    # The multiline comments included in generated .sip files.
    comments: str = ''

    # The workflow status of the API item.  Values are '', 'ignored',
    # 'removed', 'todo', and 'unknown'.
    status: str = ''
