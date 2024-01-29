# `msipgen` Command Line Tool

`msipgen` is the command line part of MetaSIP that generates the `.sip` files
from the project created by `msip`.

To install `msipgen`, run the following command:

    pip install metasip


## Command Line Options

The syntax of the `msipgen` command line is:

    msipgen [options] project

The full set of command line options is:

`-h`, `--help`
: Show a help message.

`-V`, `--version`
: Show the MetaSIP version number.

`--ignore MODULE`
: Do not generate `.sip` files for `MODULE`.

`--output-dir DIR`
: Generate the `.sip` files in `DIR`.  This option is required.

`--verbose`
: Display progress messages.
