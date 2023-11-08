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


from ...model import implements, Model
from ...ui import OptionList, Stack, WizardPage

from .. import IIoManagerUi

from .location_wizard import LocationWizard


@implements(IIoManagerUi)
class IoManagerUi(Model):
    """ The IoManagerUi class implements the various storage-independent user
    interfaces.
    """

    # FIXME: The newlines.
    # The text of the title used in the wizard pages asking the user to choose
    # a storage location.
    choose_location_title = "Choose a storage location"

    # The text of the sub-title used in the wizard page asking the user to
    # choose a readable storage location.
    choose_readable_location_subtitle = "Enter the storage location where you want to read from.\n"

    # The text of the sub-title used in the wizard page asking the user to
    # choose some readable storage.
    choose_readable_storage_subtitle = "From the list below choose where you want to read from.\n"

    # The text of the title used in the wizard pages asking the user to choose
    # some storage.
    choose_storage_title = "Choose the storage"

    # The text of the sub-title used in the wizard page asking the user to
    # choose a writeable storage location.
    choose_writeable_location_subtitle = "Enter the storage location where you want to write to.\n"

    # The text of the sub-title used in the wizard page asking the user to
    # choose some writeable storage.
    choose_writeable_storage_subtitle = "From the list below choose where you want to write to.\n"

    def readable_location_wizard_page(self, id=''):
        """ Create a wizard page factory for asking the user to provide a
        readable storage location.

        :param id:
            is the optional identifier of the page.
        :return:
            the wizard page factory.  The page's view will be an implementation
            of :class:`~dip.ui.IStack`.
        """

        return self._location_page(id, self.choose_readable_location_subtitle)

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

        return self._storage_page(bind_to, storage_list, id,
                self.choose_readable_storage_subtitle)

    def readable_storage_location(self, title, default_location=None, format='', hints=None, parent=None):
        """ Ask the user to provide a readable storage location.

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

        storage_list = self.io_manager.readable_storage(format)

        # See if a wizard is needed.
        if len(storage_list) == 1:
            # A single storage type will never have implicit locations.
            storage = storage_list[0]

            location = storage.ui.get_read_location(title,
                    default_location=default_location, hints=hints,
                    parent=parent)
        else:
            wizard = LocationWizard(ui=self,
                    storage_list=storage_list, location=default_location,
                    hints=hints, title=title)

            location = wizard.location if wizard.execute(parent) else None

        return location

    def writeable_location_wizard_page(self, id=''):
        """ Create a wizard page factory for asking the user to provide a
        writeable storage location.

        :param id:
            is the optional identifier of the page.
        :return:
            the wizard page factory.  The page's view will be an implementation
            of :class:`~dip.ui.IStack`.
        """

        return self._location_page(id, self.choose_writeable_location_subtitle)

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

        return self._storage_page(bind_to, storage_list, id,
                self.choose_writeable_storage_subtitle)

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

        storage_list = self.io_manager.writeable_storage(format)

        # See if a wizard is needed.
        if len(storage_list) == 1:
            # A single storage type will never have implicit locations.
            storage = storage_list[0]

            location = storage.ui.get_write_location(title,
                    default_location=default_location, hints=hints,
                    parent=parent)
        else:
            wizard = LocationWizard(ui=self, reading=False,
                    storage_list=storage_list, location=default_location,
                    hints=hints, title=title)

            location = wizard.location if wizard.execute(parent) else None

        return location

    def _location_page(self, id, subtitle):
        """ Return an appropriately configured location wizard page factory.
        """

        return WizardPage(Stack(tab_bar='hidden'), auto_form='never', id=id,
                title=self.choose_location_title, subtitle=subtitle)

    def _storage_page(self, bind_to, storage_list, id, subtitle):
        """ Return an appropriately configured storage wizard page factory. """

        if storage_list is None:
            storage_list = []

        return WizardPage(
                OptionList(bind_to, options=storage_list, allow_none=False,
                        sorted=True),
                auto_form='never', id=id, title=self.choose_storage_title,
                subtitle=subtitle)
