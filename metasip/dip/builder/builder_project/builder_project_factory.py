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


from ...model import adapt, Adapter, implements, Model
from ...shell import IManagedModel
from ...ui import IDisplay

from .. import IBuilderProject


@implements(IDisplay)
class BuilderProjectFactory(Model):
    """ The BuilderProjectFactory class is a factory for the default
    implementation of the IBuilderProject interface.
    """

    # The name of the type of the object.
    name = "DIP builder project"

    def __call__(self):
        """ Invoked by the model manager to create the model instance. """

        from .builder_project import BuilderProject

        return BuilderProject()


@adapt(IBuilderProject, to=IManagedModel)
class IBuilderProjectIManagedModelAdapter(Adapter):
    """ Adapt IBuilderProject to IManagedModel. """

    # The native format.
    native_format = 'dip.builder.formats.project'
