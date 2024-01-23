# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from .base_adapter import AttributeType, BaseAdapter


class WorkflowAdapter(BaseAdapter):
    """ This is the Workflow adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'status':   AttributeType.STRING,
    }

    def save_attributes(self, output):
        """ Save the XML attributes. """

        self.save_str('status', output)
