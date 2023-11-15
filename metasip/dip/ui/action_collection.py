# Copyright (c) 2023 Riverbank Computing Limited.
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


from ..model import implements, Model, ValidationTypeError, ValueTypeFactory

from .i_action_collection import IActionCollection


class ActionCollection(ValueTypeFactory):
    """ The ActionCollection class encapsulates an instance of an
    implementation of :class:`~dip.ui.IActionCollection`.  This can be used
    either to define an :term:`attribute type` in a model or to create a
    factory that then creates action collections.
    """

    def __init__(self, *action_ids, id=None, text='', within='', **metadata):
        """ Initialise the object.

        :param action_ids:
            is the list of the identifiers of actions contained in the
            collection.
        :param id:
            is the collection's identifier.  If this is not specified it will
            default to the name of the attribute if an attribute type is being
            defined.
        :param text:
            is the optional text of the collection.  If this is specified then
            the toolkit may place the actions in a hierarchy (e.g. a sub-menu).
        :param within:
            is the identifier of an optional action collection that this
            collection will be placed within.
        :param metadata:
            is additional meta-data stored with the type.
        """

        self.action_ids = action_ids
        self.id = id
        self.text = text
        self.within = within

        super().__init__(None, True, True, None, None, metadata)

    def __call__(self, model):
        """ Create the action collection.  This behaviour is similar to a view
        factory.

        :param model:
            is the model.
        :return:
            the action collection.
        """

        return self._create_action_collection('')

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(*self.action_ids, id=self.id, text=self.text,
                within=self.within, **self.metadata)

    def get_default_value(self):
        """ Get the type's default value.  This will always be a new
        implementation of IActionCollection.
        """

        return self._create_action_collection(self.name)

    def _create_action_collection(self, default_id):
        """ Create an action collection configured from this factory. """

        action_collection = ActionCollectionImpl()

        action_collection.actions.extend(self.action_ids)

        action_collection.id = self.id if self.id is not None else default_id

        action_collection.text = self.text
        action_collection.within = self.within

        action_collection.configure(self.metadata)

        return action_collection

    def validate(self, value):
        """ Validate an instance according to the constraints.  An exception
        is raised if the instance is invalid.

        :param value:
            the instance to validate.
        :return:
            the validated instance.
        """

        if value is not None:
            if IActionCollection(value, exception=False) is None:
                raise ValidationTypeError(type(self), type, value)

        return value

    @classmethod
    def different(cls, value1, value2):
        """ Reimplemented to compare two instances to see if they are
        different.

        :param value1:
            is the first value.
        :param value2:
            is the second value.
        :return:
            ``True`` if the values are different.
        """

        return value1 is not value2


@implements(IActionCollection)
class ActionCollectionImpl(Model):
    """ The implementation of the IActionCollection interface. """

    def configure(self, properties):
        """ Configure the object using a mapping of toolkit specific property
        names and values.

        :param properties:
            is the mapping of the properties.
        """

        # This doesn't have a toolkit implementation so just treat the
        # meta-data as attributes.
        for key, value in properties.items():
            setattr(self, key, value)
