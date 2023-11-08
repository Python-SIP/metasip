# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from ..model import Any, get_model_types, Instance, List, MetaModel, Str

from .editor_factory import EditorFactory
from .table_column import TableColumn
from .i_table_editor import ITableEditor
from .toolkits import UIToolkit


class TableEditor(EditorFactory):
    """ The TableEditor class implements a table editor factory for list
    attributes.
    """

    # The list of columns.  If a string is given then it is used as the column
    # heading.
    columns = List(Instance(TableColumn, str))

    # The interface that the view can be adapted to.
    interface = ITableEditor

    # When called this will create the data for a new row in the table.
    row_factory = ITableEditor.row_factory

    # The selection mode.
    selection_mode = ITableEditor.selection_mode

    # The name of the toolkit factory method.
    toolkit_factory = 'table_editor'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        if len(self.columns) == 0:
            raise AttributeError("no columns have been specified")

        # Create complete column specifications.
        columns = []

        # See what we have a list of.
        row_type = view.attribute_type.element_type
        row_factory = self.row_factory

        if not isinstance(row_type, List):
            raise TypeError("the elements of the List must be another List")

        element_type = row_type.element_type

        for col in self.columns:
            column_type = element_type

            if isinstance(col, str):
                column = TableColumn(heading=col)
            else:
                if element_type is None:
                    column_type = col.column_type
                elif col.column_type is not None:
                    raise AttributeError(
                            "'column_type' should not be specified because it "
                            "can be inferred")

                column = TableColumn(editable=col.editable,
                        editor_factory=col.editor_factory, label=col.heading)

            # Make sure there is a column type and an appropriate editor
            # factory.
            if column_type is None or isinstance(column_type, Any):
                column_type = Str()

            column.column_type = column_type

            if column.editor_factory is None:
                column.editor_factory = UIToolkit.editor_factory_for_attribute_type(column_type)

            columns.append(column)

        if row_factory is None:
            if element_type is None:
                element_type = Str()

            element = element_type.get_default_value()
            nr_elements = len(columns)
            row_factory = lambda: [element] * nr_elements

        view.columns = columns
        view.row_factory = row_factory
        view.selection_mode = self.selection_mode

    def set_default_validator(self, view):
        """ Sets a view's default validator.

        :param view:
            is the view.
        """

        from .collection_validator import CollectionValidator

        view.validator = CollectionValidator()


# Register the view factory.
TableEditor.view_factories.append(TableEditor)
