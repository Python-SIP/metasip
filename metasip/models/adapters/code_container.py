# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from .adapt import adapt
from .base_adapter import BaseAdapter


class CodeContainerAdapter(BaseAdapter):
    """ This is the CodeContainer adapter. """

    def load(self, tag_code_map, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        for subelement in element:
            model_factory = tag_code_map.get(subelement.tag)
            if model_factory is not None:
                model = model_factory()
                adapt(model).load(subelement, project, ui)
                self.model.content.append(model)

    def save_subelements(self, output):
        """ Save the XML subelements. """

        for code in self.model.content:
            adapt(code).save(output)
