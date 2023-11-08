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


from ..model import Any, Interface, Str


class IPublication(Interface):
    """ The IPublication interface defines the API to be implemented by a model
    that represents an event related to a published model.
    """

    # The event related to the model.  The following events are considered to
    # be well known.
    #
    # 'dip.events.opened'
    #   occurs once just after the model has been opened or created.
    # 'dip.events.closed'
    #   occurs once just before the model is closed.
    # 'dip.event.active'
    #   occurs whenever the model becomes active.
    # 'dip.events.inactive'
    #   occurs whenever the model becomes inactive.
    event = Str()

    # The model being published.
    model = Any()
