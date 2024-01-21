# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .annos import Annos
from .tagged import Tagged
from .workflow import Workflow


@dataclass
class Code(Annos, Tagged, Workflow):
    """ This class implements APIs that can be annotated, are subject to
    version control and a workflow.
    """
