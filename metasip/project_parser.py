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

from PyQt4.QtGui import QApplication, QProgressDialog

from .interfaces.project import ProjectVersion
from .Project import (Argument, Class, Constructor, Destructor, Enum,
        EnumValue, Function, ManualCode, Method, Namespace, OpaqueClass,
        OperatorCast, OperatorFunction, OperatorMethod, Project, Typedef,
        Variable)


class ProjectParser:
    """ This is the project file parser. """

    def parse(self, project):
        """ Parse a project file.

        :param project:
            is the project.
        """

        # Load the file.
        tree = ElementTree.parse(project.name)

        # Do some basic sanity checks.
        root = tree.getroot()

        version = root.get('version')

        if root.tag != 'Project' or version is None:
            raise Exception(
                    "The file doesn't appear to be a valid MetaSIP project")

        # Check the version.
        version = int(version)

        if version > ProjectVersion:
            raise Exception(
                    "The project was created with a later version of MetaSIP")

        # Create a progress dialog if there is a GUI.
        if QApplication.instance() is not None:
            # Progress will be reported against classes.
            nr_steps = len(root.findall('.//Class'))

            self._progress = QProgressDialog("Loading...", None, 0, nr_steps)
            self._progress.setWindowTitle(project.name)
            self._progress.setValue(0)
        else:
            self._progress = None

        # Read the project.
        project.version = version
        project.rootmodule = root.get('rootmodule', '')
        project.platforms = root.get('platforms', '')
        project.features = root.get('features', '')
        project.externalmodules = root.get('externalmodules', '')
        project.externalfeatures = root.get('externalfeatures', '')
        project.ignorednamespaces = root.get('ignorednamespaces', '')
        project.inputdir = root.get('inputdir')
        project.webxmldir = root.get('webxmldir', '')
        project.outputdir = root.get('outputdir')

        # Handle the list of versions.  A version is a name, its number is
        # called its generation.
        vers = root.get('versions')
        if vers is not None:
            project.versions = vers.split()

        for child in root:
            if child.tag == 'HeaderDirectory':
                self.add_header_directory(project, child)
            elif child.tag == 'Literal':
                self.add_literal(project, child)
            elif child.tag == 'Module':
                self.add_module(project, child)

    def add_argument(self, callable, elem):
        """ Add an element defining an argument to a callable. """

        arg = Argument(type=elem.get('type'), name=elem.get('name', ''),
                unnamed=bool(int(elem.get('unnamed', '0'))),
                default=elem.get('default', ''), pytype=elem.get('pytype', ''),
                annos=elem.get('annos', ''))

        callable.args.append(arg)

    def add_class(self, scope, elem):
        """ Add an element defining a class to a scope. """

        cls = Class(name=elem.get('name'), container=scope,
                bases=elem.get('bases', ''),
                struct=bool(int(elem.get('struct', '0'))),
                access=elem.get('access', ''), pybases=elem.get('pybases', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Constructor':
                self.add_constructor(cls, child)
            elif child.tag == 'Destructor':
                self.add_destructor(cls, child)
            elif child.tag == 'Literal':
                self.add_literal(cls, child)
            elif child.tag == 'Method':
                self.add_method(cls, child)
            elif child.tag == 'OperatorCast':
                self.add_operator_cast(cls, child)
            elif child.tag == 'OperatorMethod':
                self.add_operator_method(cls, child)
            else:
                self.add_code(cls, child)

        scope.content.append(cls)

        if self._progress is not None:
            self._progress.setValue(self._progress.value() + 1)
            QApplication.processEvents()

    def add_code(self, scope, elem):
        """ Add an element defining scoped code to a scope. """

        if elem.tag == 'Class':
            self.add_class(scope, elem)
        elif elem.tag == 'Enum':
            self.add_enum(scope, elem)
        elif elem.tag == 'ManualCode':
            self.add_manual_code(scope, elem)
        elif elem.tag == 'Namespace':
            self.add_namespace(scope, elem)
        elif elem.tag == 'OpaqueClass':
            self.add_opaque_class(scope, elem)
        elif elem.tag == 'Typedef':
            self.add_typedef(scope, elem)
        elif elem.tag == 'Variable':
            self.add_variable(scope, elem)

    def add_constructor(self, cls, elem):
        """ Add an element defining a constructor to a class. """

        cn = Constructor(name=elem.get('name'), container=cls,
                access=elem.get('access', ''),
                explicit=bool(int(elem.get('explicit', '0'))),
                pyargs=elem.get('pyargs', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Argument':
                self.add_argument(cn, child)
            elif child.tag == 'Literal':
                self.add_literal(cn, child)

        cls.content.append(cn)

    def add_destructor(self, cls, elem):
        """ Add an element defining a destructor to a class. """

        ds = Destructor(name=elem.get('name'), container=cls,
                access=elem.get('access', ''),
                virtual=bool(int(elem.get('virtual', '0'))),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Literal':
                self.add_literal(ds, child)

        cls.content.append(ds)

    def add_enum(self, scope, elem):
        """ Add an element defining an enum to a scope. """

        en = Enum(name=elem.get('name'), container=scope,
                access=elem.get('access', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'EnumValue':
                self.add_enum_value(en, child)

        scope.content.append(en)

    def add_enum_value(self, en, elem):
        """ Add an element defining an enum value to an enum. """

        ev = EnumValue(name=elem.get('name'), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        en.content.append(ev)

    def add_function(self, hf, elem):
        """ Add an element defining a function to a header file. """

        fn = Function(name=elem.get('name'), container=hf,
                rtype=elem.get('rtype'), pytype=elem.get('pytype', ''),
                pyargs=elem.get('pyargs', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Argument':
                self.add_argument(fn, child)
            elif child.tag == 'Literal':
                self.add_literal(fn, child)

        hf.content.append(fn)

    def add_header_directory(self, project, elem):
        """ Add an element defining a header directory to a project. """

        hdir = project.newHeaderDirectory(elem.get('name'),
                elem.get('parserargs'), elem.get('inputdirsuffix'),
                elem.get('filefilter'))

        for child in elem:
            if child.tag == 'HeaderFile':
                self.add_header_file(hdir, child)

    def add_header_file(self, hdir, elem):
        """ Add an element defining a header file to a header directory. """

        hf = hdir.newHeaderFile(int(elem.get('id')), elem.get('name'),
                elem.get('md5'), elem.get('parse', ''), elem.get('status', ''),
                elem.get('sgen', ''), elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Function':
                self.add_function(hf, child)
            elif child.tag == 'Literal':
                self.add_literal(hf, child)
            elif child.tag == 'OperatorFunction':
                self.add_operator_function(hf, child)
            else:
                self.add_code(hf, child)

    def add_literal(self, model, elem):
        """ Add an element defining some literal text to a model. """

        setattr(model, elem.get('type'), elem.text.strip())

    def add_manual_code(self, scope, elem):
        """ Add an element defining manual code to a scope. """

        mc = ManualCode(precis=elem.get('precis'), container=scope,
                access=elem.get('access', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Literal':
                self.add_literal(mc, child)

        scope.content.append(mc)

    def add_method(self, cls, elem):
        """ Add an element defining a method to a class. """

        mt = Method(name=elem.get('name'), container=cls,
                access=elem.get('access', ''), rtype=elem.get('rtype'),
                virtual=bool(int(elem.get('virtual', '0'))),
                const=bool(int(elem.get('const', '0'))),
                static=bool(int(elem.get('static', '0'))),
                abstract=bool(int(elem.get('abstract', '0'))),
                pytype=elem.get('pytype', ''), pyargs=elem.get('pyargs', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Argument':
                self.add_argument(mt, child)
            elif child.tag == 'Literal':
                self.add_literal(mt, child)

        cls.content.append(mt)

    def add_module(self, project, elem):
        """ Add an element defining a module to a project. """

        mod = project.newModule(elem.get('name'),
                elem.get('outputdirsuffix', ''), elem.get('version', ''),
                elem.get('imports', ''))

        for child in elem:
            if child.tag == 'Literal':
                self.add_literal(mod, child)
            elif child.tag == 'ModuleHeaderFile':
                self.add_module_header_file(project, mod, child)

    def add_module_header_file(self, project, mod, elem):
        """ Add an element defining a module header file to a module. """

        id = int(elem.get('id'))

        # Find the corresponding header file.
        for hdir in project.headers:
            for hf in hdir.content:
                if hf.id == id:
                    mod.content.append(hf)
                    return

    def add_namespace(self, scope, elem):
        """ Add an element defining a namespace to a scope. """

        ns = Namespace(name=elem.get('name'), container=scope,
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Function':
                self.add_function(ns, child)
            elif child.tag == 'Literal':
                self.add_literal(ns, child)
            elif child.tag == 'OperatorFunction':
                self.add_operator_function(ns, child)
            else:
                self.add_code(ns, child)

        scope.content.append(ns)

    def add_opaque_class(self, scope, elem):
        """ Add an element defining an opaque class to a scope. """

        oc = OpaqueClass(name=elem.get('name'), container=scope,
                access=elem.get('access', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        scope.content.append(oc)

    def add_operator_cast(self, cls, elem):
        """ Add an element defining an operator cast to a class. """

        oc = OperatorCast(name=elem.get('name'), container=cls,
                access=elem.get('access', ''),
                const=bool(int(elem.get('const', '0'))),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Argument':
                self.add_argument(oc, child)
            elif child.tag == 'Literal':
                self.add_literal(oc, child)

        cls.content.append(oc)

    def add_operator_function(self, hf, elem):
        """ Add an element defining an operator function to a header file. """

        fn = OperatorFunction(name=elem.get('name'), container=hf,
                rtype=elem.get('rtype'), pytype=elem.get('pytype', ''),
                pyargs=elem.get('pyargs', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Argument':
                self.add_argument(fn, child)
            elif child.tag == 'Literal':
                self.add_literal(fn, child)

        hf.content.append(fn)

    def add_operator_method(self, cls, elem):
        """ Add an element defining an operator method to a class. """

        mt = OperatorMethod(name=elem.get('name'), container=cls,
                access=elem.get('access', ''), rtype=elem.get('rtype'),
                virtual=bool(int(elem.get('virtual', '0'))),
                const=bool(int(elem.get('const', '0'))),
                abstract=bool(int(elem.get('abstract', '0'))),
                pytype=elem.get('pytype', ''), pyargs=elem.get('pyargs', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Argument':
                self.add_argument(mt, child)
            elif child.tag == 'Literal':
                self.add_literal(mt, child)

        cls.content.append(mt)

    def add_typedef(self, scope, elem):
        """ Add an element defining a typedef to a scope. """

        td = Typedef(name=elem.get('name'), container=scope,
                type=elem.get('type'), platforms=elem.get('platforms', ''),
                features=elem.get('features', ''),
                annos=elem.get('annos', ''), status=elem.get('status', ''),
                sgen=elem.get('sgen', ''), egen=elem.get('egen', ''))

        scope.content.append(td)

    def add_variable(self, scope, elem):
        """ Add an element defining a variable to a scope. """

        var = Variable(name=elem.get('name'), container=scope,
                type=elem.get('type'),
                static=bool(int(elem.get('static', '0'))),
                access=elem.get('access', ''),
                platforms=elem.get('platforms', ''),
                features=elem.get('features', ''), annos=elem.get('annos', ''),
                status=elem.get('status', ''), sgen=elem.get('sgen', ''),
                egen=elem.get('egen', ''))

        for child in elem:
            if child.tag == 'Literal':
                self.add_literal(var, child)

        scope.content.append(var)
