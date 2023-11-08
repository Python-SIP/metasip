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


from ....model import Interface


class IUnicodeDecoder(Interface):
    """ The IUnicodeDecoder interface defines the interface to be implemented
    by models being decoded by the :class:`~dip.io.codecs.UnicodeCodec` codec.
    """

    def set_unicode(self, model, data):
        """ Set the model data from an Python v3 str object or a Python v2
        unicode object.

        :param model:
            is the model.
        :param data:
            the encoded model data.
        :return:
            the decoded model.  This may be the original model populated from
            the storage location, or it may be a different model (of an
            appropriate type) created from the storage location.
        """
