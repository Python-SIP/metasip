# Copyright (c) 2012 Riverbank Computing Limited.
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


from ..io import IStorageLocation
from ..model import Bool, Instance, List, Str
from ..ui import IView

from .i_dirty import IDirty


class IManagedModel(IDirty):
    """ The IManagedModel interface defines the API of a :term:`managed model`.
    """

    # The :term:`storage location` of the model.  It will be ``None`` if it is
    # not stored.  It will be updated automatically.
    location = Instance(IStorageLocation)

    # The identifier of the model's native format.
    native_format = Str()

    # This explains why the model is invalid.  It will be an empty string if the
    # model is valid.
    invalid_reason = Str()

    # The views that, when active, will cause the appropriate managed model
    # actions to be enabled.
    views = List(IView)
