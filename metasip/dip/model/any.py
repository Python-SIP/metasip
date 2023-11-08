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


from .value_type_factory import ValueTypeFactory


class Any(ValueTypeFactory):
    """ The Any class encapsulates any Python object. """

    def __init__(self, default=None, allow_none=True, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param default:
            the default value of the object.
        :param allow_none:
            ``True`` if ``None`` is a valid value.  The default is ``True``.
        :param allow_rebind:
            ``True`` if the attribute can be re-bound after the model has been
            instantiated.
        :param getter:
            is the optional attribute getter.
        :param setter:
            is the optional attribute setter.
        :param \*\*metadata:
            is additional meta-data stored with the type.
        """

        super().__init__(default, allow_none, allow_rebind, getter, setter,
                metadata)
