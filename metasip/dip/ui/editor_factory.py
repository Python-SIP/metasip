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


from ..model import get_attribute_type, resolve_attribute_path, Str

from .i_editor import IEditor
from .view_factory import ViewFactory


class EditorFactory(ViewFactory):
    """ The EditorFactory class is a factory for views that implement the
    :class:`~dip.ui.IEditor` interface.  The :attr:`~dip.ui.IEditor.validator`,
    :attr:`~dip.ui.IView.status_tip`, :attr:`~dip.ui.IView.title`,
    :attr:`~dip.ui.IView.tool_tip` and :attr:`~dip.ui.IView.whats_this`
    attributes will default to any values defined in the type's meta-data.
    """

    # The name of the attribute that the editor is bound to.  This may be an
    # :term:`attribute path`.
    bind_to = Str()

    # This is set if the editor is read-only.
    read_only = IEditor.read_only

    # This is set if the editor's value should be remembered between sessions.
    remember = IEditor.remember

    # The editor's validator.
    validator = IEditor.validator

    def __init__(self, bind_to='', **properties):
        """ Initialise the factory.

        :param bind_to:
            the name of the attribute that the editor is bound to.  It should
            only be an empty string if the factory is being used to create a
            delegate.
        :param properties:
            are keyword arguments used as property names and values that are
            applied to the editor.
        """

        super().__init__(**properties)

        # It's more natural to allow this as a positional argument.
        self.bind_to = bind_to

    def finalise_view(self, view):
        """ Finalise the configuration of a view instance.

        :param view:
            is the view.
        """

        # Allow a sub-class to provide a default validator if none has been
        # supplied.  We don't use the default value of an attribute because we
        # want the fully configured view first.
        if view.validator is None:
            self.set_default_validator(view)

        if view.validator is not None:
            view.validator.configure(view)

        super().finalise_view(view)

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.read_only = self.read_only
        view.remember = self.remember

        if self.bind_to != '':
            # Get the bound attribute and model.
            name, submodel = resolve_attribute_path(self.bind_to, model)

            view.attribute_name = name
            view.attribute_type = get_attribute_type(submodel, name)
            view.model = submodel

            # Allow the bound attribute's meta-data to provide some values if
            # they haven't already been set.
            metadata = view.attribute_type.metadata

            if view.title == '':
                title = metadata.get('title', '')
                if title == '':
                    title = self.get_natural_name(name)

                if title != '':
                    view.title = title

            if view.status_tip == '':
                view.status_tip = metadata.get('status_tip', '')

            if view.tool_tip == '':
                view.tool_tip = metadata.get('tool_tip', '')

            if view.whats_this == '':
                view.whats_this = metadata.get('whats_this', '')

            if view.validator is None:
                view.validator = metadata.get('validator')

    def set_default_validator(self, view):
        """ Sets a view's default validator.  This implementation does nothing.

        :param view:
            is the view.
        """

    @ViewFactory.id.default
    def id(self):
        """ The default value of id is the name of the attribute that the
        editor is bound to.  The identifier only needs to be explicitly set if
        there is more than one editor in the same view that is bound to the
        same attribute and the editor is the target of a linked editor.
        """

        return self.bind_to
