# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class Annos:
    """ This class is a mixin for API models that may have SIP annotations. """

    # The annotations.
    annos: str = ''
