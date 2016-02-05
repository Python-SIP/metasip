# Copyright (c) 2016 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import os
import hashlib
import fnmatch
from xml.sax import saxutils

from dip.model import implements, Instance, Model, Str
from dip.shell import IDirty

from .logger import Logger
from .interfaces.project import (ProjectVersion, IArgument, IClass,
        IConstructor, IDestructor, IEnum, IEnumValue, IFunction,
        IHeaderDirectory, IHeaderFile, IHeaderFileVersion, IManualCode,
        IMethod, IModule, INamespace, IOpaqueClass, IOperatorCast,
        IOperatorFunction, IOperatorMethod, IProject, ISipFile, ITagged,
        ITypedef, IVariable, IVersionRange)


class Annotations(Model):
    """ This class is a base class for any project item that has annotations.
    """

    def sipAnnos(self):
        """ Return the annotations suitable for writing to a SIP file.

        :return:
            the annotations.
        """

        return ' /{0}/'.format(self.annos) if self.annos != '' else ''

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = []

        if self.annos != '':
            xml.append('annos="{0}"'.format(escape(self.annos)))

        return xml


@implements(IVersionRange)
class VersionRange(Model):
    """ This class implements a range of versions. """


@implements(ITagged)
class TaggedItem(Model):
    """ This class is a base class for all project elements that is subject to
    workflow or tags.
    """

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = []

        if self.status != '':
            xml.append('status="{0}"'.format(self.status))

        if len(self.versions) != 0:
            ranges = [version_range(r).replace(' ', '') for r in self.versions]
            xml.append('versions="{0}"'.format(' '.join(ranges)))

        if len(self.platforms) != 0:
            xml.append('platforms="{0}"'.format(' '.join(self.platforms)))

        if len(self.features) != 0:
            xml.append('features="{0}"'.format(' '.join(self.features)))

        return xml

    def get_project(self):
        """ Return the project instance. """

        sf = self
        while not hasattr(sf, 'project'):
            sf = sf.container

        return sf.project

    def expand_type(self, typ, name="", ignore_namespaces=False):
        """
        Return the full type for a name.

        typ is the type.
        name is the optional name.
        ignore_namespaces is True if any ignored namespaces should be ignored.
        """
        # Handle the trivial case.
        if not typ:
            return ""

        if ignore_namespaces:
            const = 'const '
            if typ.startswith(const):
                typ = typ[len(const):]
            else:
                const = ''

            typ = const + self.ignore_namespaces(typ)

        # SIP can't handle every C++ fundamental type.
        typ = typ.replace("long int", "long")

        # If there is no embedded %s then just append the name.
        if "%s" in typ:
            s = typ % name
        else:
            s = typ

            if name:
                if typ[-1] not in "&*":
                    s += " "

                s += name

        return s

    def ignore_namespaces(self, typ):
        """
        Return the name of a type with any namespaces to be ignored removed.

        typ is the type.
        """
        for ins in self.get_project().ignorednamespaces:
            ns_name = ins + "::"

            if typ.startswith(ns_name):
                typ = typ[len(ns_name):]
                break

        # Handle any template arguments.
        t_start = typ.find('<')
        t_end = typ.rfind('>')

        if t_start > 0 and t_end > t_start:
            xt = []

            # Note that this doesn't handle nested template arguments properly.
            for t_arg in typ[t_start + 1:t_end].split(','):
                xt.append(self.ignore_namespaces(t_arg.strip()))

            typ = typ[:t_start + 1] + ', '.join(xt) + typ[t_end:]

        return typ


@implements(IProject)
class Project(Model):
    """ This class represents a MetaSIP project. """

    # The filename of the project.
    name = Str()

    def vmap_create(self, initial):
        """ Return a version map with each entry set to an initial value. """

        return [initial for v in self.versions]

    def vmap_or_version_ranges(self, vmap, version_ranges):
        """ Update a version map with a list of version ranges.  Return True if
        the map becomes unconditionally True.
        """

        if len(version_ranges) == 0:
            vmap[:] = self.vmap_create(True)
            return True

        for version_range in version_ranges:
            if version_range.startversion == '':
                start_idx = 0
            else:
                start_idx = self.versions.index(version_range.startversion)

            if version_range.endversion == '':
                end_idx = len(self.versions)
            else:
                end_idx = self.versions.index(version_range.endversion)

            for i in range(start_idx, end_idx):
                vmap[i] = True

            if all(vmap):
                return True

        return False

    def vmap_to_version_ranges(self, vmap):
        """ Convert a version map to a list of version ranges.  An empty list
        means it is unconditionally True, None means it is unconditionally
        False.
        """

        # See if the item is valid for all versions.
        if all(vmap):
            return []

        # See if the item is valid for no versions.
        for v in vmap:
            if v:
                break
        else:
            return None

        # Construct the new list of version ranges.
        version_ranges = []
        vrange = None

        for idx, v in enumerate(vmap):
            if v:
                # Start a new version range if there isn't one currently.
                if vrange is None:
                    vrange = VersionRange()

                    if idx != 0:
                        vrange.startversion = self.versions[idx]
            elif vrange is not None:
                vrange.endversion = self.versions[idx]
                version_ranges.append(vrange)
                vrange = None

        if vrange is not None:
            version_ranges.append(vrange)

        return version_ranges

    def nameArgumentsFromConventions(self, prj_item, update):
        """
        Name the arguments of all callables contained in a part of the project
        according to the conventions.  Returns a 2-tuple of a list of callables
        with invalid arguments and a list of updated Argument instances.

        prj_item is the part of the project.
        update is set if the project should be updated with the names.
        """

        invalid = []
        updated = []

        for callable in self._get_unnamed_callables(prj_item):
            more_invalid, more_updated = self._applyConventions(callable,
                    update)
            invalid += more_invalid
            updated += more_updated

        if len(updated) != 0:
            IDirty(self).dirty = True

        return invalid, updated

    def acceptArgumentNames(self, prj_item):
        """
        Mark the arguments of all callables contained in a part of the project
        as being named.  Return a list of the updated Argument instances.

        prj_item is the part of the project.
        """

        updated = []

        for callable in self._get_unnamed_callables(prj_item):
            for arg in callable.args:
                if arg.unnamed and arg.default != '':
                    arg.unnamed = False
                    updated.append(arg)

        if len(updated) != 0:
            IDirty(self).dirty = True

        return updated

    def updateArgumentsFromWebXML(self, ui, module):
        """
        Update any unnamed arguments of all callables contained in a module
        from WebXML.  Returns a 2-tuple of a list of undocumented callables and
        a list of updated Argument instances.

        ui is the user interface.
        module is the module.
        """
        undocumented = []
        updated_args = []

        webxml = ui.loadWebXML()

        for hf in module:
            for callable in self._get_unnamed_callables(hf):
                # Convert the callable to the normalised form used by the
                # WebXML key.

                try:
                    static = callable.static
                except AttributeError:
                    static = False

                if static:
                    static = 'static '
                else:
                    static = ''

                try:
                    const = callable.const
                except AttributeError:
                    const = False

                if const:
                    const = ' const'
                else:
                    const = ''

                arg_types = []
                arg_names = []
                for arg in callable.args:
                    assert type(arg) is Argument

                    atype = arg.type.replace(' ', '')
                    if atype.startswith('const'):
                        atype = 'const ' + atype[5:]

                    # Function pointers may contain a format character.
                    if '%' in atype:
                        atype = atype % ''

                    arg_types.append(atype)
                    arg_names.append(arg.name)

                sig = '%s%s(%s)%s' % (static, self._fullName(callable), ', '.join(arg_types), const)

                names = webxml.get(sig)
                if names is None:
                    undocumented.append(sig)
                else:
                    for name, arg in zip(names, callable.args):
                        if arg.unnamed and name:
                            arg.name = name
                            updated_args.append(arg)

        if len(updated_args) != 0:
            IDirty(self).dirty = True

        return undocumented, updated_args

    def _applyConventions(self, callable, update):
        """
        Apply the conventions to a callable.  Returns a 2-tuple of a list of
        callables with invalid arguments and a list of updated Argument
        instances.
        """
        invalid = []
        updated = []
        skip = False

        # Make sure copy ctors don't have a named argument.
        if type(callable) is Constructor:
            if len(callable.args) == 1:
                arg = callable.args[0]
                atype = arg.type.replace(' ', '')

                if atype == 'const%s&' % callable.name:
                    skip = True

                    if arg.name != '' and arg.default != '':
                        if update:
                            arg.name = ''
                            arg.unnamed = False
                            updated.append(arg)
                        else:
                            invalid.append("%s copy constructor has a named argument" % self._fullName(callable.container))

        if type(callable) in (Function, Method):
            if callable.name == 'event' or callable.name.endswith('Event'):
                # Make sure single argument event handlers don't have a named
                # argument.

                if len(callable.args) == 1:
                    skip = True

                    arg = callable.args[0]

                    if arg.default != '':
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if arg.name != '':
                            if update:
                                arg.name = ''
                            else:
                                invalid.append("%s() event handler has a named argument" % self._fullName(callable))

        if not skip:
            for arg in callable.args:
                if arg.default == '':
                    continue

                if arg.unnamed:
                    # Check that events are called 'event'.
                    if self._argType(arg).endswith('Event*'):
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if arg.name != 'event':
                            if update:
                                arg.name = 'event'
                            else:
                                invalid.append("%s() event argument name '%s' is not 'event'" % (self._fullName(callable), arg.name))

                        continue

                    # Check that objects are called 'object' or 'parent'.
                    if self._argType(arg) == 'QObject*':
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if arg.name not in ('object', 'parent'):
                            if update:
                                arg.name = 'object'
                            else:
                                invalid.append("%s() QObject argument name '%s' is not 'object' or 'parent'" % (self._fullName(callable), arg.name))

                        continue

                    # Check that widgets are called 'widget' or 'parent'.
                    if self._argType(arg) == 'QWidget*':
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if arg.name not in ('widget', 'parent'):
                            if update:
                                arg.name = 'widget'
                            else:
                                invalid.append("%s() QWidget argument name '%s' is not 'widget' or 'parent'" % (self._fullName(callable), arg.name))

                        continue

                    # Check other common suffixes.
                    suffixes = ("Index", "Device", "NamePool", "Handler",
                            "Binding", "Mode")

                    for s in suffixes:
                        if self._argType(arg).endswith(s):
                            if update:
                                arg.unnamed = False
                                updated.append(arg)

                            lc_s = s[0].lower() + s[1:]
                            if arg.name != lc_s:
                                if update:
                                    arg.name = lc_s
                                else:
                                    invalid.append("%s() '%s' argument name '%s' is not '%s'" % (self._fullName(callable), s, arg.name, lc_s))

                    # Check for non-standard acronyms.
                    acronyms = ("XML", "URI", "URL")

                    for a in acronyms:
                        if a in arg.name:
                            if update:
                                arg.unnamed = False
                                updated.append(arg)

                            lc_a = arg.name.replace(a, a[0] + a[1:].lower())
                            if update:
                                arg.name = lc_a
                            else:
                                invalid.append("%s() argument name '%s' should be '%s'" % (self._fullName(callable), arg.name, lc_a))

                    # Check the callable has arguments with names and that they
                    # are long enough that they don't need checking manually.
                    if len(arg.name) <= 2:
                        invalid.append("%s() argument name '%s' is too short" % (self._fullName(callable), arg.name))

        return invalid, updated

    @staticmethod
    def _argType(arg):
        """
        Return the normalised C++ type of an argument.

        arg is the argument.
        """
        return arg.type.replace(' ', '')

    @staticmethod
    def _fullName(item):
        """
        Return the C++ name of an item.

        item is the item.
        """
        names = []

        while type(item) is not SipFile:
            names.insert(0, item.name)
            item = item.container

        return '::'.join(names)

    def _get_unnamed_callables(self, part):
        """
        A generator for all the checked callables in a part of a project.

        part is the part of the project.
        """
        ptype = type(part)

        if ptype is SipFile:
            for sub in part:
                for callable in self._get_unnamed_callables(sub):
                    yield callable
        elif not part.status:
            if ptype is Function:
                for arg in part.args:
                    if arg.unnamed and arg.default != '':
                        yield part
                        break
            elif ptype in (Constructor, Method):
                if part.access != 'private':
                    for arg in part.args:
                        if arg.unnamed and arg.default != '':
                            yield part
                            break
            elif ptype in (Class, Namespace):
                for sub in part:
                    for callable in self._get_unnamed_callables(sub):
                        yield callable

    def save(self, saveas=None):
        """
        Save the project and return True if the save was successful.

        saveas is the name of the file to save to, or None if the current file
        should be used.
        """
        if saveas is None:
            fname = self.name + ".new"
        else:
            fname = saveas

        # Open/create the file.
        f = _createIndentFile(self, fname)

        if f is None:
            return False

        # Handle the versions.
        if len(self.versions) != 0:
            vers = ' versions="{0}"'.format(' '.join(self.versions))
        else:
            vers = ''

        # Handle the platforms.
        if len(self.platforms) != 0:
            plat = ' platforms="{0}"'.format(' '.join(self.platforms))
        else:
            plat = ''

        # Handle the features.
        if len(self.features) != 0:
            feat = ' features="{0}"'.format(' '.join(self.features))
        else:
            feat = ''

        # Handle the external modules.
        if len(self.externalmodules) != 0:
            xmod = ' externalmodules="{0}"'.format(
                    ' '.join(self.externalmodules))
        else:
            xmod = ''

        # Handle the external features.
        if len(self.externalfeatures) != 0:
            xf = ' externalfeatures="{0}"'.format(
                    ' '.join(self.externalfeatures))
        else:
            xf = ''

        # Handle the ignored namespaces.
        if len(self.ignorednamespaces) != 0:
            ins = ' ignorednamespaces="{0}"'.format(
                    ' '.join(self.ignorednamespaces))
        else:
            ins = ''

        # Write the project using the current format version.
        f.write('<?xml version="1.0"?>\n')
        f.write('<Project version="%u" rootmodule="%s"%s%s%s%s%s%s>\n' % (ProjectVersion, self.rootmodule, vers, plat, feat, xmod, xf, ins))

        f += 1

        # Write the literals.
        if self.sipcomments != '':
            _writeLiteralXML(f, 'sipcomments', self.sipcomments)

        for hdir in self.headers:
            if len(hdir.scan) != 0:
                if hdir.scan[0] == '':
                    scan_versions = []
                else:
                    scan_versions = hdir.scan

                scan = ' scan="{0}"'.format(' '.join(scan_versions))
            else:
                scan = ''

            f.write('<HeaderDirectory name="{0}" parserargs="{1}" inputdirsuffix="{2}" filefilter="{3}"{4}>\n'.format(hdir.name, hdir.parserargs, hdir.inputdirsuffix, hdir.filefilter, scan))
            f += 1

            for hf in hdir.content:
                hf.xml(f)

            f -= 1
            f.write('</HeaderDirectory>\n')

        for mod in self.modules:
            f.write('<Module name="%s"' % mod.name)

            if mod.outputdirsuffix != '':
                f.write(' outputdirsuffix="%s"' % mod.outputdirsuffix)

            if mod.callsuperinit != 'undefined':
                f.write(' callsuperinit="%s"' % ('1' if mod.callsuperinit == 'yes' else '0'))

            if mod.virtualerrorhandler != '':
                f.write(' virtualerrorhandler="%s"' % mod.virtualerrorhandler)

            if mod.version != '':
                f.write(' version="%s"' % mod.version)

            if len(mod.imports) != 0:
                f.write(' imports="{0}"'.format(' '.join(mod.imports)))

            f.write('>\n')

            f += 1

            if mod.directives != '':
                _writeLiteralXML(f, "directives", mod.directives)

            for sf in mod.content:
                sf.xml(f)

            f -= 1
            f.write('</Module>\n')

        f -= 1
        f.write('</Project>\n')

        # Tidy up, renaming the project as necessary.
        f.close()

        if saveas is None:
            # Remove any backup file.
            backup = self.name + "~"
            try:
                os.remove(backup)
            except:
                pass

            os.rename(self.name, backup)
            os.rename(fname, self.name)
            os.remove(backup)
        else:
            self.name = saveas

        return True

    def descriptive_name(self):
        """ Return the descriptive name of the project. """

        if self.name == '':
            return "Unnamed"

        # Remove the standard extension, but leave any non-standard one in
        # place.
        (root, ext) = os.path.splitext(self.name)

        if ext != ".msp":
            root = self.name

        return os.path.basename(root)

    def generateModule(self, mod, od, latest_sip=True):
        """
        Generate the output for a module.  Return True if there was no error.

        mod is the module instance.
        od is the root of the output directory.
        """
        # Remember the root directory used.
        od = os.path.abspath(od)

        # Generate each applicable .sip file.
        sfnames = []
        for sf in mod.content:
            f = self._createSipFile(od, mod, sf)

            if f is None:
                return False

            Logger.log("Generating %s" % f.name)
            sf.sip(f, latest_sip)
            sfnames.append(os.path.basename(f.name))

            f.close()

        f = self._createSipFile(od, mod)

        if f is None:
            return False

        Logger.log("Generating %s" % f.name)

        rname = self.rootmodule

        if rname != '':
            rname += "."

        if latest_sip:
            if mod.callsuperinit != 'undefined':
                callsuperinit = ", call_super_init=%s" % ('True' if mod.callsuperinit == 'yes' else 'False')
            else:
                callsuperinit = ""

            if mod.virtualerrorhandler != '':
                virtualerrorhandler = ", default_VirtualErrorHandler=%s" % mod.virtualerrorhandler
            else:
                virtualerrorhandler = ""

            if mod.version != '':
                version = ", version=%s" % mod.version
            else:
                version = ""

            f.write("%%Module(name=%s%s%s%s, keyword_arguments=\"Optional\"%s)\n\n" % (rname, mod.name, callsuperinit, virtualerrorhandler, version))
        else:
            f.write("%%Module %s%s 0\n\n" % (rname, mod.name))

        top_level_module = True

        if len(mod.imports) != 0:
            for m in mod.imports:
                f.write("%%Import %s/%smod.sip\n" % (m, m))

                if m not in self.externalmodules:
                    top_level_module = False

            f.write("\n")

        if top_level_module:
            # Add any version, platform and feature information to all top
            # level modules (ie. those that don't import anything).

            if len(self.versions) != 0:
                f.write("%%Timeline {%s}\n\n" % ' '.join(self.versions))

            if len(self.platforms) != 0:
                f.write("%%Platforms {%s}\n\n" % ' '.join(self.platforms))

            if len(self.features) != 0:
                for feat in self.features:
                    f.write("%Feature {0}\n".format(feat))

                f.write("\n")

        if mod.directives:
            f.write(mod.directives)
            f.write("\n\n")

        for inc in sfnames:
            f.write("%%Include %s\n" % inc)

        f.close()

        return True

    def _createSipFile(self, od, mod, sf=None):
        """
        Return a boilerplate .sip file.

        od is the root of the output directory.
        mod is the module instance.
        sf is the .sip file instance.
        """
        # Work out the name of the file.
        if mod.outputdirsuffix:
            od = os.path.join(od, mod.outputdirsuffix)

        if sf is None:
            fname = mod.name + "mod"
        else:
            (fname, ext) = os.path.splitext(os.path.basename(sf.name))

        fname += ".sip"

        # Make sure the output directory exists.
        try:
            os.makedirs(od)
        except:
            pass

        pname = str(os.path.join(od, fname))

        f = _createIndentFile(self, pname, 4)

        if f:
            # Add the standard header.
            f.write(
"""// %s generated by MetaSIP
//
// This file is part of the %s Python extension module.
""" % (fname, mod.name))

            if self.sipcomments:
                f.write("//\n%s\n" % self.sipcomments)

            f.write("\n")
            f.blank()

        return f

    def findHeaderDirectory(self, target):
        """
        Return the header directory instance of a header file.

        target is the header file instance.
        """
        for hdir in self.headers:
            for hf in hdir.content:
                if hf is target:
                    return hdir

        # This should never happen.
        return None


class Code(TaggedItem, Annotations):
    """ This class is the base class for all elements of parsed C++ code. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        # Return the user friendly representation by default.
        return self.user()

    def xml(self, f):
        """
        Write the code to an XML file.  This only calls the method for each
        child code.  This method should be reimplemented to write the code
        specific data.

        f is the file.
        """
        for c in self.content:
            c.xml(f)

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Annotations.xmlAttributes(self)
        xml += TaggedItem.xmlAttributes(self)

        return xml


class Access(Model):
    """ This class is derived by all code that is affected by class access. """

    def sigAccess(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        # Any Qt specific part isn't part of the signature.
        try:
            s = self.access.split()[0]
        except IndexError:
            s = ""

        if s == 'signals':
            # This is a horrible hack (although a fairly safe one) until we
            # decide how to do it nicely.
            s = 'protected' if working_version.startswith('Qt_4_') else ''
        elif s == 'public':
            s = ''

        return s

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = []

        if self.access != '':
            xml.append('access="{0}"'.format(self.access))

        return xml


@implements(IModule)
class Module(Model):
    """ This class represents a project module. """


@implements(IHeaderDirectory)
class HeaderDirectory(Model):
    """ This class represents a project header directory. """


@implements(ISipFile)
class SipFile(Model):
    """ This class represents a .sip file. """

    # The project.
    project = Instance(IProject)

    def sip(self, f, latest_sip):
        """ Write the .sip file. """

        # See if we need a %ModuleCode directive for things which will be
        # implemented at the module level.  At the same time find the version
        # ranges that cover all the API items.
        vmap = self.project.vmap_create(False)
        need_header = False

        # This is a hack to handle the case of everything being contained in a
        # single ignored namespace.
        # FIXME: Need to handle features as well as versions.
        api_items = self.content
        if len(api_items) == 1:
            api_item = api_items[0]

            if isinstance(api_item, Namespace) and api_item.name in self.project.ignorednamespaces:
                api_items = api_item.content

        for api_item in api_items:
            if api_item.status != '':
                continue

            if vmap is not None and self.project.vmap_or_version_ranges(vmap, api_item.versions):
                vmap = None
                if need_header:
                    break

            # Note that OperatorFunctions are handled within the class even if
            # they have global declarations.
            if isinstance(api_item, (Function, Variable, Enum)):
                need_header = True
                if vmap is None:
                    break

        if need_header:
            if vmap is None:
                need = [VersionRange()]
            else:
                need = self.project.vmap_to_version_ranges(vmap)

            for vrange in need:
                vrange_str = version_range(vrange)

                if vrange_str != '':
                    f.write("%%If (%s)\n" % vrange_str, False)

                f.write(
"""%%ModuleCode
#include <%s>
%%End
""" % self.name)

                if vrange_str != '':
                    f.write("%End\n", False)

            f.blank()

        for api_item in self.content:
            if api_item.status == '':
                api_item.sip(f, self, latest_sip)

        f.blank()

        if self.exportedheadercode:
            _writeCodeSIP(f, "%ExportedHeaderCode", self.exportedheadercode, False)

        if self.moduleheadercode:
            _writeCodeSIP(f, "%ModuleHeaderCode", self.moduleheadercode, False)

        if self.modulecode:
            _writeCodeSIP(f, "%ModuleCode", self.modulecode, False)

        if self.preinitcode:
            _writeCodeSIP(f, "%PreInitialisationCode", self.preinitcode, False)

        if self.initcode:
            _writeCodeSIP(f, "%InitialisationCode", self.initcode, False)

        if self.postinitcode:
            _writeCodeSIP(f, "%PostInitialisationCode", self.postinitcode, False)

        if self.exportedtypehintcode:
            _writeCodeSIP(f, "%ExportedTypeHintCode", self.exportedtypehintcode, False)

        if self.typehintcode:
            _writeCodeSIP(f, "%TypeHintCode", self.typehintcode, False)

    def xml(self, f):
        """ Write the .sip file to an XML file. """

        f.write('<SipFile%s>\n' % _attrsAsString(self))

        f += 1
        for c in self.content:
            c.xml(f)
        f -= 1

        if self.exportedheadercode:
            _writeLiteralXML(f, "exportedheadercode", self.exportedheadercode)

        if self.moduleheadercode:
            _writeLiteralXML(f, "moduleheadercode", self.moduleheadercode)

        if self.modulecode:
            _writeLiteralXML(f, "modulecode", self.modulecode)

        if self.preinitcode:
            _writeLiteralXML(f, "preinitcode", self.preinitcode)

        if self.initcode:
            _writeLiteralXML(f, "initcode", self.initcode)

        if self.postinitcode:
            _writeLiteralXML(f, "postinitcode", self.postinitcode)

        if self.exportedtypehintcode:
            _writeLiteralXML(f, "exportedtypehintcode", self.exportedtypehintcode)

        if self.typehintcode:
            _writeLiteralXML(f, "typehintcode", self.typehintcode)

        f.write('</SipFile>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        return ['name="{0}"'.format(self.name)]


@implements(IHeaderFileVersion)
class HeaderFileVersion(Model):
    """ This class represents a version of a project header file. """

    def xml(self, f):
        """ Write the header file version to an XML file. """

        f.write('<HeaderFileVersion%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = []

        xml.append('md5="{0}"'.format(self.md5))
        xml.append('version="{0}"'.format(self.version))

        if self.parse:
            xml.append('parse="1"')

        return xml


@implements(IHeaderFile)
class HeaderFile(Model):
    """ This class represents a project header file. """

    # The project.
    project = Instance(IProject)

    def xml(self, f):
        """ Write the header file to an XML file. """

        f.write('<HeaderFile%s>\n' % _attrsAsString(self))

        f += 1
        for v in self.versions:
            v.xml(f)
        f -= 1

        f.write('</HeaderFile>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = []

        xml.append('name="{0}"'.format(self.name))

        if self.module != '':
            xml.append('module="{0}"'.format(self.module))

        if self.ignored:
            xml.append('ignored="1"')

        return xml


@implements(IArgument)
class Argument(Annotations):
    """ This class represents an argument. """

    def signature(self, callable, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = callable.expand_type(self.type)

        if self.default != '':
            s += " = " + self.default

        return s

    def user(self, callable):
        """
        Return a user friendly representation of the argument.
        """
        s = callable.expand_type(self.type)

        if self.name != '':
            if s[-1] not in "&*":
                s += " "

            s += self.name

        if self.default != '':
            s += " = " + self.default

        return s

    def sip(self, callable, latest_sip, ignore_namespaces=True):
        """
        Return the argument suitable for writing to a SIP file.
        """
        if self.pytype != '':
            s = self.pytype
        else:
            s = callable.expand_type(self.type,
                    ignore_namespaces=ignore_namespaces)

        if self.name != '':
            if s[-1] not in "&*":
                s += " "

            s += self.name

        s += self.sipAnnos()

        if self.default != '':
            s += " = " + callable.ignore_namespaces(self.default)

        return s

    def xml(self, f):
        """ Write the argument to an XML file. """

        f.write('<Argument%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        xml.append('type="{0}"'.format(escape(self.type)))

        if self.unnamed:
            xml.append('unnamed="1"')

        if self.name != '':
            xml.append('name="{0}"'.format(escape(self.name)))

        if self.default != '':
            xml.append('default="{0}"'.format(escape(self.default)))

        if self.pytype != '':
            xml.append('pytype="{0}"'.format(escape(self.pytype)))

        return xml


@implements(IClass)
class Class(Code, Access):
    """ This class represents a class. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        if self.struct:
            s = "struct"
        else:
            s = "class"

        if self.name != '':
            s += " " + self.name

        if self.bases != '':
            s += " : " + self.bases

        s += self.sigAccess(working_version)

        return s

    def user(self):
        """
        Return a user friendly representation of the class.
        """
        if self.struct:
            s = "struct"
        else:
            s = "class"

        if self.name != '':
            s += " " + self.name

        if self.bases != '':
            s += " : " + self.bases

        s += self.sipAnnos()

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the class to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        f.blank()

        bstr = ""

        if self.struct:
            tname = "struct "
        else:
            tname = "class "

        if self.pybases != '':
            # Treat None as meaning no super classes:
            if self.pybases != "None":
                bstr = " : " + ", ".join(self.pybases.split())
        elif self.bases != '':
            clslst = []

            for b in self.bases.split(", "):
                acc, cls = b.split()

                # Handle any ignored namespace.
                cls = self.ignore_namespaces(cls)

                # Remove public to maintain compatibility with old SIPs.
                if acc == "public":
                    clslst.append(cls)
                else:
                    clslst.append("%s %s" % (acc, cls))

            bstr = " : " + ", ".join(clslst)

        f.write(tname + self.name + bstr + self.sipAnnos() + "\n{\n")

        _writeDocstringSIP(f, self.docstring)

        f.write("%TypeHeaderCode\n", False)

        if self.typeheadercode:
            f.write(self.typeheadercode + "\n", False)
        else:
            f.write("#include <%s>\n" % sf.name, False)

        f.write("%End\n", False)

        f.blank()

        if self.typecode:
            _writeCodeSIP(f, "%TypeCode", self.typecode, False)

        if self.finalisationcode:
            _writeCodeSIP(f, "%FinalisationCode", self.finalisationcode)

        if self.subclasscode:
            _writeCodeSIP(f, "%ConvertToSubClassCode", self.subclasscode)

        if self.convtotypecode:
            _writeCodeSIP(f, "%ConvertToTypeCode", self.convtotypecode, False)

        if self.convfromtypecode:
            _writeCodeSIP(f, "%ConvertFromTypeCode", self.convfromtypecode,
                    False)

        if self.gctraversecode:
            _writeCodeSIP(f, "%GCTraverseCode", self.gctraversecode)

        if self.gcclearcode:
            _writeCodeSIP(f, "%GCClearCode", self.gcclearcode)

        if self.bigetbufcode:
            _writeCodeSIP(f, "%BIGetBufferCode", self.bigetbufcode)

        if self.birelbufcode:
            _writeCodeSIP(f, "%BIReleaseBufferCode", self.birelbufcode)

        if self.bireadbufcode:
            _writeCodeSIP(f, "%BIGetReadBufferCode", self.bireadbufcode)

        if self.biwritebufcode:
            _writeCodeSIP(f, "%BIGetWriteBufferCode", self.biwritebufcode)

        if self.bisegcountcode:
            _writeCodeSIP(f, "%BIGetSegCountCode", self.bisegcountcode)

        if self.bicharbufcode:
            _writeCodeSIP(f, "%BIGetCharBufferCode", self.bicharbufcode)

        if self.picklecode:
            _writeCodeSIP(f, "%PickleCode", self.picklecode)

        f += 1

        if self.struct:
            access = ""
        else:
            access = "private"

        for api_item in self.content:
            if api_item.status != '':
                continue

            if isinstance(api_item, Access):
                if access != api_item.access:
                    f -= 1
                    access = api_item.access

                    if access != '':
                        astr = access
                    else:
                        astr = "public"

                    f.blank()
                    f.write(astr + ":\n")
                    f += 1

            api_item.sip(f, sf, latest_sip)

        f -= 1
        f.write("};\n")

        f.blank()

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the class to an XML file. """

        f.write('<Class%s>\n' % _attrsAsString(self))

        _writeDocstringXML(f, self.docstring)

        if self.typeheadercode:
            _writeLiteralXML(f, "typeheadercode", self.typeheadercode)

        if self.typecode:
            _writeLiteralXML(f, "typecode", self.typecode)

        if self.finalisationcode:
            _writeLiteralXML(f, "finalisationcode", self.finalisationcode)

        if self.subclasscode:
            _writeLiteralXML(f, "subclasscode", self.subclasscode)

        if self.convtotypecode:
            _writeLiteralXML(f, "convtotypecode", self.convtotypecode)

        if self.convfromtypecode:
            _writeLiteralXML(f, "convfromtypecode", self.convfromtypecode)

        if self.gctraversecode:
            _writeLiteralXML(f, "gctraversecode", self.gctraversecode)

        if self.gcclearcode:
            _writeLiteralXML(f, "gcclearcode", self.gcclearcode)

        if self.bigetbufcode:
            _writeLiteralXML(f, "bigetbufcode", self.bigetbufcode)

        if self.birelbufcode:
            _writeLiteralXML(f, "birelbufcode", self.birelbufcode)

        if self.bireadbufcode:
            _writeLiteralXML(f, "bireadbufcode", self.bireadbufcode)

        if self.biwritebufcode:
            _writeLiteralXML(f, "biwritebufcode", self.biwritebufcode)

        if self.bisegcountcode:
            _writeLiteralXML(f, "bisegcountcode", self.bisegcountcode)

        if self.bicharbufcode:
            _writeLiteralXML(f, "bicharbufcode", self.bicharbufcode)

        if self.picklecode:
            _writeLiteralXML(f, "picklecode", self.picklecode)

        f += 1
        super().xml(f)
        f -= 1
        f.write('</Class>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Code.xmlAttributes(self)
        xml += Access.xmlAttributes(self)

        name = 'name="'

        if self.name != '':
            name += escape(self.name)

        name += '"'

        xml.append(name)

        if self.bases != '':
            xml.append('bases="{0}"'.format(escape(self.bases)))

        if self.pybases != '':
            xml.append('pybases="{0}"'.format(escape(self.pybases)))

        if self.struct:
            xml.append('struct="1"')

        return xml


class Callable(Code):
    """ This class represents a callable. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return self.expand_type(self.rtype) + self.name + "(" + ", ".join([a.signature(self, working_version) for a in self.args]) + ")"

    def user(self):
        """
        Return a user friendly representation of the callable.
        """
        # Note that we do include a separate C++ signature if it is different
        # to the Python signature.  This is so we always hint to the user that
        # something has been manually changed.

        s = self.returnType() + self.name

        if self.pyargs != '':
            s += self.pyargs
        else:
            s += "(" + ", ".join([a.sip(self, latest_sip=True, ignore_namespaces=False) for a in self.args]) + ")"

        s += self.sipAnnos()

        if self.pytype != '' or self.pyargs != '' or self.hasPyArgs():
            s += " [%s (%s)]" % (self.expand_type(self.rtype), ", ".join([a.user(self) for a in self.args]))

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the callable to a .sip file. """

        # Note that we don't include a separate C++ signature.  This is handled
        # where needed by sub-classes.

        f.write(self.returnType(ignore_namespaces=True) + self.name)

        if self.pyargs != '':
            f.write(self.pyargs)
        else:
            f.write("(" + ", ".join([a.sip(self, latest_sip) for a in self.args]) + ")")

        f.write(self.sipAnnos())

    def returnType(self, ignore_namespaces=False):
        """
        Return the return type as a string.
        """
        if self.pytype != '':
            s = self.pytype
        elif self.rtype != '':
            s = self.expand_type(self.rtype,
                    ignore_namespaces=ignore_namespaces)
        else:
            return ""

        if s[-1] not in "&*":
            s += " "

        return s

    def sipDocstring(self, f):
        """ Write any docstring to a .sip file. """

        _writeDocstringSIP(f, self.docstring)

    def sipMethcode(self, f):
        """ Write any method code to a .sip file. """

        _writeMethCodeSIP(f, self.methcode)

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        xml.append('name="{0}"'.format(escape(self.name)))

        if self.rtype != '':
            xml.append('rtype="{0}"'.format(escape(self.rtype)))

        if self.pytype != '':
            xml.append('pytype="{0}"'.format(escape(self.pytype)))

        if self.pyargs != '':
            xml.append('pyargs="{0}"'.format(escape(self.pyargs)))

        return xml

    def xmlDocstring(self, f):
        """ Write any docstring to an XML file. """

        _writeDocstringXML(f, self.docstring)

    def xmlMethcode(self, f):
        """ Write any method code to an XML file. """

        _writeMethCodeXML(f, self.methcode)

    def hasPyArgs(self):
        """
        Returns true if any of the arguments has a different Python type.
        """
        for a in self.args:
            if a.pytype != '':
                # We treat SIP_SIGNAL and SIP_SLOT as synonyms for const char *.
                if a.pytype not in ("SIP_SIGNAL", "SIP_SLOT") or a.type != "const char *":
                    return True

        return False


@implements(IEnumValue)
class EnumValue(TaggedItem, Annotations):
    """ This class represents an enum value. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return self.user()

    def user(self):
        """
        Return a user friendly representation of the enum value.
        """
        return self.name

    def sip(self, f, latest_sip):
        """ Write the enum value to a .sip file. """

        nr_ends = _sip_start_version(f, self)
        f.write(self.name + self.sipAnnos() + ",\n")
        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the enum value to an XML file. """

        f.write('<EnumValue%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Annotations.xmlAttributes(self)
        xml += TaggedItem.xmlAttributes(self)

        xml.append('name="{0}"'.format(self.name))

        return xml


@implements(IEnum)
class Enum(Code, Access):
    """ This class represents an enum. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature(working_version) + self.sigAccess(working_version)

    def user(self):
        """
        Return a user friendly representation of the enum.
        """
        s = "enum"

        if self.name != '':
            s += " " + self.name

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the enum to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        f.blank()

        f.write("enum")

        if self.name != '':
            f.write(" " + self.name)

        f.write(self.sipAnnos() + "\n{\n")
        f += 1

        for e in self.content:
            if e.status != '':
                continue

            e.sip(f, latest_sip)

        f -= 1
        f.write("};\n")
        f.blank()

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the enum to an XML file. """

        f.write('<Enum%s>\n' % _attrsAsString(self))
        f += 1

        for e in self.content:
            e.xml(f)

        f -= 1
        f.write('</Enum>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Code.xmlAttributes(self)
        xml += Access.xmlAttributes(self)

        xml.append('name="{0}"'.format(self.name))

        return xml


class ClassCallable(Callable, Access):
    """ This class represents a callable in a class context. """

    def signature(self, working_version):
        """ Return a C/C++ representation for comparison purposes. """

        return super().signature(working_version) + self.sigAccess(working_version)

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        return Callable.xmlAttributes(self) + Access.xmlAttributes(self)


@implements(IConstructor)
class Constructor(ClassCallable):
    """ This class represents a constructor. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = super().signature(working_version)

        if self.explicit:
            s = "explicit " + s

        return s

    def user(self):
        """
        Return a user friendly representation of the constructor.
        """
        s = super().user()

        if self.explicit:
            s = "explicit " + s

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the constructor to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        if self.explicit:
            f.write("explicit ")

        super().sip(f, sf, latest_sip)

        if self.pyargs != '' or self.hasPyArgs():
            f.write(" [(%s)]" % ", ".join([a.user(self) for a in self.args]))

        f.write(";\n")

        self.sipDocstring(f)
        self.sipMethcode(f)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the constructor to an XML file. """

        f.write('<Constructor%s>\n' % _attrsAsString(self))

        f += 1

        for a in self.args:
            a.xml(f)

        f -= 1

        self.xmlDocstring(f)
        self.xmlMethcode(f)
        f.write('</Constructor>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        if self.explicit:
            xml.append('explicit="1"')

        return xml


@implements(IDestructor)
class Destructor(Code, Access):
    """ This class represents a destructor. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = self.name + self.sigAccess(working_version)

        if self.virtual:
            s = "virtual " + s

        return s

    def user(self):
        """
        Return a user friendly representation of the destructor.
        """
        s = "~" + self.name + "()"

        if self.virtual:
            s = "virtual " + s

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the destructor to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        if self.virtual:
            f.write("virtual ")

        f.write("~" + self.name + "()" + self.sipAnnos() + ";\n")

        _writeMethCodeSIP(f, self.methcode)
        _writeVirtCodeSIP(f, self.virtcode)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the destructor to an XML file. """

        f.write('<Destructor%s>\n' % _attrsAsString(self))

        _writeMethCodeXML(f, self.methcode)
        _writeVirtCodeXML(f, self.virtcode)

        f.write('</Destructor>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Code.xmlAttributes(self)
        xml += Access.xmlAttributes(self)

        xml.append('name="{0}"'.format(escape(self.name)))

        if self.virtual:
            xml.append('virtual="1"')

        return xml


@implements(IOperatorCast)
class OperatorCast(ClassCallable):
    """ This class represents an operator cast. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = "operator " + super().signature(working_version)

        if self.const:
            s += " const"

        return s

    def user(self):
        """
        Return a user friendly representation of the operator cast.
        """
        s = "operator " + super().user()

        if self.const:
            s += " const"

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the operator cast to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        f.write("operator ")

        super().sip(f, sf, latest_sip)

        if self.const:
            f.write(" const")

        f.write(";\n")

        self.sipMethcode(f)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the operator cast to an XML file. """

        f.write('<OperatorCast%s>\n' % _attrsAsString(self))

        f += 1

        for a in self.args:
            a.xml(f)

        f -= 1

        self.xmlMethcode(f)
        f.write('</OperatorCast>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        if self.const:
            xml.append('const="1"')

        return xml


@implements(IMethod)
class Method(ClassCallable):
    """ This class represents a method. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = ""

        if self.virtual:
            s += "virtual "

        if self.static:
            s += "static "

        s += self.expand_type(self.rtype) + self.name + "(" + ", ".join([a.signature(self, working_version) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sigAccess(working_version)

        return s

    def user(self):
        """
        Return a user friendly representation of the method.
        """
        # We can't use the super class version because we might need to stick
        # some text in the middle of it.
        s = ""

        if self.virtual:
            s += "virtual "

        if self.static:
            s += "static "

        s += self.returnType() + self.name

        if self.pyargs:
            s += self.pyargs
        else:
            s += "(" + ", ".join([a.sip(self, latest_sip=True, ignore_namespaces=False) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sipAnnos()

        if self.pytype or self.pyargs or self.hasPyArgs():
            s += " [%s (%s)]" % (self.expand_type(self.rtype), ", ".join([a.user(self) for a in self.args]))

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the method to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        # We can't use the super class version because we might need to stick
        # some text in the middle of it.
        s = ""

        if self.virtual:
            s += "virtual "

        if self.static:
            s += "static "

        s += self.returnType(ignore_namespaces=True) + self.name

        if self.pyargs:
            s += self.pyargs
        else:
            s += "(" + ", ".join([a.sip(self, latest_sip) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sipAnnos()

        if (self.virtual or self.access.startswith("protected") or not self.methcode) and (self.pytype or self.pyargs or self.hasPyArgs()):
            s += " [%s (%s)]" % (self.expand_type(self.rtype, ignore_namespaces=True), ", ".join([a.user(self) for a in self.args]))

        f.write(s + ";\n")

        self.sipDocstring(f)
        self.sipMethcode(f)
        _writeVirtCodeSIP(f, self.virtcode)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the method to an XML file. """

        f.write('<Method%s>\n' % _attrsAsString(self))

        f += 1

        for a in self.args:
            a.xml(f)

        f -= 1

        self.xmlDocstring(f)
        self.xmlMethcode(f)
        _writeVirtCodeXML(f, self.virtcode)

        f.write('</Method>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        if self.virtual:
            xml.append('virtual="1"')

        if self.const:
            xml.append('const="1"')

        if self.static:
            xml.append('static="1"')

        if self.abstract:
            xml.append('abstract="1"')

        return xml


@implements(IOperatorMethod)
class OperatorMethod(ClassCallable):
    """ This class represents a scoped operator. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = ""

        if self.virtual:
            s += "virtual "

        s += self.expand_type(self.rtype) + "operator" + self.name + "(" + ", ".join([a.signature(self, working_version) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sigAccess(working_version)

        return s

    def user(self):
        """
        Return a user friendly representation of the operator.
        """
        s = ""

        if self.virtual:
            s += "virtual "

        s += self.returnType() + "operator" + self.name

        if self.pyargs != '':
            s += self.pyargs
        else:
            s += "(" + ", ".join([a.sip(self, latest_sip=True, ignore_namespaces=False) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sipAnnos()

        if self.pytype != '' or self.pyargs != '' or self.hasPyArgs():
            s += " [%s (%s)]" % (self.expand_type(self.rtype), ", ".join([a.user(self) for a in self.args]))

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the operator method to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        s = ""

        if self.virtual:
            s += "virtual "

        s += self.returnType(ignore_namespaces=True) + "operator" + self.name

        if self.pyargs != '':
            s += self.pyargs
        else:
            s += "(" + ", ".join([a.sip(self, latest_sip) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sipAnnos()

        if (self.virtual or self.access.startswith("protected") or not self.methcode) and (self.pytype or self.pyargs or self.hasPyArgs()):
            s += " [%s (%s)]" % (self.expand_type(self.rtype, ignore_namespaces=True), ", ".join([a.user(self) for a in self.args]))

        f.write(s + ";\n")

        self.sipMethcode(f)
        _writeVirtCodeSIP(f, self.virtcode)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the operator to an XML file. """

        f.write('<OperatorMethod%s>\n' % _attrsAsString(self))

        f += 1

        for a in self.args:
            a.xml(f)

        f -= 1

        self.xmlMethcode(f)
        _writeVirtCodeXML(f, self.virtcode)

        f.write('</OperatorMethod>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        if self.virtual:
            xml.append('virtual="1"')

        if self.const:
            xml.append('const="1"')

        if self.abstract:
            xml.append('abstract="1"')

        return xml


@implements(IFunction)
class Function(Callable):
    """ This class represents a function. """

    def sip(self, f, sf, latest_sip):
        """ Write the function to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        super().sip(f, sf, latest_sip)
        f.write(";\n")

        self.sipDocstring(f)
        self.sipMethcode(f)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the function to an XML file. """

        f.write('<Function%s>\n' % _attrsAsString(self))

        f += 1

        for a in self.args:
            a.xml(f)

        f -= 1

        self.xmlDocstring(f)
        self.xmlMethcode(f)
        f.write('</Function>\n')


@implements(IOperatorFunction)
class OperatorFunction(Callable):
    """ This class represents a global operator. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return self.expand_type(self.rtype) + "operator" + self.name + "(" + ", ".join([a.signature(self, working_version) for a in self.args]) + ")"

    def user(self):
        """
        Return a user friendly representation of the operator.
        """
        s = self.returnType() + "operator" + self.name

        if self.pyargs != '':
            s += self.pyargs
        else:
            s += "(" + ", ".join([a.sip(self, latest_sip=True, ignore_namespaces=False) for a in self.args]) + ")"

        s += self.sipAnnos()

        if self.pytype != '' or self.pyargs != '' or self.hasPyArgs():
            s += " [%s (%s)]" % (self.expand_type(self.rtype), ", ".join([a.user(self) for a in self.args]))

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the operator function to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        f.write(self.returnType(ignore_namespaces=True) + "operator" + self.name)

        if self.pyargs != '':
            f.write(self.pyargs)
        else:
            f.write("(" + ", ".join([a.sip(self, latest_sip) for a in self.args]) + ")")

        f.write(self.sipAnnos())

        f.write(";\n")

        self.sipMethcode(f)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the operator to an XML file. """

        f.write('<OperatorFunction%s>\n' % _attrsAsString(self))

        f += 1

        for a in self.args:
            a.xml(f)

        f -= 1

        self.xmlMethcode(f)
        f.write('</OperatorFunction>\n')


@implements(IVariable)
class Variable(Code, Access):
    """ This class represents a variable. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature(working_version) + self.sigAccess(working_version)

    def user(self):
        """
        Return a user friendly representation of the variable.
        """
        s = self.expand_type(self.type, self.name) + self.sipAnnos()

        if self.static:
            s = "static " + s

        return s

    def sip(self, f, sf, latest_sip):
        """ Write the variable to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        s = self.expand_type(self.type, self.name, ignore_namespaces=True)

        if self.static:
            s = "static " + s

        f.write(s + self.sipAnnos())

        if latest_sip:
            need_brace = True
        else:
            need_brace = False
            f.write(";\n", indent=False)

        if self.accesscode:
            if need_brace:
                f.write(" {\n", indent=False)
                need_brace = False

            _writeCodeSIP(f, "%AccessCode", self.accesscode)

        if self.getcode:
            if need_brace:
                f.write(" {\n", indent=False)
                need_brace = False

            _writeCodeSIP(f, "%GetCode", self.getcode)

        if self.setcode:
            if need_brace:
                f.write(" {\n", indent=False)
                need_brace = False

            _writeCodeSIP(f, "%SetCode", self.setcode)

        if latest_sip:
            if not need_brace:
                f.write("}")

            f.write(";\n", indent=False)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the variable to an XML file. """

        if self.accesscode or self.getcode or self.setcode:
            f.write('<Variable%s>\n' % _attrsAsString(self))

            if self.accesscode:
                _writeLiteralXML(f, "accesscode", self.accesscode)

            if self.getcode:
                _writeLiteralXML(f, "getcode", self.getcode)

            if self.setcode:
                _writeLiteralXML(f, "setcode", self.setcode)

            f.write('</Variable>\n')
        else:
            f.write('<Variable%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Code.xmlAttributes(self)
        xml += Access.xmlAttributes(self)

        xml.append('name="{0}"'.format(escape(self.name)))
        xml.append('type="{0}"'.format(escape(self.type)))

        if self.static:
            xml.append('static="1"')

        return xml


@implements(ITypedef)
class Typedef(Code):
    """ This class represents a typedef. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return "typedef " + self.expand_type(self.type, self.name)

    def user(self):
        """
        Return a user friendly representation of the typedef.
        """
        return "typedef " + self.expand_type(self.type, self.name) + self.sipAnnos()

    def sip(self, f, sf, latest_sip):
        """ Write the typedef to a .sip file. """

        nr_ends = _sip_start_version(f, self)
        f.write("typedef " + self.expand_type(self.type, self.name, ignore_namespaces=True) + self.sipAnnos() + ";\n")
        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the typedef to an XML file. """

        f.write('<Typedef%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        xml.append('name="{0}"'.format(escape(self.name)))
        xml.append('type="{0}"'.format(escape(self.type)))

        return xml


@implements(INamespace)
class Namespace(Code):
    """ This class represents a namespace. """

    def user(self):
        """
        Return a user friendly representation of the namespace.
        """
        return "namespace " + self.name

    def sip(self, f, sf, latest_sip):
        """ Write the namespace to a .sip file. """

        ignore = (self.name in sf.project.ignorednamespaces)

        nr_ends = _sip_start_version(f, self)

        if not ignore:
            f.blank()

            f.write("namespace " + self.name + "\n{\n")

            f.write("%TypeHeaderCode\n", False)

            if self.typeheadercode:
                f.write(self.typeheadercode + "\n", False)
            else:
                f.write("#include <%s>\n" % sf.name, False)

            f.write("%End\n", False)

            f.blank()

            f += 1

        for api_item in self.content:
            if api_item.status == '':
                api_item.sip(f, sf, latest_sip);

        if not ignore:
            f -= 1

            f.write("};\n")

            f.blank()

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the namespace to an XML file. """

        f.write('<Namespace%s>\n' % _attrsAsString(self))

        if self.typeheadercode:
            _writeLiteralXML(f, "typeheadercode", self.typeheadercode)

        f += 1
        super().xml(f)
        f -= 1
        f.write('</Namespace>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        xml.append('name="{0}"'.format(escape(self.name)))

        return xml


@implements(IOpaqueClass)
class OpaqueClass(Code, Access):
    """ This class represents an opaque class. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return "class " + self.name + self.sigAccess(working_version)

    def user(self):
        """
        Return a user friendly representation of the opaque class.
        """
        return "class " + self.name + self.sipAnnos()

    def sip(self, f, sf, latest_sip):
        """ Write the opaque class to a .sip file. """

        nr_ends = _sip_start_version(f, self);
        f.write("class " + self.name + self.sipAnnos() + ";\n")
        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the opaque class to an XML file. """

        f.write('<OpaqueClass%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Code.xmlAttributes(self)
        xml += Access.xmlAttributes(self)

        xml.append('name="{0}"'.format(escape(self.name)))

        return xml


@implements(IManualCode)
class ManualCode(Code, Access):
    """ This class represents some manual code. """

    def signature(self, working_version):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature(working_version) + self.sigAccess(working_version)

    def user(self):
        """
        Return a user friendly representation of the manual code.
        """
        return self.precis

    def sip(self, f, sf, latest_sip):
        """ Write the code to a .sip file. """

        nr_ends = _sip_start_version(f, self)

        if self.body != '':
            f.write("// " + self.precis + "\n" + self.body + "\n", False)
        elif self.precis.startswith('%'):
            f.write(self.precis + "\n", False)
        else:
            f.write(self.precis + ";\n")

        _writeDocstringSIP(f, self.docstring)
        _writeMethCodeSIP(f, self.methcode)

        _sip_end_version(f, nr_ends)

    def xml(self, f):
        """ Write the manual code to an XML file. """

        f.write('<ManualCode%s>\n' % _attrsAsString(self))

        if self.body:
            _writeLiteralXML(f, "body", self.body)

        _writeDocstringXML(f, self.docstring)
        _writeMethCodeXML(f, self.methcode)

        f.write('</ManualCode>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Code.xmlAttributes(self)
        xml += Access.xmlAttributes(self)

        xml.append('precis="{0}"'.format(escape(self.precis)))

        return xml


class _IndentFile:
    """
    This is a thin wrapper around a file object that supports indentation.
    """
    def __init__(self, fname, indent):
        """
        Create a file for writing.

        fname is the name of the file.
        indent is the default indentation step.
        """
        self._f = open(fname, "w")
        self._indent = indent
        self._nrindents = 0
        self._indentnext = True
        self._blank = False
        self._suppressblank = False

        self.name = fname

    def write(self, data, indent=True):
        """
        Write some data to the file with optional automatic indentation.

        data is the data to write.
        indent is True if the data should be indented.
        """
        if data:
            if self._blank:
                self._f.write("\n")
                self._blank = False

            lines = data.split("\n")

            for l in lines[:-1]:
                if indent and self._indentnext:
                    self._f.write(" " * (self._indent * self._nrindents))

                self._f.write(l + "\n")
                self._indentnext = True

            # Handle the last line.
            l = lines[-1]

            if l:
                if indent and self._indentnext:
                    self._f.write(" " * (self._indent * self._nrindents))

                self._f.write(l)
                self._indentnext = False
            else:
                self._indentnext = True

            self._suppressblank = False

    def blank(self):
        """
        Write a blank line.
        """
        if not self._suppressblank:
            self._blank = True

    def close(self):
        """
        Close the file.
        """
        self._f.close()

    def __iadd__(self, n):
        """
        Increase the indentation.

        n is the increase in the number of levels of indentation.
        """
        self._nrindents += n
        self._suppressblank = True

        return self

    def __isub__(self, n):
        """
        Decrease the indentation.

        n is the decrease in the number of levels of indentation.
        """
        self._nrindents -= n
        self._blank = False
        self._suppressblank = False

        return self


def _createIndentFile(prj, fname, indent=2):
    """
    Return an indent file or None if there was an error.

    prj is the project instance.
    fname is the name of the file.
    indent is the default indentation step.
    """
    try:
        f = _IndentFile(fname, indent)
    except IOError as detail:
        prj.diagnostic = "Unable to create file %s: %s" % (fname, detail)
        return None

    return f


def _writeLiteralXML(f, type, text):
    """
    Write some literal text to an XML file.

    f is the file.
    type is the type of the text.
    text is the text.
    """
    f.write('<Literal type="%s">\n%s\n</Literal>\n' % (type, escape(text)), False)


def _writeCodeSIP(f, directive, code, indent=True):
    """
    Write some code to a SIP file.

    f is the file.
    directive is the SIP directive.
    code is the code.
    indent is True if the code should be indented.
    """
    f.write(directive + "\n", False)
    f += 1
    f.write(code + "\n", indent)
    f -= 1
    f.write("%End\n", False)
    f.blank()


def _writeDocstringSIP(f, docstring):
    """
    Write an optional docstring to a SIP file.

    f is the file.
    docstring is the docstring.
    """
    if docstring:
        _writeCodeSIP(f, "%Docstring", docstring, indent=False)


def _writeDocstringXML(f, docstring):
    """
    Write an optional docstring to an XML file.

    f is the file.
    docstring is the docstring.
    """
    if docstring:
        _writeLiteralXML(f, "docstring", docstring)


def _writeMethCodeSIP(f, code):
    """
    Write some optional method code to a SIP file.

    f is the file.
    code is the code.
    """
    if code:
        _writeCodeSIP(f, "%MethodCode", code)


def _writeMethCodeXML(f, code):
    """
    Write some optional method code to an XML file.

    f is the file.
    code is the code.
    """
    if code:
        _writeLiteralXML(f, "methcode", code)


def _writeVirtCodeSIP(f, code):
    """
    Write some optional virtual catcher code to a SIP file.

    f is the file.
    code is the code.
    """
    if code:
        _writeCodeSIP(f, "%VirtualCatcherCode", code)


def _writeVirtCodeXML(f, code):
    """
    Write some optional virtual catcher code to an XML file.

    f is the file.
    code is the code.
    """
    if code:
        _writeLiteralXML(f, "virtcode", code)


def _attrsAsString(item):
    """ Return the XML attributes of an item as a string. """

    attrs = item.xmlAttributes()

    return ' ' + ' '.join(attrs) if len(attrs) != 0 else ''


def _sip_start_version(f, api_item):
    """ Write the start of the version tests for an API item.  Returns the
    number of %End statements needed to be passed to the corresponding call to
    _sip_end_version().
    """

    nr_ends = 0

    for vrange in api_item.versions:
        vr = version_range(vrange)
        if vr != '':
            f.write("%%If (%s)\n" % vr, False)
            nr_ends += 1

    # Multiple platforms are logically or-ed.
    if len(api_item.platforms) != 0:
        f.write("%%If (%s)\n" % " || ".join(api_item.platforms), False)
        nr_ends += 1

    # Multiple platforms are logically and-ed.
    for feature in api_item.features:
        f.write("%%If (%s)\n" % feature, False)
        nr_ends += 1

    return nr_ends


def _sip_end_version(f, nr_ends):
    """ Write the end of the version tests for an API item. """

    for _ in range(nr_ends):
        f.write("%End\n", False)


def _sip_versions(api_item):
    """ Return the version string corresponding to a range of versions of an
    API item.
    """

    if len(api_item.versions) == 0:
        return ""

    # At the moment we don't support generating multiple version ranges.
    if len(api_item.versions) > 1:
        raise NotImplementedError("multiple version ranges not yet supported")

    return version_range(api_item.versions[0])


def version_range(version_range):
    """ Return a version range converted to a string. """

    if version_range.startversion == '':
        if version_range.endversion == '':
            # This should never happen.
            return ""

        return "- " + version_range.endversion

    if version_range.endversion == '':
        return version_range.startversion + " -"

    return version_range.startversion + " - " + version_range.endversion


def escape(s):
    """
    Return an XML escaped string.
    """
    return saxutils.escape(s, {'"': '&quot;'})
