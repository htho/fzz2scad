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

# import statements: We use pythons included batteries!
import zipfile
import argparse
import xml.etree.ElementTree as ET
import html
import os
import math
import re
import json

VERSION = 0.1

# This is a blacklist for modules fzz2oscad can't handle.
# This list is NOT for parts that don't have any models yet.
# Missing models are simply ignored.
moduleIdRef_blacklist = frozenset([
    "WireModuleID",
    "ViaModuleID",
    "generic_male_pin_header_.*",
    "generic_female_pin_header_.*"
])
moduleIdRef_blacklist_pattern = frozenset([re.compile(s) for s in moduleIdRef_blacklist])

# This is a whitelist for <pcbView layer="x"> that determine if a part
# belongs to the pcbView.
pcbView_layer_whitelist = frozenset([
    "board",
    "copper0"
])
pcbView_layer_whitelist_pattern = frozenset([re.compile(s) for s in pcbView_layer_whitelist])

# ####################### I/O HELPER FUNCTIONS ########################


def printOutFile(s):
    """Store the given string in the buffer for output."""
    global outFileBuffer
    outFileBuffer = outFileBuffer + s


def printConsole(s, minimumVerbosityLevel):
    """Write the given string to the console. To be printed
    args.verbose needs to be >= minimumVerbosityLevel."""
    global args
    if args.verbose >= minimumVerbosityLevel:
        print(s)


def getXMLRoot(zipFile, xmlFileName):
    """get the xml root of the XML File in the given zip File."""
    ret = None
    with zipfile.ZipFile(zipFile, 'r') as zf:
        with zf.open(xmlFileName, 'r') as xf:
            ret = ET.parse(xf)
    return ret


def getFilesThatEndWith(zipFile, endswith):
    """get a list of the files in the given zip file which names end with
    the given string."""
    ret = list()
    with zipfile.ZipFile(zipFile, 'r') as zf:
        namelist = zf.namelist()
        for name in namelist:
            if name.endswith(endswith):
                ret = ret + [name]
    return ret


# ####################### TXT HELPER FUNCTIONS ########################


def txt_from_note(noteXmlElement):
    text = noteXmlElement.find("text").text
    text = html.unescape(text)
    htmlRoot = ET.fromstring(text)
    pElements = htmlRoot.findall("*/p")
    ret = ""
    for p in pElements:
        if p.text is not None:
            ret = ret + p.text + "\n"
    return ret


def txt_prefix_each_line(string, prefix, ignorefirst=False, ignorelast=False):
    """prefix each line in the given string with the given prefix.
    Useful for block indention."""
    ret = list()
    splitted = string.splitlines()
    if len(splitted) == 0:
        return ""

    if ignorefirst:
        ret.append(splitted[0])
        splitted = splitted[1:]
        if len(splitted) == 0:
            return "\n".join(ret)

    last = None
    if ignorelast:
        last = splitted[-1]
        splitted = splitted[:-1]
        if len(splitted) == 0:
            return "\n".join(ret.append(last))

    for line in splitted:
        ret.append(prefix + line)

    if ignorelast:
        ret.append(last)

    return "\n".join(ret)


def txt_match_in_patternset(string, patternset):
    for pattern in patternset:
        if pattern.fullmatch(string):
            return True
    return False

# ####################### CLASSES ########################


class Part:

    """A Part (e.g. Switch or LED)."""

    # static dictionary with information about the different parts.
    # key: moduleIdRef
    # value: dict() (see getPrototype())
    partPrototypes = dict()

    def __init__(self, moduleIdRef, title, partXPos, partYPos, matrix, bottom, attributes):
        """Create a new part instance. This Constuctor will seldom be
        called directly.

        TODO: Allow regular expressions for finding attributes
        TODO: merge attributes (attributes may be defined in a regular expression and explicitly)"""

        self.moduleIdRef = moduleIdRef
        self.title = title
        self.partXPos = partXPos
        self.partYPos = partYPos
        self.matrix = matrix
        self.bottom = bottom
        self.module_name = "m" + moduleIdRef
        if self.title in attributes.keys():
            self.attributes = attributes[self.title]
        else:
            self.attributes = dict()

        if "params" in self.attributes.keys():
            self.params = self.attributes.pop("params")
        else:
            self.params = ""

        # TODO: Use RegEx Magic instead
        for c in self.module_name:
            if c not in frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"):
                self.module_name = self.module_name.replace(c, "_")

    @staticmethod
    def getPrototype(moduleIdRef):
        """Get static Information about this part.
        return dict('svgWidth':?, 'svgHeihgt':?, 'xOffset':?. 'yOffset':?)
        svgWidth/Height: Size of the SVG that represents this parts PCB
        footprint. Needed for rotation.
        Offset: Position of connector0 IN the SVG
        """
        if moduleIdRef not in Part.partPrototypes:
            global inputFzzFileName
            global xmlRoot

            printConsole("Creating Prototype for moduleIdRef='" + moduleIdRef + "'", 2)

            Part.partPrototypes[moduleIdRef] = dict()

            fzpFileNamePath = xmlRoot.find("./instances/instance[@moduleIdRef='" + moduleIdRef + "']").attrib['path']
            fzpRoot = getXMLRoot(inputFzzFileName, "part." + os.path.basename(fzpFileNamePath))
            connector0svgId = fzpRoot.find("./connectors/connector[@id='connector0']/views/pcbView/p[@layer='copper0']").attrib['svgId']

            svgFileName = (fzpRoot.find("./views/pcbView/layers").attrib['image']).replace("/", ".")
            svgRoot = getXMLRoot(inputFzzFileName, "svg." + svgFileName)

            viewBoxValues = svgRoot.find(".").attrib['viewBox'].split()

            viewBoxWidthOfAUnit = Dimension(svgRoot.find(".").attrib['width']) / Dimension(viewBoxValues[2])
            viewBoxHeightOfAUnit = Dimension(svgRoot.find(".").attrib['height']) / Dimension(viewBoxValues[3])

            svgConnector0Element = svgRoot.find(".//*[@id='" + connector0svgId + "']")

            # width and height of the svg (important for correct rotations)
            Part.partPrototypes[moduleIdRef]['svgWidth'] = Dimension(svgRoot.find(".").attrib['width'])
            Part.partPrototypes[moduleIdRef]['svgHeight'] = Dimension(svgRoot.find(".").attrib['height'])

            # position of connector0 IN the svg.
            Part.partPrototypes[moduleIdRef]['xOffset'] = Dimension(svgConnector0Element.attrib['cx']) * viewBoxWidthOfAUnit
            Part.partPrototypes[moduleIdRef]['yOffset'] = Dimension(svgConnector0Element.attrib['cy']) * viewBoxHeightOfAUnit

            # negating on purpose! We need to transform the coordinate system from positive y to negative y:
            Part.partPrototypes[moduleIdRef]['yOffset'] = -Part.partPrototypes[moduleIdRef]['yOffset']

            printConsole("Proto '" + moduleIdRef + "': " + repr(Part.partPrototypes[moduleIdRef]), 2)

        return Part.partPrototypes[moduleIdRef]

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create a Part from the given instance Element in the tree of
        of an .fz file.
        """

        moduleIdRef = instanceXmlElement.attrib['moduleIdRef']

        partXPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['x'])
        partYPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['y'])

        bottom = False
        try:
            bottom_attrib = instanceXmlElement.find("./views/pcbView").attrib['bottom']

            if bottom_attrib == "true":
                bottom = True
        except KeyError:
            # It's okay! This just means bottom = False.
            # I heard this approach is "pythonic" ?
            pass

        # negating on purpose! We need to transform the coordinate system
        # from positive y to negative y:
        partYPos = -partYPos
        return Part(
            moduleIdRef,
            instanceXmlElement.find("./title").text,
            partXPos,
            partYPos,
            transformElement2MatrixString(instanceXmlElement.find("./views/pcbView/geometry/transform")),
            bottom,
            attributes
        )

    def asScad(self):
        """get a string representation to be used in an scad file."""
        printConsole("Self: '" + str(self) + "'", 2)
        proto = Part.getPrototype(self.moduleIdRef)
        data = dict()

        data['svgWidth'] = proto['svgWidth'].asMm()
        data['svgHeight'] = proto['svgHeight'].asMm()

        data['xOffset'] = proto['xOffset'].asMm()
        data['yOffset'] = proto['yOffset'].asMm()

        data['module_name'] = self.module_name
        data['moduleIdRef'] = self.moduleIdRef
        data['title'] = self.title
        data['attributes'] = self.attributes
        data['params'] = self.params

        data['module'] = self.module_name
        data['partXPos'] = self.partXPos.asMm()
        data['partYPos'] = self.partYPos.asMm()
        data['svgZ'] = 1.0  # How tall should the groundplate be?

        if self.matrix is not None:
            data['multmatrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"
        else:
            data['multmatrix'] = ""

        global args
        if args.show_groundplate:
            data['groundplate'] = "%translate([{svgWidth}/2,-{svgHeight}/2,-{svgZ}/2]) cube([{svgWidth},{svgHeight},{svgZ}],true);".format(**data)
        else:
            data['groundplate'] = ""

        if self.bottom:
            data['bottom_handling'] = "translate([0,0,-pcbHeight]) mirror([0,0,1])"
        else:
            data['bottom_handling'] = ""

        return"""// Part: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}'
translate([{partXPos},{partYPos},0]) //position on the PCB
{multmatrix}{{
    {bottom_handling} translate([{xOffset},{yOffset},0]) {module}({params}); {groundplate}
}}""".format(**data)

    def __str__(self):
        return "Part: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', partXPos: '{}mm', partYPos: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.partXPos.asMm(), self.partYPos.asMm())


class PCB(Part):
    """A Part representing a PCB with the given dimensions."""

    def __init__(self, moduleIdRef, title, partXPos, partYPos, matrix, width, depth, attributes):
        super().__init__(moduleIdRef, title, partXPos, partYPos, matrix, False, attributes)  # It is not possible to have a PCB on the bottom. Isnt it?
        self.width = width
        self.depth = depth
        if self.params == "":
            raise AttributeError('A PCB must have the parameter \'pcbHeight\'. Add a note like this to the PCB Layer: {{"{}":{{"params":"pcbHeight=1.2"}}}}'.format(self.title))

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create this PCB from the given instanceXmlElement """
        global xmlRoot
        title = instanceXmlElement.find("./title").text
        boardXmlElement = xmlRoot.find("./boards/board[@instance='" + title + "']")

        PCBXPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['x'])
        PCBYPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['y'])

        # negating on purpose! We need to transform the coordinate system
        # from positive y to negative y:
        PCBYPos = -PCBYPos

        return PCB(
            instanceXmlElement.attrib['moduleIdRef'],
            title,
            PCBXPos,
            PCBYPos,
            transformElement2MatrixString(instanceXmlElement.find("./views/pcbView/geometry/transform")),
            Dimension(boardXmlElement.attrib['width']),
            Dimension(boardXmlElement.attrib['height']),
            attributes
        )

    def asScad(self):
        """get a string representation to be used in an scad file."""
        data = dict()
        data['module_name'] = self.module_name
        data['moduleIdRef'] = self.moduleIdRef
        data['title'] = self.title
        data['module'] = self.module_name
        data['partXPos'] = str(self.partXPos.asMm())
        data['partYPos'] = str(self.partYPos.asMm())
        data['width'] = str(self.width.asMm())
        data['depth'] = str(self.depth.asMm())
        data['attributes'] = self.attributes
        data['params'] = self.params

        if self.matrix is not None:
            data['multmatrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"
        else:
            data['multmatrix'] = ""

        return """// PCB: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}'
translate([{partXPos},{partYPos},0]) //position
{multmatrix}{{
    {module}({width}, {depth}, {params});
}}""".format(**data)

    def __str__(self):
        return "PCB: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', PCBXPos: '{}mm', PCBYPos: '{}mm', matrix: '{}', width: '{}mm', depth: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.partXPos.asMm(), self.partYPos.asMm(), self.matrix, self.width.asMm(), self.depth.asMm())


class Hole(Part):
    """A Part representing a Hole."""

    def __init__(self, moduleIdRef, title, partXPos, partYPos, matrix, diameter, attributes):
        super().__init__(moduleIdRef, title, partXPos, partYPos, matrix, False, attributes)  # It is not possible to have a Hole on the bottom. Isnt it?
        self.diameter = diameter
        if self.params == "":
            raise AttributeError('A Hole must have the parameter \'drillDepth\'. Add a note like this to the PCB Layer: {{"{}":{{"params":"drillDepth=50"}}}}\nNote that the diameter is extracted from the sketch, so it must not be set as attribute here.'.format(self.title))

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create this Hole from the given instanceXmlElement """
        global xmlRoot
        title = instanceXmlElement.find("./title").text
        xmlElement = xmlRoot.find("./instances/instance[@moduleIdRef='HoleModuleID']")

        xPos = Dimension(xmlElement.find("./views/pcbView/geometry").attrib['x'])
        yPos = Dimension(xmlElement.find("./views/pcbView/geometry").attrib['y'])

        diameterString = xmlElement.find("./property[@name='hole size']").attrib['value']
        # The value of diameterString looks like this: "4.2mm,0.0mm" th left value is the diameter, the right value is the thickness of a ring - it can be ignored.
        diameterValue = Dimension(str(diameterString).split(sep=",", maxsplit=1)[0])

        # negating on purpose! We need to transform the coordinate system
        # from positive y to negative y:
        yPos = -yPos

        return Hole(
            instanceXmlElement.attrib['moduleIdRef'],
            title,
            xPos,
            yPos,
            transformElement2MatrixString(instanceXmlElement.find("./views/pcbView/geometry/transform")),
            diameterValue,
            attributes
        )

    def asScad(self):
        """get a string representation to be used in an scad file."""
        data = dict()
        data['module_name'] = self.module_name
        data['moduleIdRef'] = self.moduleIdRef
        data['title'] = self.title
        data['module'] = self.module_name
        data['partXPos'] = str(self.partXPos.asMm())
        data['partYPos'] = str(self.partYPos.asMm())
        data['diameter'] = str(self.diameter.asMm())
        data['attributes'] = self.attributes
        data['params'] = self.params

        if self.matrix is not None:
            data['multmatrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"
        else:
            data['multmatrix'] = ""

        return """// Hole: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}',
translate([{partXPos},{partYPos},0]) //position
{multmatrix}{{
    {module}({diameter}, {params});
}}""".format(**data)

    def __str__(self):
        return "Hole: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', PCBXPos: '{}mm', PCBYPos: '{}mm', matrix: '{}', diameter: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.partXPos.asMm(), self.partYPos.asMm(), self.matrix, self.diameter.asMm())


class Dimension:

    """A dimension. Unit conversion included."""
    unit_conversion_table = dict({
        'pxI': 72,
        'px': 90,
        'pt': 72,
        'pc': 6,
        'mm': 25.4,
        'cm': 2.54,
        'in': 1,
        'mil': 1000
    })

    def __init__(self, inputStringOrValue, unit="", isIllustrator=False):
        """Create a new  Dimension. Unit us either supplied in the input
        string or suplied with the unit variable."""
        if type(inputStringOrValue) is str:

            # split the input string into value and unit
            unitFromInput = ""
            value = inputStringOrValue

            while not value[-1].isdigit():
                unitFromInput = value[-1] + unitFromInput
                value = value[:-1]

            if unit != "" and unit != unitFromInput:
                raise ValueError("Can't interpret input! The string has the unit '{}' but the unit given is '{}'.".format(unitFromInput, unit))

            unit = unitFromInput
        else:
            value = inputStringOrValue

        if unit == "":
            unit = "px"
        if isIllustrator:
            if unit == "px":
                unit = unit + "I"
            else:
                raise ValueError("Only the unit 'px' can have isIllustrator==true, '{}' dont.".format(unit))

        if unit in Dimension.unit_conversion_table:
            value = float(value) / Dimension.unit_conversion_table[unit]
        else:
            raise ValueError("The unit '{}' is not known!".format(unit))

        self.isIllustrator = isIllustrator
        self.value = value

    def getAs(self, unit):
        if unit in Dimension.unit_conversion_table:
            if Dimension.unit_conversion_table[unit] is int:
                return math.fsum([self.value] * Dimension.unit_conversion_table[unit])
            else:
                return self.value * Dimension.unit_conversion_table[unit]
        else:
            raise ValueError("The unit '{}' is not known!".format(unit))

    def asMm(self):
        return self.getAs("mm")

    def asIn(self):
        return self.getAs("in")

    def asPx(self):
        return self.getAs("px")

    def __str__(self):
        return str(self.value) + "in"

    def __repr__(self):
        return str(self.value) + "in"

    def __add__(self, other):
        v = self.value + other.value
        ret = Dimension(0)
        ret.value = v
        return ret

    def __sub__(self, other):
        v = self.value - other.value
        ret = Dimension(0)
        ret.value = v
        return ret

    def __mul__(self, other):
        v = self.value * other.value
        ret = Dimension(0)
        ret.value = v
        return ret

    def __truediv__(self, other):
        v = self.value / other.value
        ret = Dimension(0)
        ret.value = v
        return ret

    def __neg__(self):
        ret = Dimension(0)
        ret.value = -self.value
        return ret

# ###################### STRING HELPERS ########################


def transformElement2MatrixString(element):
    """Get a OpenSCAD compatible 4x4 matrix of the given 3x3 Qtransform Matrix.
    http://qt-project.org/doc/qt-4.8/qtransform.html
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#multmatrix
    http://forum.openscad.org/Multmatrix-and-its-mysterious-4th-row-for-idiots-td10506.html"""

    if element is None:
        return None

    data = dict(element.attrib)
    data['m31'] = Dimension(data['m31']).asMm()
    data['m32'] = Dimension(data['m32']).asMm()

    # negating on purpose! We need to transform the coordinate system
    # from positive y to negative y:
    data['m32'] = -data['m32']

    return """[
[ {m11:<10}, {m12:<10}, 0         , {m31:<10}],
[ {m21:<10}, {m22:<10}, 0         , {m32:<10}],
[ 0         , 0         , 1         , 0         ],
[ 0         , 0         , 0         , 1         ]
]""".format(**data)

# ####################### WORKHORSE ########################


def getParts(xmlRoot, attributes=dict()):
    """Get a list of the parts ON this PCB"""
    boardsTitles = list()  # which of the parts are boards?
    for boardElement in xmlRoot.findall("./boards/board"):
        boardsTitles = boardsTitles + [boardElement.attrib['instance']]

    # relevant instances ON the pcb.
    # right now "on" means: geometry.z > 0
    # TODO: Find a better way to determine if the Part belongs to the
    # PCB.
    relevantParts = list()

    # As xml.etree.ElementTree's XPath implementation does not allow
    # xmlRoot.findall("./instances/instance/views/pcbView/geometry[@z > 0]")
    # we need to help our self here by selecting them our self.

    for instance in xmlRoot.findall("./instances/instance"):
        try:
            if not txt_match_in_patternset(instance.find("./views/pcbView").attrib['layer'], pcbView_layer_whitelist_pattern):
                continue
        except AttributeError:
            continue
        if not txt_match_in_patternset(str(instance.attrib['moduleIdRef']), moduleIdRef_blacklist_pattern):
            geometry = instance.find("./views/pcbView/geometry")
            if geometry is not None:
                instanceTitle = instance.find("./title").text
                if instanceTitle in boardsTitles:
                    p = PCB.buildFromInstanceXmlElement(instance, attributes)
                elif instance.attrib['moduleIdRef'] == "HoleModuleID":
                    p = Hole.buildFromInstanceXmlElement(instance, attributes)
                else:
                    p = Part.buildFromInstanceXmlElement(instance, attributes)
                relevantParts = relevantParts + [p]
            else:
                printConsole("INFO: '{}' does not have XPath:'{}' that IS strange!".format(instance.attrib, "./views/pcbView/geometry"), 2)
        else:
            printConsole("INFO: Ignoring '{}' as it is blacklisted!".format(instance.attrib['moduleIdRef']), 2)
    return relevantParts


def getAttributes(xmlRoot):
    """Extract the Attributes from the file.
    TODO: Allow more than one note and merging of attributes"""

    attributes = dict()
    for instance in xmlRoot.findall("./instances/instance"):
        try:
            if instance.attrib['moduleIdRef'] == "NoteModuleID" and instance.find("./title").text.startswith("attribute"):  # TODO It would be more elegant to do this with XPath.
                txt = ""
                txt = txt_from_note(instance)
                try:
                    jsonAttributes = json.loads(txt)
                except ValueError as err:
                    printConsole("ERROR: Problem with json syntax from the note named: '{}':".format(instance.find("./title").text), 0)
                    printConsole(txt_prefix_each_line(txt, "    ", False, False), 0)
                    printConsole(err, 0)
                    raise err
                return jsonAttributes
        except AttributeError:
            pass
    return attributes


# ####################### SCRIPT PART ########################

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Creates a 3D Model (OpenSCAD) of the PCB in a Fritzing Sketch.")
    parser.add_argument("INPUT_FILE", help="The Fritzing Sketch File (.fzz) to use.")
    parser.add_argument("-o", "--output", nargs="?", default=None, const="", help="Write output to an .scad File instead to console. (if not defined further 'foo.fzz' becomes 'foo.scad')")
    parser.add_argument("-m", "--module-name", help="The name of the OpenSCAD module that will be created. (default: 'foo.fzz' creates 'module foo()')")
    parser.add_argument("-g", "--show-groundplate", help="Show a 'groundplate' for each part. This might be helpful when creating and testing new models.", action="store_true")
    parser.add_argument("-c", "--center", help="Center the PCB in the coordinate system (not implemented yet).", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="-v -vv- -vvv increase output verbosity")
    parser.add_argument("-l", "--list", help="List the parts and their position in the given input file and exit.", action="store_true")
    parser.add_argument('-V', '--version', action='version', version="%(prog)s " + str(VERSION))
    args = parser.parse_args()

    printConsole("fzz2scad " + str(VERSION), 1)  # Say hi

    # get filename
    inputFzzFileName = args.INPUT_FILE

    # get filename of the fz file in the fzz file
    inputFzFileName = getFilesThatEndWith(inputFzzFileName, ".fz")[0]  # We take the first and hope the best.

    # get XML Root of the fz File
    xmlRoot = getXMLRoot(inputFzzFileName, inputFzFileName)

    attributes = getAttributes(xmlRoot)
    printConsole("ATTRIBUTES:\n" + str(attributes), 1)

    # get the Parts in the given xml tree
    parts = getParts(xmlRoot, attributes)

    # Execution depending on the given arguments

    # list parts and exit
    if args.list:
        printConsole("Parts:", 0)
        for part in parts:
            printConsole(part, 0)
        exit(0)

    outFileFileCommentTemplate = """@filename: {filename}
@created-with: fzz2scad v{version!s} (https://github.com/htho/fzz2scad)
"""

    outFileModuleCommentTemplate = """@created-with: fzz2scad v{version!s} (https://github.com/htho/fzz2scad)
{module-dependencies}
"""

    # The Template for the output file
    outFileTemplate = """{fileComment}

{moduleComment}
module {module_name}(){{
    {translate}{{
{parts}
    }}
}}
"""

    # Values to write into the output file.
    outFileTemplateValues = dict()
    outFileCommentTemplateValues = dict()
    outFileCommentTemplateValues['version'] = VERSION

    # where to write to?
    outFileName = (os.path.splitext(os.path.basename(inputFzzFileName))[0]) + ".scad"
    if args.output is not None and args.output != "":
        outFileName = args.output

    outFileCommentTemplateValues['filename'] = outFileName

    if args.module_name is not None:
        outFileTemplateValues['module_name'] = args.module_name
    else:
        outFileTemplateValues['module_name'] = (os.path.splitext(os.path.basename(inputFzzFileName))[0])

    if args.center:
        outFileTemplateValues['translate'] = "translate([0,0,0])"
        # TODO get translation coordinates in order to center the PCB
    else:
        outFileTemplateValues['translate'] = ""

    # Create the scad strings from the stored parts.
    outFileTemplateValues['parts'] = []
    # Create a list of the module dependencies.
    outFileCommentTemplateValues['module-dependencies'] = []
    for part in parts:
        outFileTemplateValues['parts'] = outFileTemplateValues['parts'] + [part.asScad()]
        outFileCommentTemplateValues['module-dependencies'].append("@module-dependency: " + part.module_name)
    outFileTemplateValues['parts'] = "\n\n\n".join(outFileTemplateValues['parts'])
    outFileTemplateValues['parts'] = txt_prefix_each_line(outFileTemplateValues['parts'], "        ")

    outFileCommentTemplateValues['module-dependencies'] = set(outFileCommentTemplateValues['module-dependencies'])
    outFileCommentTemplateValues['module-dependencies'] = "\n".join(outFileCommentTemplateValues['module-dependencies'])

    # The complete file as a string
    outFileTemplateValues['fileComment'] = outFileFileCommentTemplate.format(**outFileCommentTemplateValues)
    outFileTemplateValues['moduleComment'] = outFileModuleCommentTemplate.format(**outFileCommentTemplateValues)
    outFileTemplateValues['fileComment'] = "/**\n" + txt_prefix_each_line(outFileTemplateValues['fileComment'], " * ") + "\n */"
    outFileTemplateValues['moduleComment'] = "/**\n" + txt_prefix_each_line(outFileTemplateValues['moduleComment'], " * ") + "\n */"
    outString = outFileTemplate.format(**outFileTemplateValues)

    # where to write to?
    if args.output is not None:

        with open(outFileName, 'w') as f:
            f.write(outString)
    else:
        printConsole(outString, 0)

    exit(0)
