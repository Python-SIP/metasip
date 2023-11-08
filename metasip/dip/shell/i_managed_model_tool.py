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


from ..model import Bool, Enum, Instance, List

from .i_managed_model import IManagedModel
from .i_model_manager_tool import IModelManagerTool
from .i_tool import ITool


class IManagedModelTool(ITool):
    """ The IManagedModelTool interface defines the API for a :term:`tool` that
    handles one or more :term:`managed models<managed model>`.
    """

    # The model manager that is managing this tool's models.
    manager = Instance(IModelManagerTool)

    # This defines how the tool handles multiple models.  ``many`` means the
    # tool can handle any number of models at a time.  ``one`` means that the
    # tool handles exactly one model at a time - this means a new model will be
    # created automatically without user intervention.  ``zero_or_one`` means
    # that the tool handles no more than one model at time.
    model_policy = Enum('many', 'one', 'zero_or_one')

    # The managed models the tool is handling.
    models = List(IManagedModel)

    # This is set if the tool is suitable for handling a model in the context
    # of a "New" operation.
    new_tool = Bool(True)

    # This is set if the tool is suitable for handling a model in the context
    # of an "Open" operation.
    open_tool = Bool(True)

    def handles(self, model):
        """ Check if the tool can handle a particular model.

        :param model:
            is the model.
        :return:
            ``True`` if a tool can handle the model.
        """
