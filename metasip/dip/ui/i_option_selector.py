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


from ..model import Bool, Str, Tuple

from .i_editor import IEditor


class IOptionSelector(IEditor):
    """ The IOptionalSelector interface defines the API to be implemented by an
    editor that allows one of a number of options to be selected.
    """

    # The optional option labels.  These are used to visualise the
    # corresponding options.
    labels = Tuple(Str())

    # The options.  If an option has no corresponding label then it will be
    # adapted to the :class:`~dip.ui.IDisplay` interface and its
    # :attr:`~dip.ui.IDisplay.name` used (which will default to its string
    # representation).
    options = Tuple()

    # This is set of the options should be sorted.
    sorted = Bool(False)
