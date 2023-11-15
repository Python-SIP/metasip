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


from ..model import Enum

from .container_factory import ContainerFactory
from .form import Form


class SingleSubviewContainerFactory(ContainerFactory):
    """ The SingleSubviewContainerFactory class is a base class for container
    factories that can only contain a single sub-view.
    """

    # Determines if any sub-views should automatically be placed in a
    # :class:`~dip.ui.Form`.  If it is ``'non-empty'`` then a form will be used
    # if there is at least one sub-view.  If it is ``'always'`` then a form
    # will always be used, even if there are no sub-views.  If it is
    # ``'never'`` then a form will never be used.  Irrespective of the value,
    # if there is only one sub-view and it is a
    # :class:`~dip.ui.ContainerFactory` instance then a form will never be
    # used.
    auto_form = Enum('non-empty', 'always', 'never')

    def __init__(self, *contents, **properties):
        """ Initialise the factory.

        :param contents:
            is the list of the view's contents.  An individual item can either
            be a :class:`~dip.ui.ViewFactory` instance or a string.  Strings
            are are assumed to be the names of attributes within a model.  Such
            names may include one or more periods to specify an
            :term:`attribute path`.
        :param properties:
            are keyword arguments used as property names and values that are
            applied to each toolkit view created by the factory.
        """

        nr_subviews  = len(contents)

        if self.auto_form != 'never':
            # Check for a single sub-view that is a container.
            if not (nr_subviews == 1 and isinstance(contents[0], ContainerFactory)):
                if self.auto_form == 'always' or nr_subviews >= 1:
                    contents = (Form(*contents), )
        elif nr_subviews > 1:
            raise ValueError(
                    "{0} can only contain a single sub-view".format(
                            type(self).__name__))

        super().__init__(*contents, **properties)
