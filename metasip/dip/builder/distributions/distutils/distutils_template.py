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


import os
import subprocess
import sys

from ....model import Bool, Instance, Model, observe, Str, Trigger
from ....ui import (Application, FilesystemLocationEditor, Form, GroupBox,
        HBox, ListColumn, ListEditor, MessageArea, Stretch, TextEditor, VBox,
        IView, Wizard, IWizard, WizardPage)

from ... import IBuilderProject, IDistributionDefaults, DistributionManager


class DistutilsTemplate(Model):
    """ The DistutilsTemplate class contains the data gathered from the user in
    order to create a distutils distribution.
    """

    # The default values initialised from the project.
    defaults = Instance(IDistributionDefaults)

    # Pulled to find packages.
    find_packages = Trigger(tool_tip="Find packages to add to the list",
            whats_this="Find any packages (i.e. any directories containing an "
                    "__init__.py file) starting with the project's package "
                    "directory and add them to the list if they are not "
                    "already present.")

    # The parent view.
    parent = Instance(IView)

    # The project that defines the application.
    project = Instance(IBuilderProject)

    # Set if the values set by the user should be saved as defaults.
    save_as_defaults = Bool(True, label="Save details in the project",
            whats_this="Any values set when creating the distribution will be "
                    "saved in the project to be used as defaults.")

    # The window title to use in dialogs and wizards.
    title = Str()

    # The wizard used to get the input from the user.
    wizard = Wizard(
            WizardPage(
                VBox(
                    Form(
                        'project.version',
                        'defaults.name'
                    ),
                    GroupBox(
                        VBox(
                            'defaults.format_gztar',
                            'defaults.format_zip',
                        ),
                        title="Distribution formats"
                    ),
                    'save_as_defaults',
                    'defaults.clean',
                    Stretch(),
                    MessageArea()
                ),
                title="Configure the distribution",
                subtitle="Enter the details of the distribution to create."
            ),
            WizardPage(
                VBox(
                    ListEditor('defaults.scripts',
                            columns=[ListColumn(
                                    editor_factory=FilesystemLocationEditor())]),
                    Stretch(),
                    MessageArea()
                ),
                title="Configure the scripts",
                subtitle="Enter the names of the scripts to include in the "
                        "distribution."
            ),
            WizardPage(
                VBox(
                    HBox(
                        'find_packages',
                    ),
                    ListEditor('defaults.packages')
                ),
                title="Configure the packages",
                subtitle="Enter the names of the packages to include in the "
                        "distribution."
            ),
            WizardPage(
                TextEditor('defaults.manifest_in'),
                title="Configure the manifest",
                subtitle="Enter the contents of the MANIFEST.in file."
            )
        )

    def populate(self):
        """ Populate the distutils template with input from the user.

        :return:
            ``True`` if the template is populated.
        """

        wizard = self.wizard(self, parent=self.parent, title=self.title)

        # "Find packages" needs the model to be up to date.
        wizard.controller.auto_update_model = True

        if not wizard.execute():
            return False

        # Update the project defaults if requested.
        if self.save_as_defaults:
            DistributionManager.instance().distribution_manager.update_defaults(self.project, self.defaults)

        return True

    def create_distribution(self):
        """ Create a distribution for the application.

        :return:
            ``True`` if the distribution was created.  ``False`` will be
            returned if the user decided not to proceed.  An exception will be
            raised if there was an error.
        """

        # Create the temporary files.
        setup_py = self._create_file('setup.py')
        if setup_py is None:
            return False

        if self.defaults.manifest_in != '':
            manifest_in = self._create_file('MANIFEST.in')
            if manifest_in is None:
                self._tidy_up()
                return False

        # Populate setup.py.
        self._add_header_text(setup_py, '#')

        setup_py.write("""from distutils.core import setup

setup(
    name='{name}',
    version='{version}',
""".format(name=self.defaults.name, version=self.project.version))

        if self.project.description != '':
            setup_py.write(
                    "    description='{0}',\n".format(
                            self.project.description))

        if self.project.author != '':
            setup_py.write("    author='{0}',\n".format(self.project.author))

        if self.project.author_email != '':
            setup_py.write(
                    "    author_email='{0}',\n".format(
                            self.project.author_email))

        if self.project.home_page != '':
            setup_py.write("    url='{0}',\n".format(self.project.home_page))

        if len(self.defaults.scripts) > 0:
            script_list = ", ".join(
                    ["'{0}'".format(s) for s in self.defaults.scripts])
            setup_py.write("    scripts=[{0}],\n".format(script_list))

        if len(self.defaults.packages) > 0:
            package_list = ", ".join(
                    ["'{0}'".format(p) for p in self.defaults.packages])
            setup_py.write("    packages=[{0}],\n".format(package_list))

        setup_py.write(")\n")

        setup_py.close()

        # Populate MANIFEST.in.
        if self.defaults.manifest_in != '':
            manifest_in.write(self.defaults.manifest_in)
            manifest_in.close()

        # Run distutils.
        args = [sys.executable, 'setup.py', 'sdist']
        formats = []

        if self.defaults.format_gztar:
            formats.append('gztar')

        if self.defaults.format_zip:
            formats.append('zip')

        if len(formats) != 0:
            args.append('--formats={0}'.format(','.join(formats)))

        if self.defaults.manifest_in != '':
            args.append('--force-manifest')

        subprocess.check_call(args)

        self._tidy_up()

        return True

    @observe('find_packages')
    def __find_packages_changed(self):
        """ Invoked to find any packages and add them to the list of packages.
        """

        # Check that the project defines a package directory.
        root = self.project.package_directory
        if root == '':
            Application.warning(self.title,
                    "The project doesn't define a package directory to search "
                    "from.",
                    self.parent)
        elif os.path.isdir(root):
            # Get the package names.
            cwd = os.getcwd()
            os.chdir(root)

            root_package = os.path.basename(root)
            packages = []

            for dirpath, dirs, files in os.walk('.'):
                if '__init__.py' in files:
                    module_names = dirpath.split(os.sep)
                    module_names[0] = root_package

                    packages.append('.'.join(module_names))
                else:
                    del dirs[:]

            os.chdir(cwd)

            # Update the model with the new packages.
            if len(packages) == 0:
                Application.warning(self.title,
                        "No packages were found.", self.parent)
            else:
                packages = [p for p in packages
                        if p not in self.defaults.packages]

                if len(packages) == 0:
                    Application.information(self.title,
                            "No new packages were found.", self.parent)
                else:
                    self.defaults.packages.extend(packages)
        else:
            Application.warning(self.title,
                    "{0} is not a directory.".format(root),
                    self.parent)

    def _create_file(self, name):
        """ Create a file with the given name.  If it already exists then only
        overwrite it if with the user's agreement.
        """

        if os.path.exists(name):
            answer = Application.question(self.title,
                    "The file {0} already exists and will be overwritten when "
                    "the distribution is created. Do you wish to "
                    "continue?".format(name),
                    self.parent)

            if answer != 'yes':
                return None

        return open(name, 'w', encoding='utf8')

    def _tidy_up(self):
        """ Remove any temporary files if requested by the user. """

        if self.defaults.clean:
            try:
                os.remove('setup.py')
            except:
                pass

            if self.defaults.manifest_in != '':
                try:
                    os.remove('MANIFEST.in')
                except:
                    pass

    def _add_header_text(self, file, comment=''):
        """ Add any header text to a file. """

        if self.project.file_header_text != '':
            for line in self.project.file_header_text.split('\n'):
                if comment != '':
                    file.write(comment + " ")

                file.write(line + "\n")

            file.write("\n")
