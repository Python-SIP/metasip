# Release Notes

## v2.13.5

### Bug fixes

Fixed the crash when creating a new project from the command line (ie. when
running `msip` without a project name).


## v2.13.4

### Bug fixes

- Fixed a crash when creating a new header directory in the Scanner tool.
  Resolves [#23](https://github.com/Python-SIP/metasip/issues/23)
- Fixed a crash when editing a class's properties.  Resolves
  [#22](https://github.com/Python-SIP/metasip/issues/22)
- Fixed a crash when editing an enum member's properties.  Resolves
  [#21](https://github.com/Python-SIP/metasip/issues/21)
- Fixed a crash when creating a new module.  Resolves
  [#20](https://github.com/Python-SIP/metasip/issues/20)

### Missing `LICENSE` file

The missing `LICENSE` file was added.

Resolves [#18](https://github.com/Python-SIP/metasip/issues/18)


## v2.13.3

### Bug fixes

- Fixed the initial status of newly scanned class variables.
- Fixed the displayed signatures after `%MethodCode` has been defined.
- New manual code is now displayed and has an appropriate status and
  version range.
- Added the missing access specifiers in the context menu for methods.
- Updating the version range of an API item will now update the GUI.
- Deleting an API item will now update the GUI.
- Deleting a `.sip` file will now update the GUI.
- Fixed a crash inserting a file into the external editor.
- Fixed a crash when selecting the `KeepReference` annotation of the
  argument properties dialog.
- Fixed two crashes in the callable properties dialog.
- Fixed a crash when doing `Hide Ignored`.
- Fixed a crash in the version range dialog.

Resolves [#16](https://github.com/Python-SIP/metasip/issues/16)

### Documentation references

Links to the documentation have been added to `README.md` and to the
documentation itself.

Resolves [#14](https://github.com/Python-SIP/metasip/issues/14)


## v2.13.2

### Support for Python v3.8

The code has been fixed to enable it to be run under Python v3.8.

Resolves [#13](https://github.com/Python-SIP/metasip/issues/13)


## v2.13.1

### Regression fixes

The following regressions from the PyQt5 based version were fixed:

- crash when resetting the workflow
- crash when scanning a header directory
- a scanned header directory did not expand to show files that need parsing
- crash when parsing a header file
- slots and signals were not recognised as existing methods
- crash when adding a new header file to a module
- drag and drop didn't work
- some new API elements were not initialised as `Unchecked`.

Resolves [#12](https://github.com/Python-SIP/metasip/issues/12)


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
