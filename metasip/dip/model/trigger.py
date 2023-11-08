# Copyright (c) 2017 Riverbank Computing Limited.
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


from .change_trigger import get_change_trigger
from .type_factory import TypeFactory


class Trigger(TypeFactory):
    """ The Trigger class represents an asynchronous event.  Attributes of
    this type can be observed and can be set to any value (which is then
    discarded).
    """

    def __init__(self, **metadata):
        """ Initialise the object.

        :param metadata:
            is additional meta-data stored with the type.
        """

        super().__init__(metadata)

    def __set__(self, instance, value):
        """ Reimplemented to pull the trigger. """

        name = self.name
        trigger = get_change_trigger(instance, name)

        if trigger is not None:
            # Avoid a circular import.
            from .attribute_change import AttributeChange

            trigger.change = AttributeChange(model=instance, name=name,
                    new=value, old=None)
