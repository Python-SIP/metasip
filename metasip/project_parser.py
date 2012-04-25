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

from .Parser import optAttribute, ParserBase
from .Project import (Argument, Class, Constructor, Destructor, Enum,
        EnumValue, Function, ManualCode, Method, Namespace, OpaqueClass,
        OperatorCast, OperatorFunction, OperatorMethod, Project, Typedef,
        Variable)
from .project_version import ProjectVersion


class ProjectParser(ParserBase):
    """ This is the project file parser. """

    def parse(self, prj):
        """ Parse a project file.

        :param prj:
            is the project.
        :return:
            ``True`` if there was no error.
        """

        self.project = prj

        self._literal = []
        self._literaltext = None

        # This should get overwritten.
        prj.version = -1

        rc = super().parse(prj.name)

        if rc:
            if prj.version < 0:
                prj.diagnostic = "The file doesn't appear to contain a valid MetaSIP project"
                rc = False
            elif prj.version > ProjectVersion:
                prj.diagnostic = "The project was created with a later version of MetaSIP"
                rc = False
        else:
            prj.diagnostic = self.diagnostic

        return rc

    def projectStart(self, attrs):
        """
        Called at the start of a project.

        attrs is the dictionary of attributes.
        """
        self.project.version = int(attrs["version"])
        self.project.rootmodule = optAttribute(attrs, "rootmodule")
        self.project.platforms = optAttribute(attrs, "platforms")
        self.project.features = optAttribute(attrs, "features")
        self.project.externalmodules = optAttribute(attrs, "externalmodules")
        self.project.externalfeatures = optAttribute(attrs, "externalfeatures")
        self.project.ignorednamespaces = optAttribute(attrs,
                "ignorednamespaces")
        self.project.inputdir = attrs["inputdir"]
        self.project.webxmldir = optAttribute(attrs, "webxmldir")
        self.project.outputdir = attrs["outputdir"]

        self.project.xinputdir = os.path.expanduser(self.project.inputdir)

        # Handle the list of versions.  A version is a name, its number is
        # called its generation.
        vers = optAttribute(attrs, "versions")

        if vers != '':
            self.project.versions = vers.split()

        self._literal.append(self.project)

    def projectEnd(self):
        """
        Called at the end of a project.
        """
        self._literal.pop()

    def moduleStart(self, attrs):
        """
        Called at the start of a module.

        attrs is the dictionary of attributes.
        """
        mod = self.project.newModule(attrs["name"],
                optAttribute(attrs, "outputdirsuffix"),
                optAttribute(attrs, "version"), optAttribute(attrs, "imports"))

        self._literal.append(mod)

    def moduleEnd(self):
        """
        Called at the end of a module.
        """
        self._literal.pop()

    def literalStart(self, attrs):
        """
        Called at the start of a literal block.

        attrs is the dictionary of attributes used to determine the type of the
        literal block.
        """
        self._literaltype = attrs["type"]
        self._literaltext = ""

    def characters(self, content):
        """
        Called with #PCDATA content.

        content is the content.
        """
        if self._literaltext is not None:
            self._literaltext += content

    def literalEnd(self):
        """
        Called at the end of a literal block.
        """
        self._literal[-1].literal(self._literaltype, self._literaltext.strip())
        self._literaltext = None

    def moduleheaderfileStart(self, attrs):
        """
        Called at the start of a module header file.

        attrs is the dictionary of attributes.
        """
        id = int(attrs["id"])

        # Find the corresponding header file.
        for hdir in self.project.headers:
            for hf in hdir.content:
                if hf.id == id:
                    self.project.modules[-1].content.append(hf)
                    return

    def headerdirectoryStart(self, attrs):
        """
        Called at the start of a header directory.

        attrs is the dictionary of attributes.
        """
        self.project.newHeaderDirectory(attrs["name"], attrs["parserargs"],
                attrs["inputdirsuffix"], attrs["filefilter"])

    def headerfileStart(self, attrs):
        """
        Called at the start of a header file.

        attrs is the dictionary of attributes.
        """
        hf = self.project.headers[-1].newHeaderFile(int(attrs["id"]),
                attrs["name"], attrs["md5"], optAttribute(attrs, "parse"),
                optAttribute(attrs, "status"), optAttribute(attrs, "sgen"),
                optAttribute(attrs, "egen"))

        self._setScope(hf)
        self._literal.append(hf)

    def headerfileEnd(self):
        """
        Called at the end of a header file.
        """
        self._literal.pop()

    def classStart(self, attrs):
        """
        Called at the start of a class.

        attrs is the dictionary of attributes.
        """
        cls = Class(name=attrs["name"], container=self._scope,
                bases=optAttribute(attrs, "bases"),
                struct=bool(int(optAttribute(attrs, "struct", "0"))),
                access=optAttribute(attrs, "access"),
                pybases=optAttribute(attrs, "pybases"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(cls)
        self._pushScope(cls)
        self._literal.append(cls)

    def classEnd(self):
        """
        Called at the end of a class.
        """
        self._popScope()
        self._literal.pop()

    def manualcodeStart(self, attrs):
        """
        Called at the start of manual code.

        attrs is the dictionary of attributes.
        """
        mc = ManualCode(precis=attrs["precis"],
                access=optAttribute(attrs, "access"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(mc)
        self._literal.append(mc)

    def manualcodeEnd(self):
        """
        Called at the end of manual code.
        """
        self._literal.pop()

    def constructorStart(self, attrs):
        """
        Called at the start of a constructor.

        attrs is the dictionary of attributes.
        """
        cn = Constructor(name=attrs["name"], container=self._scope,
                access=optAttribute(attrs, "access"),
                explicit=bool(int(optAttribute(attrs, "explicit", "0"))),
                pyargs=optAttribute(attrs, "pyargs"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(cn)
        self._argumentscope = cn
        self._literal.append(cn)

    def constructorEnd(self):
        """
        Called at the end of a constructor.
        """
        self._literal.pop()

    def destructorStart(self, attrs):
        """
        Called at the start of a destructor.

        attrs is the dictionary of attributes.
        """
        ds = Destructor(name=attrs["name"], container=self._scope,
                access=optAttribute(attrs, "access"),
                virtual=bool(int(optAttribute(attrs, "virtual", "0"))),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(ds)
        self._literal.append(ds)

    def destructorEnd(self):
        """
        Called at the end of a destructor.
        """
        self._literal.pop()

    def operatorcastStart(self, attrs):
        """
        Called at the start of an operator cast.

        attrs is the dictionary of attributes.
        """
        oc = OperatorCast(name=attrs["name"], container=self._scope,
                access=optAttribute(attrs, "access"),
                const=bool(int(optAttribute(attrs, "const", "0"))),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(oc)
        self._literal.append(oc)

    def operatorcastEnd(self):
        """
        Called at the end of an operator cast.
        """
        self._literal.pop()

    def methodStart(self, attrs):
        """
        Called at the start of a method.

        attrs is the dictionary of attributes.
        """
        mt = Method(name=attrs["name"], container=self._scope,
                access=optAttribute(attrs, "access"),
                rtype=attrs["rtype"],
                virtual=bool(int(optAttribute(attrs, "virtual", "0"))),
                const=bool(int(optAttribute(attrs, "const", "0"))),
                static=bool(int(optAttribute(attrs, "static", "0"))),
                abstract=bool(int(optAttribute(attrs, "abstract", "0"))),
                pytype=optAttribute(attrs, "pytype"),
                pyargs=optAttribute(attrs, "pyargs"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(mt)
        self._argumentscope = mt
        self._literal.append(mt)

    def methodEnd(self):
        """
        Called at the end of a method.
        """
        self._literal.pop()

    def operatormethodStart(self, attrs):
        """
        Called at the start of an operatormethod.

        attrs is the dictionary of attributes.
        """
        mt = OperatorMethod(name=attrs["name"], container=self._scope,
                access=optAttribute(attrs, "access"), rtype=attrs["rtype"],
                virtual=bool(int(optAttribute(attrs, "virtual", "0"))),
                const=bool(int(optAttribute(attrs, "const", "0"))),
                abstract=bool(int(optAttribute(attrs, "abstract", "0"))),
                pytype=optAttribute(attrs, "pytype"),
                pyargs=optAttribute(attrs, "pyargs"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(mt)
        self._argumentscope = mt
        self._literal.append(mt)

    def operatormethodEnd(self):
        """
        Called at the end of an operatormethod.
        """
        self._literal.pop()

    def functionStart(self, attrs):
        """
        Called at the start of a function.

        attrs is the dictionary of attributes.
        """
        fn = Function(name=attrs["name"], container=self._scope,
                rtype=attrs["rtype"], pytype=optAttribute(attrs, "pytype"),
                pyargs=optAttribute(attrs, "pyargs"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(fn)
        self._argumentscope = fn
        self._literal.append(fn)

    def functionEnd(self):
        """
        Called at the end of a function.
        """
        self._literal.pop()

    def operatorfunctionStart(self, attrs):
        """
        Called at the start of an operatorfunction.

        attrs is the dictionary of attributes.
        """
        fn = OperatorFunction(name=attrs["name"], container=self._scope,
                rtype=attrs["rtype"], pytype=optAttribute(attrs, "pytype"),
                pyargs=optAttribute(attrs, "pyargs"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(fn)
        self._argumentscope = fn
        self._literal.append(fn)

    def operatorfunctionEnd(self):
        """
        Called at the end of an operatorfunction.
        """
        self._literal.pop()

    def argumentStart(self, attrs):
        """
        Called at the start of an argument.

        attrs is the dictionary of attributes.
        """
        a = Argument(type=attrs["type"], name=optAttribute(attrs, "name"),
                unnamed=bool(int(optAttribute(attrs, "unnamed", '0'))),
                default=optAttribute(attrs, "default"),
                pytype=optAttribute(attrs, "pytype"),
                annos=optAttribute(attrs, "annos"))

        self._argumentscope.args.append(a)

    def enumStart(self, attrs):
        """
        Called at the start of an enum.

        attrs is the dictionary of attributes.
        """
        en = Enum(name=attrs["name"], access=optAttribute(attrs, "access"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(en)
        self._enumscope = en

    def enumvalueStart(self, attrs):
        """
        Called at the start of an enum value.

        attrs is the dictionary of attributes.
        """
        self._enumscope.content.append(EnumValue(name=attrs["name"],
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen")))

    def variableStart(self, attrs):
        """
        Called at the start of a variable.

        attrs is the dictionary of attributes.
        """
        v = Variable(name=attrs["name"], type=attrs["type"],
                static=bool(int(optAttribute(attrs, "static", "0"))),
                access=optAttribute(attrs, "access"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(v)
        self._literal.append(v)

    def variableEnd(self):
        """
        Called at the end of a variable.
        """
        self._literal.pop()

    def namespaceStart(self, attrs):
        """
        Called at the start of a namespace.

        attrs is the dictionary of attributes.
        """
        ns = Namespace(name=attrs["name"], container=self._scope,
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(ns)
        self._pushScope(ns)
        self._literal.append(ns)

    def namespaceEnd(self):
        """
        Called at the end of a namespace.
        """
        self._popScope()
        self._literal.pop()

    def opaqueclassStart(self, attrs):
        """
        Called at the start of an opaque class.

        attrs is the dictionary of attributes.
        """
        oc = OpaqueClass(name=attrs["name"], container=self._scope,
                access=optAttribute(attrs, "access"),
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(oc)

    def typedefStart(self, attrs):
        """
        Called at the start of a typedef.

        attrs is the dictionary of attributes.
        """
        td = Typedef(name=attrs["name"], type=attrs["type"],
                platforms=optAttribute(attrs, "platforms"),
                features=optAttribute(attrs, "features"),
                annos=optAttribute(attrs, "annos"),
                status=optAttribute(attrs, "status"),
                sgen=optAttribute(attrs, "sgen"),
                egen=optAttribute(attrs, "egen"))

        self._scope.content.append(td)

    def _setScope(self, scope):
        """
        Clear the scope stack and set the initial scope.

        scope is the initial scope.
        """
        self._scopestack = []
        self._scope = scope

    def _pushScope(self, scope):
        """
        Make a scope current.

        scope is the scope to make current.
        """
        self._scopestack.append(self._scope)
        self._scope = scope

    def _popScope(self):
        """
        Restore the previous scope.
        """
        self._scope = self._scopestack.pop()
