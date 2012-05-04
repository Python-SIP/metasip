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


import os
import hashlib
import time
import fnmatch
from xml.sax import saxutils

from dip.model import implements, Instance, Model, Str
from dip.shell import IDirty

from .logger import Logger
from .interfaces.project import (ProjectVersion, IArgument, IClass,
        IConstructor, IDestructor, IEnum, IEnumValue, IFunction,
        IHeaderDirectory, IHeaderFile, IManualCode, IMethod, IModule,
        INamespace, IOpaqueClass, IOperatorCast, IOperatorFunction,
        IOperatorMethod, IProject, ITypedef, IVariable)


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


class VersionedItem(Model):
    """ This class is a base class for all project elements that is subject to
    workflow or versions.
    """

    def isCurrent(self):
        """
        Returns True if the element is current.
        """
        return (self.egen == '')

    def sip(self, f, hf, latest_sip):
        """
        Write the code to a SIP file.  This only calls the method for each
        child code.  This method should be reimplemented to write the code
        specific data.  Note that this is in this class only because it is the
        common super-class of the classes that call it.

        f is the file.
        hf is the corresponding header file instance.
        """
        for c in self.content:
            if c.status:
                continue

            vrange = self.get_project().versionRange(c.sgen, c.egen)

            if vrange != '':
                f.write("%%If (%s)\n" % vrange, False)

            if len(c.platforms) != 0:
                f.write("%%If (%s)\n" % " || ".join(c.platforms), False)

            if len(c.features) != 0:
                f.write("%%If (%s)\n" % " || ".join(c.features), False)

            c.sip(f, hf, latest_sip)

            if len(c.features) != 0:
                f.write("%End\n", False)

            if len(c.platforms) != 0:
                f.write("%End\n", False)

            if vrange != '':
                f.write("%End\n", False)

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = []

        if self.status != '':
            xml.append('status="{0}"'.format(self.status))

        if self.sgen != '':
            xml.append('sgen="{0}"'.format(self.sgen))

        if not self.isCurrent():
            xml.append('egen="{0}"'.format(self.egen))

        return xml

    def get_project(self):
        """ Return the project instance. """

        hf = self
        while not isinstance(hf, HeaderFile):
            hf = hf.container

        return hf.project

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
                if arg.unnamed and arg.default is not None:
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

                    name = arg.name
                    if name is None:
                        name = ''

                    arg_names.append(name)

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

                    if arg.name is not None and arg.default is not None:
                        if update:
                            arg.name = None
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

                    if arg.default is not None:
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if arg.name is not None:
                            if update:
                                arg.name = None
                            else:
                                invalid.append("%s() event handler has a named argument" % self._fullName(callable))

        if not skip:
            for arg in callable.args:
                if arg.default is None:
                    continue

                if arg.unnamed:
                    aname = arg.name
                    if aname is None:
                        aname = ''

                    # Check that events are called 'event'.
                    if self._argType(arg).endswith('Event*'):
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if aname != 'event':
                            if update:
                                arg.name = 'event'
                            else:
                                invalid.append("%s() event argument name '%s' is not 'event'" % (self._fullName(callable), aname))

                        continue

                    # Check that objects are called 'object' or 'parent'.
                    if self._argType(arg) == 'QObject*':
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if aname not in ('object', 'parent'):
                            if update:
                                arg.name = 'object'
                            else:
                                invalid.append("%s() QObject argument name '%s' is not 'object' or 'parent'" % (self._fullName(callable), aname))

                        continue

                    # Check that widgets are called 'widget' or 'parent'.
                    if self._argType(arg) == 'QWidget*':
                        if update:
                            arg.unnamed = False
                            updated.append(arg)

                        if aname not in ('widget', 'parent'):
                            if update:
                                arg.name = 'widget'
                            else:
                                invalid.append("%s() QWidget argument name '%s' is not 'widget' or 'parent'" % (self._fullName(callable), aname))

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
                            if aname != lc_s:
                                if update:
                                    arg.name = lc_s
                                else:
                                    invalid.append("%s() '%s' argument name '%s' is not '%s'" % (self._fullName(callable), s, aname, lc_s))

                    # Check for non-standard acronyms.
                    acronyms = ("XML", "URI", "URL")

                    for a in acronyms:
                        if a in aname:
                            if update:
                                arg.unnamed = False
                                updated.append(arg)

                            lc_a = aname.replace(a, a[0] + a[1:].lower())
                            if update:
                                arg.name = lc_a
                            else:
                                invalid.append("%s() argument name '%s' should be '%s'" % (self._fullName(callable), aname, lc_a))

                    # Check the callable has arguments with names and that they
                    # are long enough that they don't need checking manually.
                    if len(aname) <= 2:
                        invalid.append("%s() argument name '%s' is too short" % (self._fullName(callable), aname))

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

        while type(item) is not HeaderFile:
            names.insert(0, item.name)
            item = item.container

        return '::'.join(names)

    def _get_unnamed_callables(self, part):
        """
        A generator for all the checked callables in a part of a project.

        part is the part of the project.
        """
        ptype = type(part)

        if ptype is HeaderFile:
            for sub in part:
                for callable in self._get_unnamed_callables(sub):
                    yield callable
        elif not part.status:
            if ptype is Function:
                for arg in part.args:
                    if arg.unnamed and arg.default is not None:
                        yield part
                        break
            elif ptype in (Constructor, Method):
                if part.access != 'private':
                    for arg in part.args:
                        if arg.unnamed and arg.default is not None:
                            yield part
                            break
            elif ptype in (Class, Namespace):
                for sub in part:
                    for callable in self._get_unnamed_callables(sub):
                        yield callable

    def addVersion(self, vers):
        """ Add a new version to the project. """

        self.versions.append(vers)
        IDirty(self).dirty = True

    def addPlatform(self, plat):
        """ Add a new platform to the project. """

        self.platforms.append(plat)
        IDirty(self).dirty = True

    def addFeature(self, feat):
        """ Add a new feature to the project. """

        self.features.append(feat)
        IDirty(self).dirty = True

    def addExternalModule(self, xm):
        """ Add a new external module to the project. """

        self.externalmodules.append(xm)
        IDirty(self).dirty = True

    def addExternalFeature(self, xf):
        """ Add a new external feature to the project. """

        self.externalfeatures.append(xf)
        IDirty(self).dirty = True

    def addIgnoredNamespace(self, ns):
        """ Add a new ignored namespace to the project. """

        self.ignorednamespaces.append(ns)
        IDirty(self).dirty = True

    def versionRange(self, sgen, egen):
        """
        Return the version string corresponding to a range of generations.

        sgen is the start generation.
        egen is the end generation.
        """
        if sgen == '':
            if egen == '':
                return ""

            return "- " + self.versions[int(egen) - 1]

        if egen == '':
            return self.versions[int(sgen) - 1] + " -"

        return self.versions[int(sgen) - 1] + " - " + self.versions[int(egen) - 1]

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

        # Handle the list of versions.
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

        # Write the project using the current version.
        f.write('<?xml version="1.0"?>\n')
        f.write('<Project version="%u" rootmodule="%s"%s%s%s%s%s%s inputdir="%s" webxmldir="%s" outputdir="%s">\n' % (ProjectVersion, self.rootmodule, vers, plat, feat, xmod, xf, ins, self.inputdir, self.webxmldir, self.outputdir))

        if self.sipcomments != '':
            _writeLiteralXML(f, "sipcomments", self.sipcomments)

        f += 1

        # Give each header file a unique ID, ignoring any current one.  The ID
        # is only used when the project file is written and read.  It is
        # undefined at all other times.
        hfid = 0

        for hdir in self.headers:
            f.write('<HeaderDirectory name="%s" parserargs="%s" inputdirsuffix="%s" filefilter="%s">\n' % (hdir.name, hdir.parserargs, hdir.inputdirsuffix, hdir.filefilter))
            f += 1

            for hf in hdir.content:
                hf.id = hfid
                hf.xml(f)
                hfid += 1

            f -= 1
            f.write('</HeaderDirectory>\n')

        for mod in self.modules:
            f.write('<Module name="%s"' % mod.name)

            if mod.outputdirsuffix != '':
                f.write(' outputdirsuffix="%s"' % mod.outputdirsuffix)

            if mod.version != '':
                f.write(' version="%s"' % mod.version)

            if len(mod.imports) != 0:
                f.write(' imports="{0}"'.format(mod.imports))

            f.write('>\n')

            f += 1

            if mod.directives != '':
                _writeLiteralXML(f, "directives", mod.directives)

            for hf in mod.content:
                f.write('<ModuleHeaderFile id="%u"/>\n' % hf.id)

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

    def descriptiveName(self):
        """
        Return the descriptive name of the project.
        """
        if self.name == '':
            return "Untitled"

        # Remove the standard extension, but leave any non-standard one in
        # place.
        (root, ext) = os.path.splitext(self.name)

        if ext != ".msp":
            root = self.name

        return os.path.basename(root)

    def generateModule(self, mod, od, saveod=True, latest_sip=True):
        """
        Generate the output for a module.  Return True if there was no error.

        mod is the module instance.
        od is the root of the output directory.
        saveod is True if od should be saved in the project.
        """
        # Remember the root directory used.
        od = os.path.abspath(od)

        if saveod and self.outputdir != od:
            self.outputdir = od

        # Generate each applicable header file.
        hfnames = []
        for hf in mod.content:
            f = self._createSIPFile(od, mod, hf)

            if f is None:
                return False

            Logger.log("Generating %s" % f.name)
            hf.sip(f, latest_sip)
            hfnames.append(os.path.basename(f.name))

            f.close()

        f = self._createSIPFile(od, mod)

        if f is None:
            return False

        Logger.log("Generating %s" % f.name)

        rname = self.rootmodule

        if rname != '':
            rname += "."

        if mod.version != '':
            version = ", version=%s" % mod.version
        else:
            version = ""

        if latest_sip:
            f.write("%%Module(name=%s%s, keyword_arguments=\"Optional\"%s)\n\n" % (rname, mod.name, version))
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

        for inc in hfnames:
            f.write("%%Include %s\n" % inc)

        f.close()

        return True

    def _createSIPFile(self, od, mod, hf=None):
        """
        Return a boilerplate SIP file.

        od is the root of the output directory.
        mod is the module instance.
        hf is the header file instance.
        """
        # Work out the name of the file.
        if mod.outputdirsuffix:
            od = os.path.join(od, mod.outputdirsuffix)

        if hf is None:
            fname = mod.name + "mod"
        else:
            (fname, ext) = os.path.splitext(os.path.basename(hf.name))

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
"""// %s generated by MetaSIP on %s
//
// This file is part of the %s Python extension module.
""" % (fname, time.asctime(), mod.name))

            if self.sipcomments:
                f.write("//\n%s\n" % self.sipcomments)

            f.write("\n")
            f.blank()

        return f

    def newModule(self, name, odirsuff="", version="", imports=""):
        """
        Add a new module to the project.

        name is the name of the module.
        odirsuff is the optional output directory suffix.
        version is the module version number.
        imports is the optional space separated list of imported modules.
        """
        mod = Module(name=name, outputdirsuffix=odirsuff, version=version,
                imports=imports.split())
        self.modules.append(mod)

        IDirty(self).dirty = True

        return mod

    def newHeaderDirectory(self, name, pargs="", inputdirsuffix="", filefilter=""):
        """
        Add a new header directory to the project and return it.

        name is the descriptive name of the header directory.
        pargs is the optional string of parser arguments.
        inputdirsuffix when joined to the inputdir gives the absolute name of
        the header directory.
        filefilter is the optional pattern used to select only those files of
        interest.
        """
        hdir = HeaderDirectory(project=self, name=name, parserargs=pargs,
                inputdirsuffix=inputdirsuffix, filefilter=filefilter)
        self.headers.append(hdir)

        IDirty(self).dirty = True

        return hdir

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


class Code(VersionedItem, Annotations):
    """ This class is the base class for all elements of parsed C++ code. """

    def signature(self):
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
        xml += VersionedItem.xmlAttributes(self)

        if len(self.platforms) != 0:
            xml.append('platforms="{0}"'.format(' '.join(self.platforms)))

        if len(self.features) != 0:
            xml.append('features="{0}"'.format(' '.join(self.features)))

        return xml


class Access(Model):
    """ This class is derived by all code that is affected by class access. """

    def sigAccess(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        # Any Qt specific part isn't part of the signature.
        try:
            s = self.access.split()[0]
        except IndexError:
            s = ""

        if s == "signals":
            s = "protected"
        elif s == "public":
            s = ""

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

    # The project.
    project = Instance(IProject)

    def newHeaderFile(self, id, name, md5, parse, status, sgen, egen=''):
        """
        Add a new header file to the project and return it.

        id is the ID.
        name is the path name of the header file excluding the header
        directory.
        md5 is the file's MD5 signature.
        parse is the file parse status.
        status is the file status.
        sgen is the start generation.
        egen is the end generation.
        """
        hf = HeaderFile(project=self.project, id=id, name=name, md5=md5,
                parse=parse, status=status, sgen=sgen, egen=egen)
        self.content.append(hf)

        IDirty(self.project).dirty = True

        return hf

    def addParsedHeaderFile(self, hf, phf):
        """
        Add a parsed header file to the project.

        hf is the header file instance.
        phf is the parsed header file.
        """
        self._mergeCode(hf, phf)

        # Assume something has changed.
        IDirty(self.project).dirty = True

    def _mergeCode(self, dsc, ssc):
        """
        Merge source code into destination code.

        dsc is the destination code instance.
        ssc is the list of parsed source code items.
        """
        generation = str(len(self.project.versions))

        # Go though each existing code item.
        for dsi in dsc.content:
            # Ignore anything that isn't current.
            if not dsi.isCurrent():
                continue

            # Manual code is sticky.
            if isinstance(dsi, ManualCode):
                continue

            # Go through each potentially new code item.
            for ssi in ssc:
                if type(dsi) is type(ssi) and dsi.signature() == ssi.signature():
                    break
            else:
                ssi = None

            if ssi is None:
                # The existing one no longer exists.
                dsi.egen = generation
            else:
                # Discard the new code item.
                ssc.remove(ssi)

                # Merge any child code.
                if isinstance(dsi, (Class, Namespace)):
                    self._mergeCode(dsi, ssi.content)

        # Anything left in the source code is new.
        for ssi in ssc:
            ssi.sgen = generation

            dsc.content.append(ssi)

    def scan(self, sd):
        """ Scan a header directory and process it's contents.

        :param sd:
            is the name of the directory to scan.
        """

        sd = os.path.abspath(sd)
        sdlen = len(sd) + len(os.path.sep)

        # Save the files that were in the directory.
        saved = self[:]

        Logger.log("Scanning header directory %s" % sd)

        for (root, dirs, files) in os.walk(sd):
            for f in files:
                hpath = os.path.join(root, f)
                hfile = hpath[sdlen:]

                # Apply any file name filter.
                if self.filefilter:
                    if not fnmatch.fnmatch(hfile, self.filefilter):
                        continue

                if os.access(hpath, os.R_OK):
                    hf = self._scanHeaderFile(hpath, hfile)

                    for shf in saved:
                        if shf.name == hf.name:
                            saved.remove(shf)
                            break

                    Logger.log("Scanned %s" % hfile)
                else:
                    Logger.log("Skipping unreadable header file %s" % hfile)

        # Anything left in the known list has gone missing or was already
        # missing.
        generation = str(len(self.project.versions))
        for hf in saved:
            if hf.isCurrent():
                Logger.log("%s is no longer in the header directory" % hf.name)

                # If it is unknown then just forget about it.
                if hf.status == "unknown":
                    self.content.remove(hf)
                else:
                    hf.egen = generation

        # Assume something has changed.
        IDirty(self.project).dirty = True

    def _scanHeaderFile(self, hpath, hfile):
        """
        Scan a header file and return the header file instance.

        hpath is the full pathname of the header file.
        hfile is the pathname relative to the header directory.
        """
        # Calculate the MD5 signature ignoring any comments.  Note that nested
        # C style comments aren't handled very well.
        m = hashlib.md5()

        f = open(hpath, "r")
        src = f.read()
        f.close()

        lnr = 1
        state = "copy"
        copy = ""
        idx = 0

        for ch in src:
            # Get the previous character.
            if idx > 0:
                prev = src[idx - 1]
            else:
                prev = ""

            idx += 1

            # Line numbers must be accurate.
            if ch == "\n":
                lnr += 1

            # Handle the end of a C style comment.
            if state == "ccmnt":
                if ch == "/" and prev == "*":
                    state = "copy"

                continue

            # Handle the end of a C++ style comment.
            if state == "cppcmnt":
                if ch == "\n":
                    state = "copy"

                continue

            # We must be in the copy state.

            if ch == "*" and prev == "/":
                # The start of a C style comment.
                state = "ccmnt"
                continue

            if ch == "/" and prev == "/":
                # The start of a C++ style comment.
                state = "cppcmnt"
                continue

            # At this point we know the previous character wasn't part of a
            # comment.
            if prev:
                m.update(prev.encode(f.encoding))

        # Note that we didn't add the last character, but it would normally be
        # a newline.
        sig = m.hexdigest()

        # See if we already know about the file.
        for hf in self.content:
            if hf.name == hfile:
                if hf.isCurrent():
                    if hf.md5 != sig:
                        hf.md5 = sig
                        hf.parse = "needed"

                    return hf

                break

        # It is a new file, or the reappearence of an old one.
        return self.newHeaderFile('', hfile, sig, 'needed', 'unknown',
                str(len(self.project.versions)))


@implements(IHeaderFile)
class HeaderFile(VersionedItem):
    """ This class represents a project header file. """

    # The project.
    project = Instance(IProject)

    def sip(self, f, latest_sip):
        """
        Write the header file to a SIP file.

        f is the output file.
        """
        if self.status != '':
            return 

        # See if we need a %ModuleCode directive for things which will be
        # implemented at the module level.
        for c in self.content:
            if c.status != '':
                continue

            if isinstance(c, Function) or isinstance(c, OperatorFunction) or isinstance(c, Variable) or isinstance(c, Enum):
                vrange = self.project.versionRange(self.sgen, self.egen)

                if vrange:
                    f.write("%%If (%s)\n" % vrange, False)

                f.write(
"""%%ModuleCode
#include <%s>
%%End
""" % self.name)

                if vrange:
                    f.write("%End\n", False)

                f.blank()

                break

        super().sip(f, self, latest_sip)

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

    def xml(self, f):
        """ Write the header file to an XML file. """

        f.write('<HeaderFile%s>\n' % _attrsAsString(self))

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

        f.write('</HeaderFile>\n')

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = super().xmlAttributes()

        xml.append('id="{0}"'.format(self.id))
        xml.append('name="{0}"'.format(self.name))
        xml.append('md5="{0}"'.format(self.md5))

        if self.parse != '':
            xml.append('parse="{0}"'.format(self.parse))

        return xml


@implements(IArgument)
class Argument(Annotations):
    """ This class represents an argument. """

    def signature(self, callable):
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

    def signature(self):
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

        s += self.sigAccess()

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

    def sip(self, f, hf, latest_sip):
        """
        Write the class to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        if self.status != '':
            return 

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
            f.write("#include <%s>\n" % hf.name, False)

        f.write("%End\n", False)

        f.blank()

        if self.typecode:
            _writeCodeSIP(f, "%TypeCode", self.typecode, False)

        if self.convtotypecode:
            _writeCodeSIP(f, "%ConvertToTypeCode", self.convtotypecode, False)

        if self.subclasscode:
            _writeCodeSIP(f, "%ConvertToSubClassCode", self.subclasscode)

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

        for c in self.content:
            if c.status != '':
                continue

            if isinstance(c, Access):
                if access != c.access:
                    f -= 1
                    access = c.access

                    if access != '':
                        astr = access
                    else:
                        astr = "public"

                    f.blank()
                    f.write(astr + ":\n")
                    f += 1

            vrange = self.get_project().versionRange(c.sgen, c.egen)

            if vrange != '':
                f.write("%%If (%s)\n" % vrange, False)

            if len(c.platforms) != 0:
                f.write("%%If (%s)\n" % " || ".join(c.platforms), False)

            if len(c.features) != 0:
                f.write("%%If (%s)\n" % " || ".join(c.features), False)

            c.sip(f, hf, latest_sip)

            if len(c.features) != 0:
                f.write("%End\n", False)

            if len(c.platforms) != 0:
                f.write("%End\n", False)

            if vrange != '':
                f.write("%End\n", False)

        f -= 1
        f.write("};\n")

        f.blank()

    def xml(self, f):
        """ Write the class to an XML file. """

        f.write('<Class%s>\n' % _attrsAsString(self))

        _writeDocstringXML(f, self.docstring)

        if self.typeheadercode:
            _writeLiteralXML(f, "typeheadercode", self.typeheadercode)

        if self.typecode:
            _writeLiteralXML(f, "typecode", self.typecode)

        if self.convtotypecode:
            _writeLiteralXML(f, "convtotypecode", self.convtotypecode)

        if self.subclasscode:
            _writeLiteralXML(f, "subclasscode", self.subclasscode)

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return self.expand_type(self.rtype) + self.name + "(" + ", ".join([a.signature(self) for a in self.args]) + ")"

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

    def sip(self, f, hf, latest_sip):
        """
        Write the callable to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
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
        """
        Write any docstring to a SIP file.

        f is the file.
        """
        _writeDocstringSIP(f, self.docstring)

    def sipMethcode(self, f):
        """
        Write any method code to a SIP file.

        f is the file.
        """
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
        """
        Write any docstring to an XML file.

        f is the file.
        """
        _writeDocstringXML(f, self.docstring)

    def xmlMethcode(self, f):
        """
        Write any method code to an XML file.

        f is the file.
        """
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
class EnumValue(VersionedItem, Annotations):
    """ This class represents an enum value. """

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return self.user()

    def user(self):
        """
        Return a user friendly representation of the enum value.
        """
        return self.name

    def sip(self, latest_sip):
        """
        Return the enum value suitable for writing to a SIP file.
        """
        return self.name + self.sipAnnos()

    def xml(self, f):
        """ Write the enum value to an XML file. """

        f.write('<EnumValue%s/>\n' % _attrsAsString(self))

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        xml = Annotations.xmlAttributes(self)
        xml += VersionedItem.xmlAttributes(self)

        xml.append('name="{0}"'.format(self.name))

        return xml


@implements(IEnum)
class Enum(Code, Access):
    """ This class represents an enum. """

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature() + self.sigAccess()

    def user(self):
        """
        Return a user friendly representation of the enum.
        """
        s = "enum"

        if self.name != '':
            s += " " + self.name

        return s

    def sip(self, f, hf, latest_sip):
        """
        Write the enum to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        f.blank()

        f.write("enum")

        if self.name != '':
            f.write(" " + self.name)

        f.write(self.sipAnnos() + "\n{\n")
        f += 1

        for e in self.content:
            if e.status != '':
                continue

            vrange = self.get_project().versionRange(e.sgen, e.egen)

            if vrange != '':
                f.write("%%If (%s)\n" % vrange, False)

            f.write(e.sip(latest_sip) + ",\n")

            if vrange != '':
                f.write("%End\n", False)

        f -= 1
        f.write("};\n")
        f.blank()

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

    def signature(self):
        """ Return a C/C++ representation for comparison purposes. """

        return super().signature() + self.sigAccess()

    def xmlAttributes(self):
        """ Return the XML attributes as a list. """

        return Callable.xmlAttributes(self) + Access.xmlAttributes(self)


@implements(IConstructor)
class Constructor(ClassCallable):
    """ This class represents a constructor. """

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = super().signature()

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

    def sip(self, f, hf, latest_sip):
        """
        Write the constructor to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        if self.explicit:
            f.write("explicit ")

        super().sip(f, hf, latest_sip)

        if self.pyargs != '' or self.hasPyArgs():
            f.write(" [(%s)]" % ", ".join([a.user(self) for a in self.args]))

        f.write(";\n")

        self.sipDocstring(f)
        self.sipMethcode(f)

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = self.name + self.sigAccess()

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

    def sip(self, f, hf, latest_sip):
        """
        Write the destructor to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        if self.virtual:
            f.write("virtual ")

        f.write("~" + self.name + "()" + self.sipAnnos() + ";\n")

        _writeMethCodeSIP(f, self.methcode)
        _writeVirtCodeSIP(f, self.virtcode)

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = "operator " + super().signature()

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

    def sip(self, f, hf, latest_sip):
        """
        Write the operator cast to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        f.write("operator ")

        super().sip(f, hf, latest_sip)

        if self.const:
            f.write(" const")

        f.write(";\n")

        self.sipMethcode(f)

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = ""

        if self.virtual:
            s += "virtual "

        if self.static:
            s += "static "

        s += self.expand_type(self.rtype) + self.name + "(" + ", ".join([a.signature(self) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sigAccess()

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

    def sip(self, f, hf, latest_sip):
        """
        Write the method to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        s = ""

        if self.virtual:
            s += "virtual "

        s += self.expand_type(self.rtype) + "operator" + self.name + "(" + ", ".join([a.signature(self) for a in self.args]) + ")"

        if self.const:
            s += " const"

        if self.abstract:
            s += " = 0"

        s += self.sigAccess()

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

    def sip(self, f, hf, latest_sip):
        """
        Write the operator to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
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

    def sip(self, f, hf, latest_sip):
        """
        Write the destructor to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        super().sip(f, hf, latest_sip)
        f.write(";\n")
        self.sipDocstring(f)
        self.sipMethcode(f)

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return self.expand_type(self.rtype) + "operator" + self.name + "(" + ", ".join([a.signature(self) for a in self.args]) + ")"

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

    def sip(self, f, hf, latest_sip):
        """
        Write the operator to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        f.write(self.returnType(ignore_namespaces=True) + "operator" + self.name)

        if self.pyargs != '':
            f.write(self.pyargs)
        else:
            f.write("(" + ", ".join([a.sip(self, latest_sip) for a in self.args]) + ")")

        f.write(self.sipAnnos())

        f.write(";\n")

        self.sipMethcode(f)

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature() + self.sigAccess()

    def user(self):
        """
        Return a user friendly representation of the variable.
        """
        s = self.expand_type(self.type, self.name) + self.sipAnnos()

        if self.static:
            s = "static " + s

        return s

    def sip(self, f, hf, latest_sip):
        """
        Write the variable to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
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

    def user(self):
        """
        Return a user friendly representation of the typedef.
        """
        return "typedef " + self.expand_type(self.type, self.name) + self.sipAnnos()

    def sip(self, f, hf, latest_sip):
        """
        Write the code to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        f.write("typedef " + self.expand_type(self.type, self.name, ignore_namespaces=True) + self.sipAnnos() + ";\n")

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

    def sip(self, f, hf, latest_sip):
        """
        Write the code to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        if self.status:
            return 

        if self.name in self.get_project().ignorednamespaces:
            super().sip(f, hf, latest_sip)
            return

        f.blank()

        f.write("namespace " + self.name + "\n{\n")

        f.write("%TypeHeaderCode\n", False)

        if self.typeheadercode:
            f.write(self.typeheadercode + "\n", False)
        else:
            f.write("#include <%s>\n" % hf.name, False)

        f.write("%End\n", False)

        f.blank()

        f += 1
        super().sip(f, hf, latest_sip)
        f -= 1

        f.write("};\n")

        f.blank()

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature() + self.sigAccess()

    def user(self):
        """
        Return a user friendly representation of the opaque class.
        """
        return "class " + self.name + self.sipAnnos()

    def sip(self, f, hf, latest_sip):
        """
        Write the code to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        f.write("class " + self.name + self.sipAnnos() + ";\n")

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

    def signature(self):
        """
        Return a C/C++ representation for comparison purposes.
        """
        return super().signature() + self.sigAccess()

    def user(self):
        """
        Return a user friendly representation of the manual code.
        """
        return self.precis

    def sip(self, f, hf, latest_sip):
        """
        Write the code to a SIP file.

        f is the file.
        hf is the corresponding header file instance.
        """
        if self.body:
            f.write("// " + self.precis + "\n" + self.body + "\n", False)
        elif self.precis.startswith('%'):
            f.write(self.precis + "\n", False)
        else:
            f.write(self.precis + ";\n")

        _writeDocstringSIP(f, self.docstring)
        _writeMethCodeSIP(f, self.methcode)

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


def escape(s):
    """
    Return an XML escaped string.
    """
    return saxutils.escape(s, {'"': '&quot;'})
