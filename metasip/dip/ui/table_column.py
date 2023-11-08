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


from ..model import Bool, Callable, Instance, Model, Str, TypeFactory


class TableColumn(Model):
    """ The TableColumn class represents the meta-data of a column of a table.
    """

    # The type of the column.  It should not be specified if the type can be
    # inferred from the attribute type.  If it is not specified and no type can
    # be inferred or the type is :class:`~dip.model.Any` then
    # :class:`~dip.model.Str` is used.
    column_type = Instance(TypeFactory)

    # The factory for the view created to edit a value in the column.  It will
    # default to the factory provided by the toolkit for the column type.
    editor_factory = Callable()

    # This is set if the values in the column are editable.
    editable = Bool(True)

    # The heading of the column.
    heading = Str(None, allow_none=True)
