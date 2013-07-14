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
import subprocess
import tempfile

from dip.model import implements, Instance, Model

from .interfaces.project import ICodeContainer, IProject

from .logger import Logger
from .Parser import ParserBase, optAttribute
from .Project import (Function, Argument, Variable, Typedef, OpaqueClass,
        Class, Constructor, Destructor, Method, Enum, EnumValue,
        OperatorFunction, OperatorMethod, Namespace, OperatorCast)


# The tuple of code items generated by Qt's Q_OBJECT macro to automatically
# ignore.
_Q_OBJECT = (
    # These are for Qt v3 only.
    "virtual QMetaObject *metaObject() const",
    "virtual const char *className() const",
    "virtual void *qt_cast(const char *)",
    "virtual bool qt_invoke(int, QUObject *)",
    "virtual bool qt_emit(int, QUObject *)",
    "virtual bool qt_property(int, int, QVariant *)",
    "static bool qt_static_property(QObject *, int, int, QVariant *)",
    "static QMetaObject *staticMetaObject()",
    "QObject *qObject()",

    # These are for Qt v3 and v4.
    "static QString tr(const char *, const char * = 0)",
    "static QString trUtf8(const char *, const char * = 0)",

    # These are for Qt v4 only.
    "virtual const QMetaObject *metaObject() const",
    "static const QMetaObject staticMetaObject",
    "virtual void *qt_metacast(const char *)",
    "virtual int qt_metacall(QMetaObject::Call, int, void **)",
)


def _fixQt(code):
    """ Update the status for code items generated from Qt's Q_OBJECT macro.
    At the moment we don't check argument lists as they haven't been set up
    yet.

    :param code:
        is the code instance.
    """

    # FIXME: We can now check the full signature.
    def leading(s):
        """ Return the start of the string up to the first opening parenthesis.
        """

        idx = s.find("(")

        if idx > 0:
            s = s[:idx]

        return s

    cs = leading(code.user())

    for qo in _Q_OBJECT:
        if cs == leading(qo):
            code.status = "ignored"
            break


class _Access(object):
    """
    This class is derived by all code that is affected by class access.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the instance.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        self.access = attrs.get('access', '')
        if self.access == 'public':
            self.access = ''


class _ScopedItem(object):
    """
    This class is a base class for any entity that is part of a scope.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the instance.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        # Not everything has a name (some structs for example).
        try:
            self.name = attrs["name"]
        except KeyError:
            self.name = None

        # Not everything has an ID.
        try:
            self.id = attrs["id"]
        except KeyError:
            self.id = None

        if self.id:
            parser.byid[self.id] = self

        # The root namespace doesn't have a context.
        try:
            self.context = attrs["context"]
        except KeyError:
            self.context = None

        # Namespaces don't have file IDs or line numbers.
        try:
            self.file = attrs["file"]
        except KeyError:
            self.file = None

        try:
            self.line = int(attrs["line"])
        except KeyError:
            self.line = None

        parser.scopeditems.append(self)

    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the item for when it is used as a
        type.

        parser is the parser instance.
        """
        assert prefix_ok is None

        sl = []

        # Prefix it by any scope.
        if self.name:
            sl.append(self.name)

        pc = parser.byid[self.context]

        # Watch for the root namespace which doesn't have a context.
        while isinstance(pc, _ScopedItem) and pc.context is not None:
            sl.insert(0, pc.name)
            pc = parser.byid[pc.context]

        return "::".join(sl), True


class _Namespace(_ScopedItem):
    """
    This class represents a GCC-XML namespace entity.
    """
    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        tci = Namespace(name=self.name, container=scope)
        scope.content.append(tci)

        parser.transformScope(tci, self)


class _Class(_ScopedItem, _Access):
    """
    This class represents a GCC-XML class entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)
        _Access.__init__(self, parser, attrs)

        self.bases = optAttribute(attrs, "bases")

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        bl = []

        for bid in self.bases.split():
            sbid = bid.split(":")

            if len(sbid) == 1:
                acc = "public"
            else:
                acc = sbid[0]
                bid = sbid[1]

            bl.append("%s %s" % (acc, parser.asType(bid)))

        # Automatically ignore non-public classes.
        status = 'unknown' if self.access == '' else 'ignored'

        tci = Class(name=self.name, container=scope, bases=', '.join(bl),
                struct=False, access=self.access, status=status)
        scope.content.append(tci)

        parser.transformScope(tci, self)


class _Struct(_ScopedItem, _Access):
    """
    This class represents a GCC-XML struct entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)
        _Access.__init__(self, parser, attrs)

        self.incomplete = bool(int(optAttribute(attrs, "incomplete", "0")))

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        if self.name is None:
            return

        if self.incomplete:
            scope.content.append(
                    OpaqueClass(name=self.name, container=scope,
                            access=self.access, status='ignored'))
        else:
            # Automatically ignore non-public classes.
            status = 'unknown' if self.access == '' else 'ignored'

            tci = Class(name=self.name, container=scope, struct=True,
                    access=self.access, status=status)
            scope.content.append(tci)

            parser.transformScope(tci, self)


# Treat a union as a struct so that it appears in the .sip file where it can be
# handled with handwritten code.
_Union = _Struct


class _Callable(_ScopedItem):
    """
    This class is the base class for callable code.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)

        self.args = []


class _ClassCallable(_Callable, _Access):
    """
    This class is the base class for callable code in a class context.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _Callable.__init__(self, parser, attrs)
        _Access.__init__(self, parser, attrs)


class _Constructor(_ClassCallable):
    """
    This class represents a GCC-XML constructor entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ClassCallable.__init__(self, parser, attrs)

        self.explicit = bool(int(optAttribute(attrs, "explicit", "0")))

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        # Don't specify explicit unless it's applicable.
        if len(self.args) == 1:
            explicit = self.explicit
        else:
            explicit = False

        tci = Constructor(name=self.name, container=scope, access=self.access,
                explicit=explicit)

        _transformArgs(parser, self.args, tci.args)

        scope.content.append(tci)


class _Destructor(_ScopedItem, _Access):
    """
    This class represents a GCC-XML destructor entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)
        _Access.__init__(self, parser, attrs)

        self.virtual = bool(int(optAttribute(attrs, "virtual", "0")))

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        scope.content.append(
                Destructor(name=self.name, container=scope, access=self.access,
                        virtual=self.virtual))


class _Converter(_ClassCallable):
    """
    This class represents a GCC-XML converter entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        super().__init__(parser, attrs)

        self.returns = attrs["returns"]
        self.const = bool(int(optAttribute(attrs, "const", "0")))

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        name = parser.asType(self.returns)
        if name is not None:
            tci = OperatorCast(name=name, container=scope, access=self.access,
                    const=self.const)

            scope.content.append(tci)


class _Method(_ClassCallable):
    """
    This class represents a GCC-XML method entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ClassCallable.__init__(self, parser, attrs)

        self.returns = attrs["returns"]
        self.virtual = bool(int(optAttribute(attrs, "virtual", "0")))
        self.const = bool(int(optAttribute(attrs, "const", "0")))
        self.static = bool(int(optAttribute(attrs, "static", "0")))
        self.abstract = bool(int(optAttribute(attrs, "pure_virtual", "0")))

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        # Private methods are ignored by default.
        status = 'ignored' if self.access.startswith('private') else 'unknown'

        tci = Method(name=self.name, container=scope, access=self.access,
                rtype=parser.asType(self.returns), virtual=self.virtual,
                const=self.const, static=self.static, abstract=self.abstract,
                status=status)

        _transformArgs(parser, self.args, tci.args)

        _fixQt(tci)

        scope.content.append(tci)


class _OperatorMethod(_ClassCallable):
    """
    This class represents a GCC-XML operatormethod entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ClassCallable.__init__(self, parser, attrs)

        self.returns = attrs["returns"]
        self.virtual = bool(int(optAttribute(attrs, "virtual", "0")))
        self.const = bool(int(optAttribute(attrs, "const", "0")))
        self.abstract = bool(int(optAttribute(attrs, "pure_virtual", "0")))

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        # Private methods are ignored by default.
        status = 'ignored' if self.access.startswith('private') else 'unknown'

        tci = OperatorMethod(name=self.name, container=scope,
                access=self.access, rtype=parser.asType(self.returns),
                virtual=self.virtual, const=self.const, abstract=self.abstract,
                status=status)

        _transformArgs(parser, self.args, tci.args)

        scope.content.append(tci)


class _Function(_Callable):
    """
    This class represents a GCC-XML function entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _Callable.__init__(self, parser, attrs)

        self.returns = attrs["returns"]

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        tci = Function(name=self.name, container=scope,
                rtype=parser.asType(self.returns))

        _transformArgs(parser, self.args, tci.args)

        scope.content.append(tci)


class _OperatorFunction(_Callable):
    """
    This class represents a GCC-XML operatorfunction entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _Callable.__init__(self, parser, attrs)

        self.returns = attrs["returns"]

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        tci = OperatorFunction(name=self.name, container=scope,
                rtype=parser.asType(self.returns))

        _transformArgs(parser, self.args, tci.args)

        scope.content.append(tci)


class _Variable(_ScopedItem, _Access):
    """
    This class represents a GCC-XML variable entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)
        _Access.__init__(self, parser, attrs)

        self.type_id = attrs["type"]

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        status = 'ignored' if self.access.startswith('protected') else 'unknown'

        tci = Variable(name=self.name, type=parser.asType(self.type_id),
                static=isinstance(scope, Class), access=self.access,
                status=status)

        _fixQt(tci)

        scope.content.append(tci)


class _Field(_Variable):
    """
    This class represents a GCC-XML field entity.
    """
    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        t = parser.asType(self.type_id)

        if t:
            scope.content.append(
                    Variable(name=self.name, type=t, static=False,
                            access=self.access))


class _Enumeration(_ScopedItem, _Access):
    """
    This class represents a GCC-XML enumeration entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)
        _Access.__init__(self, parser, attrs)

        # Deal with anonymous enums.
        if self.name.startswith("."):
            self.name = ""

        self.values = []

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        # We don't support private enums.  We didn't filter it out before
        # because it may have been used as a type.
        if self.access.startswith("private"):
            return

        tci = Enum(name=self.name, access=self.access)

        for e in self.values:
            tci.content.append(EnumValue(name=e.name))

        scope.content.append(tci)


class _EnumValue(object):
    """
    This class represents a GCC-XML enum value entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        self.name = attrs["name"]


class _Typedef(_ScopedItem):
    """
    This class represents a GCC-XML typedef entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _ScopedItem.__init__(self, parser, attrs)

        self.type_id = attrs["type"]

    def transform(self, parser, scope):
        """
        Transform the entity.

        parser is the parser instance.
        scope is the scope to append the transformed entity to.
        """
        t = parser.asType(self.type_id)

        # Ignore unsupported types - probably only those defined in terms of
        # a MethodType (eg. typedef foo_t (scope::*bar)();).
        if t:
            scope.content.append(Typedef(name=self.name, type=t))


class _FunctionType(object):
    """
    This class represents a GCC-XML function type entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        self.returns = attrs["returns"]
        self.args = []

        parser.byid[attrs["id"]] = self

    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the type.

        parser is the parser instance.
        """
        assert prefix_ok is None

        al = []
        for a in self.args:
            al.append(parser.asType(a.type_id))

        return parser.asType(self.returns) + " (%s)(" + ", ".join(al) + ")", False


class _FundamentalType(object):
    """
    This class represents a GCC-XML fundamental type entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        self.name = attrs["name"]

        parser.byid[attrs["id"]] = self

    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the type.

        parser is the parser instance.
        """
        assert prefix_ok is None

        # Map some of GCC-XML's verbose types to something SIP can handle.
        type_map = {
            "short int": "short",
            "short unsigned int": "unsigned short",
            "long unsigned int": "unsigned long",
            "long long unsigned int": "unsigned long long"
        }

        return type_map.get(self.name, self.name), True


class _IndirectType(object):
    """
    This class represents the base type for all GCC-XML indirect type
    entities, ie. those linked to other types through a type attribute.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        self.type_id = attrs["type"]

        parser.byid[attrs["id"]] = self

    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the type that this type indirects
        to.

        parser is the parser instance.
        """
        return parser.asInnerType(self.type_id, prefix_ok)


class _ReferenceType(_IndirectType):
    """
    This class represents a GCC-XML reference type entity.
    """
    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the type.

        parser is the parser instance.
        """
        s, _ = super().asType(parser, prefix_ok)

        if s[-1] not in "*&":
            s += " "

        return s + "&", False


class _PointerType(_IndirectType):
    """
    This class represents a GCC-XML pointer type entity.
    """
    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the type.

        parser is the parser instance.
        """
        s, _ = super().asType(parser, prefix_ok)

        rt = parser.byid[self.type_id]

        if isinstance(rt, _FunctionType):
            # If the base type is a function then put the pointer immediately
            # before the function name marker.
            s = s % "*%s"
        else:
            if s[-1] not in "*&":
                s += " "

            s += "*"

        return s, False


class _CvQualifiedType(_IndirectType):
    """
    This class represents a GCC-XML reference type entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        _IndirectType.__init__(self, parser, attrs)

        self.const = bool(int(optAttribute(attrs, "const", "0")))

    def asType(self, parser, prefix_ok):
        """
        Return the string representation of the type.

        parser is the parser instance.
        """
        s, prefix_ok = super().asType(parser, prefix_ok)

        if self.const:
            if prefix_ok:
                s = "const " + s
            else:
                s = s + " const"

        return s, False


class _Argument(object):
    """
    This class represents a GCC-XML argument entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        self.type_id = attrs["type"]
        self.name = optAttribute(attrs, "name")
        self.default = optAttribute(attrs, "default")

        # Negative numbers are represented as hex for some reason.
        if self.default.startswith('-0x'):
            self.default = str(int(self.default, base=16))

        # These are Qt specific and should be moved to a plugin.
        if self.default == 'QLatin1Char(32)':
            self.default = "QLatin1Char(' ')"


class _Ellipsis(object):
    """
    This class represents a GCC-XML ellipsis entity.
    """
    def __init__(self, parser, attrs):
        """
        Initialise the entity.

        parser is the parser instance.
        attr is the entity's attribute dictionary.
        """
        pass


def _transformArgs(parser, gargs, pargs):
    """
    Transform a list of GCC-XML arguments and append them to a list of project
    arguments.

    parser is the parser instance.
    gargs is the list of GCC-XML arguments.
    pargs is the list of project arguments.
    """
    for a in gargs:
        if isinstance(a, _Ellipsis):
            pa = Argument(type="...")
        else:
            # GCC-XML doesn't add the scope to default values of enums so we
            # try and fix it here.
            typ = parser.asType(a.type_id)
            if typ is None:
                continue

            # For Qt5.
            if typ.endswith('::QPrivateSignal'):
                continue

            default = a.default

            if (default and ("::" in typ) and ("::" not in default) and
                ("()" not in default) and
                (default not in ("0", "NULL", "true", "TRUE", "false", "FALSE"))):
                default = typ[:typ.rfind("::")] + "::" + default

            pa = Argument(type=typ, name=a.name, default=default)

        pargs.append(pa)


@implements(ICodeContainer)
class _CodeContainer(Model):
    """ An internal class that implements the root of the transformed items.
    """

    # The project.
    project = Instance(IProject)


class GccXMLParser(ParserBase):
    """
    This class implements a C++ parser based on GCC-XML.  It should be used as
    an abstract class with a derived class handling any user interaction.
    """
    def classMap(self):
        """
        Return a dictionary of XML entity names and their corresponding
        classes.  These are the ones that don't need any special handling.
        """
        return {"class":            _Class,
                "typedef":          _Typedef,
                "fundamentaltype":  _FundamentalType,
                "referencetype":    _ReferenceType,
                "pointertype":      _PointerType,
                "arraytype":        _PointerType,
                "cvqualifiedtype":  _CvQualifiedType}

    def parse(self, project, input_dir, hdir, hf, pathname):
        """
        Parse a file and return the parsed file instance or None if there was
        an error.

        project is the project.
        input_dir is the root input directory.
        hdir is the header directory instance.
        hf is the header file instance.
        pathname is the name of the actual file to parse.
        """
        self._pathname = pathname
        iname = os.path.join(tempfile.gettempdir(), hf.name + '.tmp')

        argv = ['gccxml']
        argv.append(hdir.parserargs)
        argv.append(self._pathname)
        argv.append('-fxml=' + iname)

        # We use shell=True and a string argv for OS/X - but I don't understand
        # why it's needed.
        args = ' '.join(argv)

        Logger.log(args)

        cwd = os.getcwd()
        os.chdir(input_dir)

        try:
            output = subprocess.check_output(args, shell=True,
                    stderr=subprocess.STDOUT)
            rc = 0
        except subprocess.CalledProcessError as exc:
            output = exc.output
            rc = exc.returncode

        os.chdir(cwd)

        # Log any output.
        for line in output.decode().rstrip().split('\n'):
            Logger.log(line.rstrip())

        if rc != 0:
            try:
                os.remove(iname)
            except:
                pass

            sig = rc & 0x7f
            rc >>= 8

            if sig:
                self.diagnostic = "%s killed by signal %d" % (argv[0], sig)
            else:
                self.diagnostic = "%s failed with exit code %d" % (argv[0], rc)

            Logger.log(self.diagnostic)

            return None

        Logger.log("Parsing %s output for %s" % (argv[0], self._pathname))

        # Initialise the parser state.  The first pass is to read in the
        # GCC-XML output filtering out stuff we definately don't need.  The
        # second pass is to convert it into the internal project format.  We
        # need to do two passes because GCC-XML does not ensure that everything
        # is defined by the time it is referenced.
        self.byid = {}
        self.scopeditems = []
        self._rootns = None
        self._args = None
        self._evalues = None
        self._fileid = None

        rc = super().parse(iname)

        #os.remove(iname)

        if not rc:
            return None

        # Now convert it to the internal format.
        phf = _CodeContainer(project=project)

        self.transformScope(phf, self._rootns)

        return phf.content

    def namespaceStart(self, attrs):
        """
        Called at the start of a namespace.

        attrs is the dictionary of attributes.
        """
        ns = _Namespace(self, attrs)

        # Remember the root namespace.
        if ns.name == '::':
            self._rootns = ns

    def fieldStart(self, attrs):
        """
        Called at the start of a field.

        attrs is the dictionary of attributes.
        """
        # At the moment we only support public variables.  We could support
        # protected ones in the future, but we will never support private ones.
        if optAttribute(attrs, "access") == "private":
            return

        _Field(self, attrs)

    def variableStart(self, attrs):
        """
        Called at the start of a variable.

        attrs is the dictionary of attributes.
        """
        # At the moment we only support public variables.  We could support
        # protected ones in the future, but we will never support private ones.
        if optAttribute(attrs, "access") == "private":
            return

        if optAttribute(attrs, "artificial", None) is not None:
            return

        _Variable(self, attrs)

    def unionStart(self, attrs):
        """
        Called at the start of a union.

        attrs is the dictionary of attributes.
        """
        _Union(self, attrs)

    def structStart(self, attrs):
        """
        Called at the start of a structure.

        attrs is the dictionary of attributes.
        """
        _Struct(self, attrs)

    def constructorStart(self, attrs):
        """
        Called at the start of a constructor.

        attrs is the dictionary of attributes.
        """
        if optAttribute(attrs, "artificial", None) is not None:
            return

        self._args = _Constructor(self, attrs).args

    def constructorEnd(self):
        """
        Called at the end of a constructor.
        """
        self._args = None

    def destructorStart(self, attrs):
        """
        Called at the start of a destructor.

        attrs is the dictionary of attributes.
        """
        if optAttribute(attrs, "artificial", None) is not None:
            return

        _Destructor(self, attrs)

    def converterStart(self, attrs):
        """
        Called at the start of a converter.

        attrs is the dictionary of attributes.
        """
        _Converter(self, attrs)

    def methodStart(self, attrs):
        """
        Called at the start of a method.

        attrs is the dictionary of attributes.
        """
        self._args = _Method(self, attrs).args

    def methodEnd(self):
        """
        Called at the end of a method.
        """
        self._args = None

    def operatormethodStart(self, attrs):
        """
        Called at the start of an operatormethod.

        attrs is the dictionary of attributes.
        """
        self._args = _OperatorMethod(self, attrs).args

    def operatormethodEnd(self):
        """
        Called at the end of an operatormethod.
        """
        self._args = None

    def functionStart(self, attrs):
        """
        Called at the start of a function.

        attrs is the dictionary of attributes.
        """
        self._args = _Function(self, attrs).args

    def functionEnd(self):
        """
        Called at the end of a function.
        """
        self._args = None

    def functiontypeStart(self, attrs):
        """
        Called at the start of a function type.

        attrs is the dictionary of attributes.
        """
        self._args = _FunctionType(self, attrs).args

    def functiontypeEnd(self):
        """
        Called at the end of a function type.
        """
        self._args = None

    def operatorfunctionStart(self, attrs):
        """
        Called at the start of an operatorfunction.

        attrs is the dictionary of attributes.
        """
        self._args = _OperatorFunction(self, attrs).args

    def operatorfunctionEnd(self):
        """
        Called at the end of an operatorfunction.
        """
        self._args = None

    def argumentStart(self, attrs):
        """
        Called at the start of an argument.

        attrs is the dictionary of attributes.
        """
        if self._args is not None:
            self._args.append(_Argument(self, attrs))

    def ellipsisStart(self, attrs):
        """
        Called at the start of an ellipsis.

        attrs is the dictionary of attributes.
        """
        if self._args is not None:
            self._args.append(_Ellipsis(self, attrs))

    def enumerationStart(self, attrs):
        """
        Called at the start of an enumeration.

        attrs is the dictionary of attributes.
        """
        self._evalues = _Enumeration(self, attrs).values

    def enumvalueStart(self, attrs):
        """
        Called at the start of an enum value.

        attrs is the dictionary of attributes.
        """
        self._evalues.append(_EnumValue(self, attrs))

    def fileStart(self, attrs):
        """
        Called at the start of a file.

        attrs is the dictionary of attributes.
        """
        # Remember the file ID of the file being parsed.
        name = attrs["name"]
        if os.path.isabs(name):
            if name == self._pathname:
                self._fileid = attrs["id"]
        else:
            if self._pathname.endswith(name[1:]):
                self._fileid = attrs["id"]

    def transformScope(self, container, scope):
        """
        Transform a scope (either a namespace or a class) from the stripped
        down GCC-XML format to the internal project format.

        container is the code container to add to.
        scope is the scope to convert.
        """
        # Transform each scoped item.
        for si in self._sorted_scope(scope):
            si.transform(self, container)

    def _sorted_scope(self, unsorted):
        """
        Return a list of the items in a scope sorted by line number.

        unsorted is the scope.
        """
        # Return the cached list if we have already built it.
        try:
            return unsorted._cache
        except AttributeError:
            pass

        ssl = []

        for si in self.scopeditems:
            # Skip if this item is part of the scope.
            if si is unsorted or si.context != unsorted.id:
                continue

            # If we don't know the item's position then it must be a namespace
            # so sort it's contents and take the position of it's first
            # "child".
            if si.file is None or si.line is None:
                si_sorted = self._sorted_scope(si)

                # Skip it if it was empty.
                if len(si_sorted) == 0:
                    continue

                si.file = si_sorted[0].file
                si.line = si_sorted[0].line

            if si.file == self._fileid:
                ssl.append(si)

        ssl.sort(key=lambda k: k.line)
        unsorted._cache = ssl

        return ssl

    def asType(self, type_id):
        """
        Return the string representation of a type or None if it is an
        unsupported type.

        type_id is the type ID.
        """
        type_str, _ = self.asInnerType(type_id, None)

        return type_str

    def asInnerType(self, type_id, prefix_ok):
        """
        Return the string representation of a type or None if it is an
        unsupported type.

        type_id is the type ID.
        """
        try:
            type_str, prefix_ok = self.byid[type_id].asType(self, prefix_ok)
        except KeyError:
            type_str = None

        return type_str, prefix_ok
