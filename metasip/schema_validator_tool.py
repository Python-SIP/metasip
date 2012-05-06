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


import os
import sys

from dip.io import IFilterHints
from dip.model import implements, List, Model, Str
from dip.shell import ITool
from dip.ui import (Action, IAction, Application, Dialog, IDialog,
        DialogController, IEditor, Label, OptionList, StorageLocationEditor,
        IStorageLocationEditor, VBox)

from .interfaces import ISchema


class _DialogController(DialogController):
    """ An internal class that implements the controller for the schema
    validator dialog.
    """

    def validate(self):
        """ Reimplemented to change the configuration of the dialog. """

        # Configure the storage location editor according to the current
        # schema.
        ixmlfileeditor = IStorageLocationEditor(self.xml_file_editor)
        schema = IEditor(self.schema_editor).value

        if schema is None:
            ixmlfileeditor.enabled = False
        else:
            ixmlfileeditor.enabled = True

            ifilterhints = IFilterHints(schema, exception=False)
            if ifilterhints is not None:
                ixmlfileeditor.filter_hints = ifilterhints.filter

        # Do the normal validation.
        super().validate()


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
                    StorageLocationEditor('xml_file', required=True)),
            controller_factory=_DialogController)

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

        window_title=IAction(self.validate_action).plain_text

        model = dict(prompt=self.dialog_prompt, schema=None,
                schemas=self.schemas, xml_file='')

        view = self.dialog(model, window_title=window_title)

        if IDialog(view).execute():
            from .schema_validator import (SchemaValidator,
                    SchemaValidationException)

            schema = model['schema']
            xml_file = model['xml_file']

            schema_file = os.path.join(os.path.dirname(os.path.abspath(sys.modules[type(schema).__module__].__file__)), ISchema(schema).schema_file)

            validator = SchemaValidator()

            try:
                validator.validate(schema_file, xml_file)
            except SchemaValidationException as e:
                Application.warning(window_title, str(e), self.shell,
                        "File: {0}\nLine: {1}\nColumn: {2}".format(e.filename,
                                e.line, e.column))
                return
            except IOError as e:
                Application.warning(window_title,
                        "There was an i/o error validating the file.",
                        self.shell, str(e))
                return

            Application.information(window_title,
                    "{0} is valid.".format(xml_file), self.shell)
