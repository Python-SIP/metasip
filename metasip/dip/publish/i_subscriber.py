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


from ..model import Instance, Interface

from .i_publication import IPublication


class ISubscriber(Interface):
    """ The ISubscriber interface defines the API to be implemented by an
    object that subscribes to the publication of events related to a
    :term:`model` by other objects that implement the
    :class:`~dip.publish.IPublisher` interface.
    """

    # The publication we have subscribed to.
    subscription = Instance(IPublication)

    # The type of model that the subscriber is interested in.  If it is
    # ``None`` then publications related to all types of model will be
    # subscribed to.
    subscription_type = Instance(type)
