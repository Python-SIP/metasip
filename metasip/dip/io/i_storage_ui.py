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


from ..model import Instance, Interface


class IStorageUi(Interface):
    """ The IStorageUi interface defines the API that implements the various
    storage specific user interfaces.
    """

    # The storage that this is the user interface for.
    storage = Instance('.IStorage')

    def read_browser(self, default_location=None, hints=None):
        """ Create a view that allows the user to browse storage and select a
        read location.

        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :return:
            the view which must implement, or can be adapted to,
            :class:`~dip.io.IStorageBrowser`.
        """

    def get_read_location(self, title, default_location=None, hints=None, parent=None):
        """ Get a new location from the user to read from.

        :param title:
            is the title, typically used as the title of a dialog.
        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :param parent:
            is the optional parent view.
        :return:
            the new location or ``None`` if the user cancelled.
        """

    def write_browser(self, default_location=None, hints=None):
        """ Create a view that allows the user to browse storage and select a
        write location.

        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :return:
            the view which must implement, or can be adapted to,
            :class:`~dip.io.IStorageBrowser`.
        """

    def get_write_location(self, title, default_location=None, hints=None, parent=None):
        """ Get a new location from the user to write to.

        :param title:
            is the title, typically used as the title of a dialog.
        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :param parent:
            is the optional parent view.
        :return:
            the new location or ``None`` if the user cancelled.
        """
