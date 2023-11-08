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


from ...model import implements, MetaInterface, Model, observe

from .. import Publication, IPublicationManager


@implements(IPublicationManager)
class PublicationManager(Model):
    """ The PublicationManager class is the default implementation of the
    :class:`~dip.publish.IPublicationManager` interface.
    """

    @observe('publishers')
    def __publishers_changed(self, change):
        """ Invoked when the list of publishers changes. """

        for publisher in change.old:
            observe('publication', publisher, self.__publication_changed,
                    remove=True)

        for publisher in change.new:
            observe('publication', publisher, self.__publication_changed)

    def __publication_changed(self, change):
        """ Invoked when a publisher's publication changes. """

        publication = change.new

        for subscriber in self.subscribers:
            if subscriber.subscription_type is None:
                model = publication.model
            elif isinstance(subscriber.subscription_type, MetaInterface):
                model = subscriber.subscription_type(publication.model,
                        exception=False)
            elif isinstance(publication.model, subscriber.subscription_type):
                model = publication.model
            else:
                model = None

            if model is not None:
                # Give each subscriber their own copy.
                subscriber.subscription = Publication(model=model,
                        event=publication.event)
