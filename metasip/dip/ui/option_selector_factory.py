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


from ..model import Bool, Enum, Instance, List, Str

from .editor_factory import EditorFactory
from .i_option_selector import IOptionSelector


class OptionSelectorFactory(EditorFactory):
    """ The OptionSelectorFactory class is a base class for editors that allow
    an option to be selected.
    """

    # This is set if ``None`` is allowed as a valid value.  If it is not
    # explicitly set then any corresponding value in the type's meta-data is
    # used.
    allow_none = Bool(None, allow_none=True)

    # The optional option labels.  These are used to visualise the
    # corresponding options.
    labels = List(Str())

    # The options.  If it is a string then it is the name of the attribute in
    # the model where the options can be found.  If an option has no
    # corresponding label then it will be adapted to the
    # :class:`~dip.ui.IDisplay` interface and its :attr:`~dip.ui.IDisplay.name`
    # used (which defaults to its string representation).
    options = Instance(Str(), List())

    # This is set of the options should be sorted.
    sorted = IOptionSelector.sorted

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        labels = self.labels
        options = self.options

        if view.attribute_type is not None:
            if isinstance(view.attribute_type, Enum):
                options = view.attribute_type.members
                labels = [self.get_natural_name(option) for option in options]
            else:
                if isinstance(options, str):
                    options = getattr(view.model, options)

        if options is None:
            options = ()

        view.labels = labels
        view.options = options
        view.sorted = self.sorted

    def set_default_validator(self, view):
        """ Sets a view's default validator.

        :param view:
            is the view.
        """

        # See if a value is required.
        allow_none = self.allow_none
        if allow_none is None:
            attribute_type = view.attribute_type
            if attribute_type is not None:
                allow_none = attribute_type.allow_none
            else:
                allow_none = False

        # See if a validator is required.
        if not allow_none:
            from .option_validator import OptionValidator

            view.validator = OptionValidator()
