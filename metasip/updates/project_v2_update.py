# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from xml.etree import ElementTree

from dip.model import implements, Model

from PyQt4.QtGui import QComboBox

from ..interfaces import IUpdate


@implements(IUpdate)
class ProjectV2Update(Model):
    """ The ProjectV2Update class implements the update of a project from v1 to
    v2.
    """

    # The instruction to the user.
    instruction = "Select the version that was current when the project's header directories were last scanned. Normally this would be the latest version.\n"

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = 2

    def create_view(self, root):
        """ Create the view that will gather the information from the user
        needed to perform the update.

        :param root:
            is the root element of the project.
        :return:
            the view.
        """

        versions = root.get('versions', '').split()
        if len(versions) == 0:
            return None

        versions.reverse()

        view = QComboBox()
        view.addItems(versions)

        return view

    def update(self, root, view):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        :param view:
            is the view returned by create_view().
        """

        # Get the versions and what will become the workflow version.
        if view is None:
            # No versions have been explicitly defined.
            vname = ''
            versions = [vname]
        else:
            vname = view.currentText()
            versions = root.get('versions', '').split()

        # Convert generation numbers to version ranges.
        for elem in root.iter():
            sgen = elem.get('sgen')
            if sgen is None:
                sname = ''
            else:
                sname = versions[int(sgen) - 1]
                del elem.attrib['sgen']

            egen = elem.get('egen')
            if egen is None:
                ename = ''
            else:
                ename = versions[int(egen) - 1]
                del elem.attrib['egen']

            if sname != '' or ename != '':
                elem.set('versions', '{0}-{1}'.format(sname, ename))

        # Create sub-elements for each version.
        versions.reverse()
        for vers in versions:
            attrib = {'name': vers}

            if vers == vname:
                attrib['inputdir'] = root.get('inputdir')

                webxmldir = root.get('webxmldir')
                if webxmldir is not None:
                    attrib['webxmldir'] = webxmldir
            else:
                attrib['inputdir'] = ''

            root.insert(0, ElementTree.Element('Version', attrib))

        root.set('workingversion', vname)

        # Removed old root attributes.
        del root.attrib['inputdir']
        del root.attrib['outputdir']
        del root.attrib['versions']

        try:
            del root.attrib['webxmldir']
        except KeyError:
            pass

        root.set('version', str(self.updates_to))
