# Release Notes


## v2.13.0

### Initial documentation

Created the initial, very superficial documentation hosted at Read the Docs.

Resolves [#8](https://github.com/Python-SIP/metasip/issues/8)

### Platform-specific header directory properties

The header directory properties that specify the header files to scan (ie.
the suffix directory and the file filter) have now been combined into a
single header file pattern.

The properties of a header directory (ie. the header file pattern and the
C++ parser arguments) can now be specified in the scanner tool GUI on a
per-platform basis.

Resolves [#7](https://github.com/Python-SIP/metasip/issues/7)

### Added support for attaching comments to API items

The `Comments...` option has been added to the context menu of the API
editor to allow multi-line comments to be attached to any API item.  These
comments are placed above the API item in the generated `.sip` file.

Resolves [#11](https://github.com/Python-SIP/metasip/issues/11)

### Defining the default handling of keyword arguments

It is now possible to configure a module's default handling of keyword
arguments in the module properties dialog.

Resolves [#10](https://github.com/Python-SIP/metasip/issues/10)

### Improved support for typedefs

The typedef properties dialog has been added.

typedefs can now have docstrings.

Resolves [#9](https://github.com/Python-SIP/metasip/issues/9)

### Resolving legacy TODOs

The project format version is now v0.17.

The output directory suffix of a module is now deprecated and the name of
the module is used instead.

The user is now warned that the project format will be updated if it is
saved. In previous versions the format was updated, with the user's
permission when the project was loaded.

The access specifier of a super-class is always generated in a `.sip` file.
In previous versions `public` was omitted to be compatible with old
versions of sip.

Resolves [#6](https://github.com/Python-SIP/metasip/issues/6)
