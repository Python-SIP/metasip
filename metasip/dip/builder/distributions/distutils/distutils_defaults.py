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


from ....model import Bool, implements, List, Model, Str

from ... import IDistributionDefaults
from ...types import ModuleName


@implements(IDistributionDefaults)
class DistutilsDefaults(Model):
    """ The DistutilsDefaults class defines the default values used by the
    distutils distribution that can be saved in a project.
    """

    # This is set if any files generated while creating the distribution should
    # be removed afterwards.
    clean = Bool(True, label="Remove generated files",
            tool_tip="Remove any temporary files generated",
            whats_this="If this is checked then any temporary files generated "
                    "while creating the distribution (e.g. setup.py and "
                    "MANIFEST.in) will be automatically removed afterwards.")

    # Set if a .tar.gz format distribution should be created.
    format_gztar = Bool(True, label="gztar",
            tool_tip="Create a .tar.gz format distribution",
            whats_this="When this is checked a .tar.gz format distribution "
                    "will be created.")

    # Set if a .zip format distribution should be created.
    format_zip = Bool(True, label="zip",
            tool_tip="Create a .zip format distribution",
            whats_this="When this is checked a .zip format distribution will "
                    "be created.")

    # The name of the distribution.
    name = Str(required='yes',
            tool_tip="The distribution name",
            whats_this="The name of the distribution.  This is passed as the "
                    "name argument to the generated setup() function.")

    # The contents of the MANIFEST.in file used to specify the files to be
    # included in the distribution.
    manifest_in = Str(
            whats_this="The contents of the MANIFEST.in file that is used to "
                    "specify the files to be included in the distribution.")

    # The list of packages to include in the distribution.
    packages = List(ModuleName())

    # The list of scripts to include in the distribution.
    scripts = List(Str(required='yes'))
