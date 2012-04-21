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


from dip.model import implements, List, Model, Str
from dip.shell import ITool
from dip.ui import (Action, IAction, Dialog, IDialog, Label, OptionList,
        StorageLocationEditor, VBox)

from .i_schema import ISchema


@implements(ITool)
class SchemaValidatorTool(Model):
    """ The SchemaValidatorTool implements a tool for validating an XML file
    against a schema.
    """

    # The tool's dialog.
    dialog = Dialog(
            VBox(Label('prompt'),
                    OptionList('schema', allow_none=False, options='schemas',
                            sorted=True),
                    StorageLocationEditor('xml_file', required=True)))

    # The prompt to use in the dialog.
    dialog_prompt = Str("Select a schema and enter the location of the file "
            "to validate.")

    # The tool's identifier.
    id = 'metasip.tools.schema_validator'

    # The list of available schemas.
    schemas = List(ISchema)

    # The action.
    validate_action = Action(text="Validate Schema...",
            within='dip.ui.collections.tools')

    @validate_action.triggered
    def validate_action(self):
        """ Invoked when the validate action is triggered. """

        model = dict(prompt=self.dialog_prompt, schema=self.schemas[0],
                schemas=self.schemas, xml_file='')

        view = self.dialog(model,
                window_title=IAction(self.validate_action).plain_text)

        if IDialog(view).execute():
            schema = model['schema']
            xml_file = model['xml_file']
            print("Doing the validation", schema, xml_file)
