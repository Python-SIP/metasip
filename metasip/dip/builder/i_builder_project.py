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


from ..model import Interface, List, Str

from .types import Version

from .i_distribution_defaults import IDistributionDefaults


class IBuilderProject(Interface):
    """ The IBuilderProject interface defines the API of the object that models
    a dip builder project.
    """

    # The application's author.
    author = Str(tool_tip="The application's author",
            whats_this="This is the name of the author of the application.  "
                    "It is typically included with a distribution's meta-data.")

    # The application's author's email address.
    author_email = Str(
            tool_tip="The email address of the application's author",
            whats_this="This is the email address of the author of the "
                    "application.  It is typically included with a "
                    "distribution's meta-data.")

    # The application's description.
    description = Str(required='stripped',
            tool_tip="A short description of the application",
            whats_this="This is a short description of the application.  It "
                    "is typically included with a distribution's meta-data.")

    # The defaults for different distributions.
    distributions_defaults = List(IDistributionDefaults)

    # The text placed at the start of any generated file.
    file_header_text = Str(
            tool_tip="The text included at the start of a generated file",
            whats_this="This text is included at the start of any generated "
                    "file, preceded by appropriate comment characters if "
                    "necessary. This is typically used for copyright and "
                    "licensing information.")

    # The application's home page.
    home_page = Str(tool_tip="The application's home page",
            whats_this="This is the URL that provides more information about "
                    "the application.  It is typically included with a "
                    "distribution's meta-data.")

    # The name of the directory containing the application's source packages.
    package_directory = Str(required='yes',
            tool_tip="The application's source package directory",
            whats_this="This is the name of the directory containing the "
                    "Python packages that make up the application's source "
                    "code.")

    # The version number of the application.  This is expected to be updated
    # when creating a distribution.
    version = Version("0.1", tool_tip="The application version number",
            whats_this="The version number of the application.  No particular "
                    "format or convention is imposed.")

    def create_application(self, py_name, template):
        """ Create an application based on a template.

        :param py_name:
            is the name of the Python file to create.
        :param template:
            is the template which will be an implementation of the
            :class:`~dip.builder.IApplicationTemplate` interface.
        """
