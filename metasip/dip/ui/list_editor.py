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
from .list_column import ListColumn
from .i_list_editor import IListEditor
from .toolkits import UIToolkit


class ListEditor(EditorFactory):
    """ The ListEditor class implements a list editor factory.  An element of
    the list can either be an instance of a model or it can be a simple type.
    If an element is a model instance then each attribute of the model will be
    displayed in a separate column.
    """

    # The list of columns.  If a string is given, and list elements are model
    # instances, then it is assumed to be the name of an attribute in the
    # model.  Otherwise, if a string is given, it is assumed to be the heading
    # of the column.
    columns = List(Instance(ListColumn, str))

    # When called this will create a new element for the list.  If elements are
    # model instances it will default to the model type.  Otherwise, if
    # elements are simple types, then a value based on the default value of the
    # type is used.
    element_factory = IListEditor.element_factory

    # The interface that the view can be adapted to.
    interface = IListEditor

    # The name of the toolkit factory method.
    toolkit_factory = 'list_editor'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        # Create complete column specifications.
        columns = []

        # See what we have a list of.
        attribute_type = view.attribute_type
        element_type = attribute_type.element_type
        element_factory = self.element_factory

        nr_columns = len(self.columns)
        redundant_column_type = False

        if isinstance(element_type, MetaModel):
            model_types = get_model_types(element_type)

            if nr_columns == 0:
                # Create a column for each attribute of the model.
                columns = [ListColumn(name, column_type=atype,
                                heading=self.get_natural_name(name))
                        for name, atype in model_types.items()]

                if len(columns) == 0:
                    raise AttributeError(
                            "unable to infer how many columns the list editor "
                            "should have")

            else:
                # Convert strings to columns.
                for col_nr, col in enumerate(self.columns):
                    if isinstance(col, str):
                        column = ListColumn(col)
                    elif col.column_type is None:
                        column = ListColumn(col.bind_to,
                                editor_factory=col.editor_factory,
                                heading=col.heading)
                    else:
                        redundant_column_type = True
                        break

                    if column.bind_to == '':
                        raise AttributeError(
                                "column {0} is not bound to an attribute".format(col_nr))

                    try:
                        column.column_type = model_types[column.bind_to]
                    except KeyError:
                        raise AttributeError(
                                "'{0}' has no attribute '{1}'".format(
                                        element_type.__name__, column.bind_to))

                    # Make sure there is a heading.
                    if column.heading is None:
                        column.heading = self.get_natural_name(column.bind_to)

                    columns.append(column)

            # Make sure there is an element factory.
            if element_factory is None:
                element_factory = element_type

        else:
            if nr_columns == 0:
                column = ListColumn(column_type=element_type,
                        heading=self.get_natural_name(self.bind_to))
            elif nr_columns == 1:
                column = self.columns[0]

                if column.column_type is None:
                    column = ListColumn(column_type=element_type,
                            editor_factory=column.editor_factory,
                            heading=column.heading)
                elif element_type is not None:
                    redundant_column_type = True
            else:
                raise AttributeError(
                        "too many column definitions for a single column list")

            columns.append(column)

        if redundant_column_type:
            raise AttributeError(
                    "'column_type' should not be specified because it can be "
                    "inferred")

        # Make sure each column has a type and an appropriate editor factory.
        for col in columns:
            if col.column_type is None or isinstance(col.column_type, Any):
                col.column_type = Str()

            if col.editor_factory is None:
                col.editor_factory = UIToolkit.editor_factory_for_attribute_type(
                        col.column_type)

        # Make sure that there is an element factory.  If we haven't got one
        # yet it's because an element is a simple type.
        if element_factory is None:
            element_factory = columns[0].column_type.get_default_value

        view.columns = columns
        view.element_factory = element_factory

    def set_default_validator(self, view):
        """ Sets a view's default validator.

        :param view:
            is the view.
        """

        from .collection_validator import CollectionValidator

        view.validator = CollectionValidator()


# Register the view factory.
ListEditor.view_factories.append(ListEditor)
