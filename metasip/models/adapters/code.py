# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..annos import Annos
from ..tagged import Tagged
from ..workflow import Workflow

from .adapt import adapt
from .base_adapter import BaseAdapter


class CodeAdapter(BaseAdapter):
    """ This is the Code adapter. """

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        adapt(self.model, Annos).load(element, project, ui)
        adapt(self.model, Tagged).load(element, project, ui)
        adapt(self.model, Workflow).load(element, project, ui)

    def save_attributes(self, output):
        """ Save the XML attributes. """

        # The order is to match older versions.
        adapt(self.model, Annos).save_attributes(output)
        adapt(self.model, Workflow).save_attributes(output)
        adapt(self.model, Tagged).save_attributes(output)

    def save_subelements(self, output):
        """ Save the XML subelements. """

        adapt(self.model, Annos).save_subelements(output)
        adapt(self.model, Tagged).save_subelements(output)
        adapt(self.model, Workflow).save_subelements(output)
