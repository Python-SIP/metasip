# Copyright (c) 2011 Riverbank Computing Limited.
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


from ..model import Instance, Tuple

from .i_container import IContainer
from .i_view import IView
from .stretch import Stretch


class IBox(IContainer):
    """ The IBox interface defines the API to be implemented (typically
    using adaptation) by a :term:`view` that can contain a mixture of sub-views
    and :class:`~dip.ui.Stretch` instances.
    """

    # The contained sub-views.
    views = Tuple(Instance(IView, Stretch))
