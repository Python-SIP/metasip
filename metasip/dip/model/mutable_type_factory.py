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


from .collection_type_factory import CollectionTypeFactory


class MutableTypeFactory(CollectionTypeFactory):
    """ The MutableTypeFactory class is a base class for all mutable types. """

    def bind(self, model, value, rebind=False):
        """ This is called when a model attribute is being bound or rebound.

        :param model:
            is the model.
        :param value:
            is the attribute's new value.
        :param rebind:
            is set if the attribute already has a value.
        """

        # Mutable types know the model they are contained by.

        if rebind:
            old_value = getattr(model, self.name)
            old_value._dip_model = None

        value._dip_model = model
