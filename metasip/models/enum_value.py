# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .annos import Annos
from .tagged import Tagged
from .workflow import Workflow


@dataclass
class EnumValue(Annos, Tagged, Workflow):
    """ This class implements an enum value. """

    # The name of the value.
    name: str = ''
