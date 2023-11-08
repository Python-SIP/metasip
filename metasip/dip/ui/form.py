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


from .container_factory import ContainerFactory
from .i_editor import IEditor
from .i_form import IForm


class Form(ContainerFactory):
    """ The Form class arranges its contents as a form. """

    # If there are no explicit contents then automatically populate the form
    # with the model's attribute types.
    auto_populate = True

    # The interface that the view can be adapted to.
    interface = IForm

    # The name of the toolkit factory method.
    toolkit_factory = 'form'

    def create_subviews(self, model, view, root):
        """ Configure the view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        subviews = super().create_subviews(model, view, root)

        labels = []

        for subview in subviews:
            label = None

            if isinstance(subview, IEditor):
                title_policy = subview.title_policy

                if title_policy == 'optional':
                    label = subview.title
                    subview.remove_title()
                elif title_policy != 'embedded':
                    label = subview.title

            labels.append(label)

        view.labels = labels

        return subviews


# Register the view factory.
Form.view_factories.append(Form)
