# Copyright (c) 2023 Riverbank Computing Limited.
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

from ..dip.model import implements, Model

from PyQt6.QtWidgets import QComboBox

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

        # Get the versions.
        versions = root.get('versions', '').split()
        working_version = '' if view is None else view.currentText()

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

        # Get the HeaderFile elements.
        header_files = root.findall('HeaderDirectory/HeaderFile')

        # Replace ModuleHeaderFile elements with SipFile Elements.
        for module in root.iterfind('Module'):
            module_name = module.get('name')
            module_header_files = module.findall('ModuleHeaderFile')

            for mhf in module_header_files:
                # Get the id and then remove it.
                hf_id = mhf.get('id')
                module.remove(mhf)

                # Find the header file.
                for hf in header_files:
                    if hf.get('id') == hf_id:
                        # Create the SipFile element.
                        sf = ElementTree.SubElement(module, 'SipFile',
                                name=hf.get('name'))

                        # Copy all the HeaderFile sub-elements to the SipFile.
                        for elem in hf:
                            sf.append(elem)

                        # Remember the name of the module that the header file
                        # is assigned to.
                        hf.set('module', module_name)

        # Create a HeaderFileVersion for every HeaderFile that has been
        # assigned to a module.
        for header_directory in root.iterfind('HeaderDirectory'):
            for hf in header_directory:
                # This is no longer needed.
                del hf.attrib['id']

                status = hf.get('status')
                if status is None:
                    is_ignored = False
                else:
                    is_ignored = (status == 'ignored')
                    del hf.attrib['status']

                # If the version of the header file has an upper bound then (if
                # it is not being ignored) assume that this is the version the
                # rest of the data refers to - otherwise use the working
                # version.  Note that we are ignoring the (unlikely) case where
                # the working version is prior to the starting version of a
                # header file.
                hf_versions = hf.get('versions')

                if hf_versions is not None:
                    del hf.attrib['versions']

                if hf_versions is None or hf_versions.endswith('-'):
                    use_version = working_version
                elif is_ignored:
                    # The header file is being ignored and is no longer present
                    # so just discard it.
                    header_directory.remove(hf)
                    continue
                else:
                    upper_version = hf_versions.split('-')[1]
                    use_version = versions[versions.index(upper_version) - 1]

                # Remove any existing elements as they will have been copied to
                # a SipFile element.
                for elem in list(hf):
                    hf.remove(elem)

                hfv = ElementTree.SubElement(hf, 'HeaderFileVersion',
                        md5=hf.get('md5'), version=use_version)
                del hf.attrib['md5']

                if hf.get('parse', '') == 'needed':
                    hfv.set('parse', '1')
                    del hf.attrib['parse']

                if is_ignored:
                    hf.set('ignored', '1')

        # Removed old root attributes.
        del root.attrib['inputdir']
        del root.attrib['outputdir']

        try:
            del root.attrib['webxmldir']
        except KeyError:
            pass

        root.set('version', str(self.updates_to))
