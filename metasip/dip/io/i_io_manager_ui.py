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


from ..model import Instance, Interface, Str


class IIoManagerUi(Interface):
    """ The IIoManagerUi interface defines the API that implements the various
    storage-independent user interfaces.
    """

    # The text of the title used in the wizard pages asking the user to choose
    # a storage location.
    choose_storage_title = Str()

    # The text of the sub-title used in the wizard page asking the user to
    # choose a readable storage location.
    choose_readable_location_subtitle = Str()

    # The text of the sub-title used in the wizard page asking the user to
    # choose some readable storage.
    choose_readable_storage_subtitle = Str()

    # The text of the title used in the wizard pages asking the user to choose
    # some storage.
    choose_storage_title = Str()

    # The text of the sub-title used in the wizard page asking the user to
    # choose a writeable storage location.
    choose_readable_location_subtitle = Str()

    # The text of the sub-title used in the wizard page asking the user to
    # choose some writeable storage.
    choose_writeable_storage_subtitle = Str()

    # The i/o manager that this is the user interface for.
    io_manager = Instance('.IIoManager')

    def readable_location_wizard_page(self, id=''):
        """ Create a wizard page factory for asking the user to provide a
        readable storage location.

        :param id:
            is the optional identifier of the page.
        :return:
            the wizard page factory.  The page's view will be an implementation
            of :class:`~dip.ui.IStack`.
        """

    def readable_storage_wizard_page(self, bind_to, storage_list=None, id=''):
        """ Create a wizard page factory for asking the user to select from a
        list of readable storage.

        :param bind_to:
            is the attribute of the model containing the selected storage.
        :param storage_list:
            is the optional list of available readable storage.
        :param id:
            is the optional identifier of the page.
        :return:
            the wizard page factory.
        """

    def readable_storage_location(self, title, default_location=None, format='', hints=None, parent=None):
        """ Ask the user to provide a readable storage location.

        :param title:
            is the title to use in any wizards and dialogs.
        :param storage_list:
            is the storage from which the use may choose.  If it is not
            specified then a list of all available readable storage is used.
        :param default_location:
            is the optional default location.
        :param format:
            is the identifier of the optional format.
        :param hints:
            is an optional source of hints.
        :param parent:
            is the optional parent view.
        :return:
            the storage location or ``None`` if the user declined to provide
            one.
        """

    def writeable_location_wizard_page(self, id=''):
        """ Create a wizard page factory for asking the user to provide a
        writeable storage location.

        :param id:
            is the optional identifier of the page.
        :return:
            the wizard page factory.  The page's view will be an implementation
            of :class:`~dip.ui.IStack`.
        """

    def writeable_storage_wizard_page(self, bind_to, storage_list=None, id=''):
        """ Create a wizard page factory for asking the user to select from a
        list of writeable storage.

        :param bind_to:
            is the attribute of the model containing the selected storage.
        :param storage_list:
            is the optional list of available writeable storage.
        :param id:
            is the optional identifier of the page.
        :return:
            the wizard page factory.
        """

    def writeable_storage_location(self, title, default_location=None, format='', hints=None, parent=None):
        """ Ask the user to provide a writeable storage location.

        :param title:
            is the title to use in any wizards and dialogs.
        :param default_location:
            is the optional default location.
        :param format:
            is the identifier of the optional format.
        :param hints:
            is an optional source of hints.
        :param parent:
            is the optional parent view.
        :return:
            the storage location or ``None`` if the user declined to provide
            one.
        """
