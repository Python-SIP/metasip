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


from .editor_factory import EditorFactory
from .i_float_spin_box import IFloatSpinBox


class FloatSpinBox(EditorFactory):
    """ The FloatSpinBox class implements a spin box editor factory for float
    attributes.
    """

    # The interface that the view can be adapted to.
    interface = IFloatSpinBox

    # The maximum value.  ``None`` is interpreted as the toolkit specific
    # default.
    maximum = IFloatSpinBox.maximum

    # The minimum value.  ``None`` is interpreted as the toolkit specific
    # default.
    minimum = IFloatSpinBox.minimum

    # The name of the toolkit factory method.
    toolkit_factory = 'float_spin_box'

    def initialise_view(self, view, model):
        """ Initialise the configuration as a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        maximum = self.maximum
        minimum = self.minimum

        if view.attribute_type is not None:
            metadata = view.attribute_type.metadata

            if maximum is None:
                maximum = metadata.get('maximum')

            if minimum is None:
                minimum = metadata.get('minimum')

        view.maximum = maximum
        view.minimum = maximum


# Register the view factory.
FloatSpinBox.view_factories.append(FloatSpinBox)
