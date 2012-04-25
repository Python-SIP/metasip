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


from dip.model import Bool, Enum, Int, Instance, Interface, List, Str

from ... import ProjectVersion


class ICodeContainer(Interface):

    content = List(ICode)


class IAnnos(Interface):

    annos = Str()


class IDocString(Interface):

    docstring = Str()


class IVersionRange(Interface):

    egen = Str()

    sgen = Str()


class IWorkflow(Interface):

    status = Enum('', 'ignored', 'todo', 'unknown', default='unknown')


class IHeaderFile(ICodeContainer, IVersionRange, IWorkflow):

    exportedheadercode = Str()

    id = Int()

    initcode = Str()

    md5 = Str()

    modulecode = Str()

    moduleheadercode = Str()

    name = Str()

    parse = Enum('', 'needed')

    postinitcode = Str()

    preinitcode = Str()


class IHeaderDirectory(Interface):

    content = List(IHeaderFile)

    filefilter = Str()

    inputdirsuffix = Str()

    name = Str()

    parserargs = Str()


class IModule(Interface):

    content = List(IHeaderFile)

    directives = Str()

    imports = List(Str())

    name = Str()

    outputdirsuffix = Str()

    version = Str()


class IProject(Interface):
    """ The IProject interface is implemented by projects. """

    externalfeatures = List(Str())

    externalmodules = List(Str())

    features = List(Str())

    headers = List(IHeaderDirectory)

    ignorednamespaces = List(Str())

    inputdir = Str()

    modules = List(IModule)

    outputdir = Str()

    platforms = List(Str())

    rootmodule = Str()

    sipcomments = Str()

    version = Int(ProjectVersion)

    versions = List(Str())

    webxmldir = Str()


class IArgument(IAnnos):

    default = Str()

    name = Str()

    pytype = Str()

    type = Str()

    unnamed = Bool(True)


class ICode(IAnnos, IVersionRange, IWorkflow):

    container = Instance(ICodeContainer)

    features = List(Str())

    platforms = List(Str())


class IAccess(Interface):

    access = Enum('', 'protected', 'private')


class IExtendedAccess(IAccess):

    access = Enum('', 'protected', 'protected slots', 'private',
            'public slots', 'signals'))


class ICallable(ICode):

    args = List(IArgument)

    methcode = Str()

    name = Str()

    pyargs = Str()

    pytype = Str()

    rtype = Str()


class IClassCallable(ICallable):

    container = instance(IClass)


class IFunction(ICallable, IDocString):

    pass


class IOperatorFunction(ICallable):

    pass


class IClass(ICode, ICodeContainer, IDocString, IAccess):

    bases = Str()

    bicharbufcode = Str()

    bigetbufcode = Str()

    bireadbufcode = Str()

    birelbufcode = Str()

    bisegcountcode = Str()

    biwritebufcode = Str()

    convtotypecode = Str()

    gcclearcode = Str()

    gctraversecode = Str()

    name = Str()

    picklecode = Str()

    pybases = Str()

    struct = Bool(False)

    subclasscode = Str()

    typecode = Str()

    typeheadercode = Str()


class IEnumValue(IAnnos, IVersionRange, IWorkflow):

    name = Str()


class IEnum(ICode, IAccess):

    content = List(IEnumValue)


class IManualCode(ICode, IDocString, IExtendedAccess):

    body = Str()

    methcode = Str()

    precis = Str()


class INamespace(ICode, ICodeContainer):

    name = Str()

    typeheadercode = Str()


class IOpaqueClass(ICode, IAccess):

    name = Str()


class ITypedef(ICode):

    name = Str()

    type = Str()


class IVariable(ICode, IAccess):

    accesscode = Str()

    getcode = Str()

    name = Str()

    setcode = Str()

    static = Bool(False)

    type = Str()


class IConstructor(IClassCallable, IDocString, IAccess):

    explicit = Bool(False)

    name = Str()


class IDestructor(ICode, IAccess):

    container = Instance(IClass)

    methcode = Str()

    name = Str()

    virtcode = Str()

    virtual = Bool(False)


class IMethod(IClassCallable, IDocString, IExtendedAccess):

    abstract = Bool(False)

    const = Bool(False)

    static = Bool(False)

    virtcode = Str()

    virtual = Bool(False)


class IOperatorCast(IClassCallable, IAccess):

    const = Bool(False)


class IOperatorMethod(IClassCallable, IAccess):

    abstract = Bool(False)

    const = Bool(False)

    virtcode = Str()

    virtual = Bool(False)
