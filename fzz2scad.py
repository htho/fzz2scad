'''
    fzz2scad: Creates OpenSCAD 3D models of PCBs from Fritzing-Sketches.

    Copyright (C) 2015  Hauke Thorenz <htho@thorenz.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as    published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import fzz2scadLib as lib
import argparse
import os
import json

# ####################### SCRIPT PART ########################

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Creates a 3D Module (OpenSCAD) of the PCB in a Fritzing Sketch.")
    parser.add_argument("INPUT_FILE", help="The Fritzing Sketch File (.fzz) to use.")
    parser.add_argument("-m", "--module-name", default=None, help="The name of the OpenSCAD module that will be created. (default: 'foo.fzz' creates 'module foo()') If there are names set in the Sketch, this becomes a prefix.")
    parser.add_argument("-g", "--show-groundplate", help="Show a 'groundplate' for each part. This might be helpful when creating and testing new modules.", action="store_true")
    parser.add_argument("-r", "--round", help="Try to round coordinates as Fritzing is not able to place parts in eg. x=0;y=0 (NOT IMPLEMENTED YET).", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="-v -vv- -vvv increase output verbosity")
    parser.add_argument("-l", "--list", help="List the parts and their position in the given input file and exit.", action="store_true")
    parser.add_argument('-V', '--version', action='version', version="%(prog)s " + str(lib.VERSION))
    parser.add_argument("-o", "--output", nargs="?", default=None, const="", help="Write output to an .scad File instead to console. (if not defined further 'foo.fzz' becomes 'foo.scad')")
    parser.add_argument("--override", action="store_true", help="Override existing output files without asking.")
    parser.add_argument("--dont-override", action="store_true", help="Do not override any existing output files - Print to console instead.")
    parser.add_argument("--ask", default="true", action="store_true", help="Ask if an existing file should be overwritten. (default)")

    args = parser.parse_args()
    lib.args = args

    lib.printConsole("fzz2scad " + str(lib.VERSION), 1)  # Say hi

    # get filename
    inputFzzFileName = args.INPUT_FILE
    lib.inputFzzFileName = inputFzzFileName

    outputFileName = lib.determineOutFile(args.INPUT_FILE, None, ".scad")

    # get filename of the fz file in the fzz file
    inputFzFileName = lib.getFilesThatEndWith(inputFzzFileName, ".fz")[0]  # We take the first and hope the best.

    lib.printConsole("PROGRESS: Taking XML Root from input file...", 1)
    xmlRoot = lib.getXMLRoot(inputFzzFileName, inputFzFileName)
    lib.xmlRoot = xmlRoot

    lib.printConsole("PROGRESS: Taking the Configturation from the xml tree...", 1)

    if args.module_name is not None:
        moduleNameOrPrefix = args.module_name
    else:
        moduleNameOrPrefix = str(os.path.split(inputFzzFileName)[-1]).split(".")[0]

    configuration = lib.getConfig(xmlRoot, moduleNameOrPrefix)
    lib.printConsole("CONFIGURATION:" + json.dumps(configuration, sort_keys=True, indent=4), 1)

    lib.printConsole("PROGRESS: Extracting Parts from the xml tree...", 1)
    parts = lib.getParts(xmlRoot, configuration['attributes'])
    lib.printConsole("PARTS:" + repr(parts), 1)

    # list parts and exit
    if args.list:
        lib.printConsole("Parts:", 0)
        for part in sorted(parts):
            lib.printConsole(part, 0)
        exit(0)

    exportString = lib.createExportString(parts, configuration)

    lib.printConsole("PROGRESS: Sorting parts into modules...", 1)
    modules = lib.splitPartsToModules(xmlRoot, parts, configuration['modules'])
    for moduleName, moduleParts in modules.items():
        lib.printConsole("MODULE '{}':".format(moduleName), 1)
        lib.printConsole("    PARTS: {}".format(moduleParts.keys()), 1)

    fileCommentTemplate = """@filename: {filename}
@created-with: fzz2scad v{version!s} (https://github.com/htho/fzz2scad)
"""

    # The Template for the output file
    fileTemplate = """{fileComment}
{export}

{modules}
"""

    # Values to write into the output file.
    fileValues = dict()
    fileValues['version'] = lib.VERSION

    # where to write to?
    fileValues['filename'] = outputFileName

    lib.printConsole("PROGRESS: Creating modules...", 1)
    fileValues['modules'] = []
    for moduleName, moduleParts in modules.items():
        fileValues['modules'].append(lib.createModuleString(moduleName, moduleParts, configuration))

    fileValues['modules'] = sorted(fileValues['modules'])
    fileValues['modules'] = "\n\n\n".join(fileValues['modules'])

    fileValues['export'] = exportString

    # The complete file as a string
    fileValues['fileComment'] = fileCommentTemplate.format(**fileValues)
    fileValues['fileComment'] = "/**\n" + lib.txt_prefix_each_line(fileValues['fileComment'], " * ") + "\n */"

    outString = fileTemplate.format(**fileValues)

    lib.outputHelper(outString, outputFileName)
    exit(0)
