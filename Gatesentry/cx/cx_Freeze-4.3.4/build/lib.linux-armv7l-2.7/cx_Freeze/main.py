import optparse
import os
import shutil
import stat
import sys

import cx_Freeze

__all__ = ["main"]

USAGE = \
"""
%prog [options] [SCRIPT]

Freeze a Python script and all of its referenced modules to a base
executable which can then be distributed without requiring a Python
installation."""

VERSION = \
"""
%%prog %s
Copyright (c) 2007-2013 Anthony Tuininga. All rights reserved.
Copyright (c) 2001-2006 Computronix Corporation. All rights reserved.""" % \
        cx_Freeze.version


def ParseCommandLine():
    parser = optparse.OptionParser(version = VERSION.strip(),
            usage = USAGE.strip())
    parser.add_option("-O",
            action = "count",
            default = 0,
            dest = "optimized",
            help = "optimize generated bytecode as per PYTHONOPTIMIZE; "
                   "use -OO in order to remove doc strings")
    parser.add_option("-c", "--compress",
            action = "store_true",
            dest = "compress",
            help = "compress byte code in zip files")
    parser.add_option("-s", "--silent",
            action = "store_true",
            dest = "silent",
            help = "suppress all output except warnings and errors")
    parser.add_option("--base-name",
            dest = "baseName",
            metavar = "NAME",
            help = "file on which to base the target file; if the name of the "
                   "file is not an absolute file name, the subdirectory bases "
                   "(rooted in the directory in which the freezer is found) "
                   "will be searched for a file matching the name")
    parser.add_option("--init-script",
            dest = "initScript",
            metavar = "NAME",
            help = "script which will be executed upon startup; if the name "
                   "of the file is not an absolute file name, the "
                   "subdirectory initscripts (rooted in the directory in "
                   "which the cx_Freeze package is found) will be searched "
                   "for a file matching the name")
    parser.add_option("--target-dir", "--install-dir",
            dest = "targetDir",
            metavar = "DIR",
            help = "the directory in which to place the target file and "
                   "any dependent files")
    parser.add_option("--target-name",
            dest = "targetName",
            metavar = "NAME",
            help = "the name of the file to create instead of the base name "
                   "of the script and the extension of the base binary")
    parser.add_option("--no-copy-deps",
            dest = "copyDeps",
            default = True,
            action = "store_false",
            help = "do not copy the dependent files (extensions, shared "
                   "libraries, etc.) to the target directory; this also "
                   "modifies the default init script to ConsoleKeepPath.py "
                   "and means that the target executable requires a Python "
                   "installation to execute properly")
    parser.add_option("--default-path",
            action = "append",
            dest = "defaultPath",
            metavar = "DIRS",
            help = "list of paths separated by the standard path separator "
                   "for the platform which will be used to initialize "
                   "sys.path prior to running the module finder")
    parser.add_option("--include-path",
            action = "append",
            dest = "includePath",
            metavar = "DIRS",
            help = "list of paths separated by the standard path separator "
                   "for the platform which will be used to modify sys.path "
                   "prior to running the module finder")
    parser.add_option("--replace-paths",
            dest = "replacePaths",
            metavar = "DIRECTIVES",
            help = "replace all the paths in modules found in the given paths "
                   "with the given replacement string; multiple values are "
                   "separated by the standard path separator and each value "
                   "is of the form path=replacement_string; path can be * "
                   "which means all paths not already specified")
    parser.add_option("--include-modules",
            dest = "includeModules",
            metavar = "NAMES",
            help = "comma separated list of modules to include")
    parser.add_option("--exclude-modules",
            dest = "excludeModules",
            metavar = "NAMES",
            help = "comma separated list of modules to exclude")
    parser.add_option("--ext-list-file",
            dest = "extListFile",
            metavar = "NAME",
            help = "name of file in which to place the list of dependent files "
                   "which were copied into the target directory")
    parser.add_option("-z", "--zip-include",
            dest = "zipIncludes",
            action = "append",
            default = [],
            metavar = "SPEC",
            help = "name of file to add to the zip file or a specification of "
                   "the form name=arcname which will specify the archive name "
                   "to use; multiple --zip-include arguments can be used")
    parser.add_option("--icon",
            dest = "icon",
            help = "name of the icon file for the application")
    options, args = parser.parse_args()
    if len(args) == 0:
        options.script = None
    elif len(args) == 1:
        options.script, = args
    else:
        parser.error("only one script can be specified")
    if not args and options.includeModules is None and options.copyDeps:
        parser.error("script or a list of modules must be specified")
    if not args and options.targetName is None:
        parser.error("script or a target name must be specified")
    if options.excludeModules:
        options.excludeModules = options.excludeModules.split(",")
    else:
        options.excludeModules = []
    if options.includeModules:
        options.includeModules = options.includeModules.split(",")
    else:
        options.includeModules = []
    replacePaths = []
    if options.replacePaths:
        for directive in options.replacePaths.split(os.pathsep):
            fromPath, replacement = directive.split("=")
            replacePaths.append((fromPath, replacement))
    options.replacePaths = replacePaths
    if options.defaultPath is not None:
        sys.path = [p for mp in options.defaultPath \
                for p in mp.split(os.pathsep)]
    if options.includePath is not None:
        paths = [p for mp in options.includePath for p in mp.split(os.pathsep)]
        sys.path = paths + sys.path
    if options.script is not None:
        sys.path.insert(0, os.path.dirname(options.script))
    zipIncludes = []
    if options.zipIncludes:
        for spec in options.zipIncludes:
            if '=' in spec:
                zipIncludes.append(spec.split('=', 1))
            else:
                zipIncludes.append(spec)
    options.zipIncludes = zipIncludes
    return options


def main():
    options = ParseCommandLine()
    executables = [cx_Freeze.Executable(options.script,
            targetName = options.targetName)]
    freezer = cx_Freeze.Freezer(executables,
            includes = options.includeModules,
            excludes = options.excludeModules,
            replacePaths = options.replacePaths,
            compress = options.compress,
            optimizeFlag = options.optimized,
            copyDependentFiles = options.copyDeps,
            initScript = options.initScript,
            base = options.baseName,
            path = None,
            createLibraryZip = False,
            appendScriptToExe = True,
            targetDir = options.targetDir,
            zipIncludes = options.zipIncludes,
            icon = options.icon,
            silent = options.silent)
    freezer.Freeze()
