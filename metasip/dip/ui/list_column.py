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


from ..model import Str

from .table_column import TableColumn


class ListColumn(TableColumn):
    """ The ListColumn class represents the meta-data of the column of a list.
    """

    # The name of attribute that the column is bound to.  It will be empty if
    # a list element is a simple type rather than a model instance.
    bind_to = Str()

    def __init__(self, bind_to=''):
        """ Initialise the column.

        :param bind_to:
            the name of the atribute that the column is bound to.  It should
            not be specified if a row is a list rather than a model.
        """

        super().__init__()

        # It's more natural to allow this as a positional argument.
        self.bind_to = bind_to
