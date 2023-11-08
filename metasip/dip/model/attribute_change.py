# Copyright (c) 2010 Riverbank Computing Limited.
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


from .any import Any
from .instance import Instance
from .model import Model
from .str import Str


class AttributeChange(Model):
    """ The AttributeChange class contains the information that describes an
    observable change to a typed attribute.  An instance is passed to the
    observer defined using :func:`~dip.model.observe`.
    """

    # The model containing the changed attribute.
    model = Instance(Model)

    # The name of the changed attribute.
    name = Str()

    # The new value of the attribute.  If the type of the attribute is a
    # collection, e.g. a list, then the value is a collection of the items that
    # have been added.  Note that an item may appear in both in both ``new``
    # and ``old``.
    new = Any()

    # The old value of the attribute.  If the type of the attribute is a
    # collection, e.g. a list, then the value is a collection of the items that
    # have been removed.  Note that an item may appear in both in both ``new``
    # and ``old``.
    old = Any()
