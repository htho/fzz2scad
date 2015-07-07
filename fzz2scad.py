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
import sys

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


def printConsole(message, minimumVerbosityLevel):
    """Write the given string to the console. To be printed
    args.verbose needs to be >= minimumVerbosityLevel."""
    global args
    if args.verbose >= minimumVerbosityLevel:
        print(message)


def printErrorConsole(message, minimumVerbosityLevel):
    print(message, file=sys.stderr)


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


def determineOutFile(defaultFilenameToDeriveFrom=None, defaultExtensionInfix=None, defaultExtensionOverride=None):
    global args
    if args.output is None:
        return None
    else:
        if args.output == "":
            if defaultFilenameToDeriveFrom is None:
                outFile = "out"
                if defaultExtensionInfix is not None:
                    outFile = outFile + "." + defaultExtensionInfix
                if defaultExtensionOverride is not None:
                    outFile = outFile + "." + defaultExtensionOverride
            else:
                outFile = os.path.basename(defaultFilenameToDeriveFrom).rsplit(".", 1)
                if defaultExtensionInfix is not None:
                    outFile[0] = outFile[0] + "." + defaultExtensionInfix
                if defaultExtensionOverride is not None:
                    outFile[1] = defaultExtensionOverride
                outFile = outFile[0] + outFile[1]
        else:
            outFile = args.output
        return outFile


def outputHelper(fileContent, outFile):
    global args
    override = True
    if outFile is not None and os.path.exists(outFile):
        if args.override:
            override = True
            pass
        elif args.dont_override:
            override = False
        else:
            ans = None
            while ans is None:
                tmp_ans = input("'{}' already exists. Do you want to override it? (y/n)".format(outFile))
                if tmp_ans.strip().lower() == "y":
                    ans = True
                elif tmp_ans.strip().lower() == "n":
                    ans = False
                else:
                    print("Please type 'y' for Yes and 'n' for No.\n")
            if ans is True:
                override = True
            else:
                override = False

    if outFile is None or override is False:
        printConsole(fileContent, 0)
    else:
        with open(outFile, 'w') as f:
            f.write(fileContent)

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

    def __init__(self, moduleIdRef, title, partXPos, partYPos, matrix, bottom, attributes, schematicCoords):
        """Create a new part instance. This Constructor will seldom be
        called directly.

        TODO: Allow regular expressions for finding attributes
        TODO: merge attributes (attributes may be defined in a regular expression and explicitly)"""

        self.schematicCoords = schematicCoords
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
            self.params = dict()

        if "z" in self.attributes.keys():
            self.partZPos = Dimension(self.attributes.pop("z"))
        else:
            self.partZPos = Dimension(0)

        # TODO: Use RegEx Magic instead
        for c in self.module_name:
            if c not in frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"):
                self.module_name = self.module_name.replace(c, "_")

    def paramsAsString(self):
        ret = []
        for k, v in self.params.items():
            v = Dimension(v)
            ret.append("{}={}".format(k, v.asMm()))
        return ",".join(ret)

    @staticmethod
    def getPrototype(moduleIdRef):
        """Get static Information about this part.
        return dict('svgWidth':?, 'svgHeihgt':?, 'xOffset':?. 'yOffset':?)
        svgWidth/Height: Size of the SVG that represents this parts PCB
        footprint. Needed for rotation.
        Offset: Position of connector0 IN the SVG
        """
        if moduleIdRef not in Part.partPrototypes:
            printConsole("INFO: Creating Prototype for moduleIdRef='" + moduleIdRef + "'...", 2)
            Part.partPrototypes[moduleIdRef] = dict()

            if moduleIdRef == "HoleModuleID":
                # Fetching information from https://github.com/fritzing/fritzing-app/blob/master/resources/parts/svg/core/pcb/hole.svg
                Part.partPrototypes[moduleIdRef]['svgWidth'] = Dimension("0.075in")
                Part.partPrototypes[moduleIdRef]['svgHeight'] = Dimension("0.075in")

                # position of center IN the svg.
                Part.partPrototypes[moduleIdRef]['xOffset'] = Dimension("27.7") * (Dimension("0.075in") / Dimension("75"))
                Part.partPrototypes[moduleIdRef]['yOffset'] = -(Dimension("27.7") * (Dimension("0.075in") / Dimension("75")))

            else:
                global inputFzzFileName
                global xmlRoot

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

            printConsole("      Prototype '" + moduleIdRef + "': " + repr(Part.partPrototypes[moduleIdRef]), 2)

        return Part.partPrototypes[moduleIdRef]

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create a Part from the given instance Element in the tree of
        of an .fz file.
        """

        moduleIdRef = instanceXmlElement.attrib['moduleIdRef']

        partXPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['x'])
        partYPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['y'])

        schematicGeometry = instanceXmlElement.find("./views/schematicView/geometry")
        schematicCoords = (Dimension(schematicGeometry.attrib['x']), Dimension(schematicGeometry.attrib['y']))

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
            attributes,
            schematicCoords
        )

    def asScad(self):
        """get a string representation to be used in an scad file."""
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
        data['params'] = self.paramsAsString()

        data['module'] = self.module_name
        data['partXPos'] = self.partXPos.asMm()
        data['partYPos'] = self.partYPos.asMm()
        data['partZPos'] = self.partZPos.asMm()
        data['svgZ'] = 1.0  # How tall should the groundplate be?

        if self.matrix is not None:
            data['multmatrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"
        else:
            data['multmatrix'] = ""

        global args
        if args.show_groundplate:
            data['groundplate'] = "%translate([{svgWidth}/2,-{svgHeight}/2,{partZPos}-{svgZ}/2]) cube([{svgWidth},{svgHeight},{svgZ}],true);".format(**data)
        else:
            data['groundplate'] = ""

        if self.bottom:
            data['bottom_handling'] = "mirror([0,0,1])"
        else:
            data['bottom_handling'] = ""

        return"""// Part: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}'
translate([{partXPos},{partYPos},partZPos]) //position on the PCB
{multmatrix}{{
    {bottom_handling} translate([{xOffset},{yOffset},0]) {module}({params}); {groundplate}
}}""".format(**data)

    def __str__(self):
        return "Part: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', partXPos: '{}mm', partYPos: '{}mm', partZPos: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.partXPos.asMm(), self.partYPos.asMm(), self.partZPos.asMm())


class PCB(Part):
    """A Part representing a PCB with the given dimensions."""

    def __init__(self, moduleIdRef, title, partXPos, partYPos, matrix, width, depth, attributes):
        super().__init__(moduleIdRef, title, partXPos, partYPos, matrix, False, attributes, None)  # It is not possible to have a PCB on the bottom. Isnt it?
        self.width = width
        self.depth = depth
        self.params['width'] = str(self.width)
        self.params['depth'] = str(self.depth)

        if "pcbHeight" not in self.params.keys():
            raise AttributeError('A PCB must have the parameter \'pcbHeight\'. Add a note like this to the PCB Layer: {{"attributes": {{"{}":{{"params":"{{"pcbHeight"="1.2mm"}}}}}}}}'.format(self.title))

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
        data['partZPos'] = str(self.partZPos.asMm())
        data['attributes'] = self.attributes
        data['params'] = self.paramsAsString()

        if self.matrix is not None:
            data['multmatrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"
        else:
            data['multmatrix'] = ""

        return """// PCB: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}'
translate([{partXPos},{partYPos},{partZPos}]) //position
{multmatrix}{{
    {module}({params});
}}""".format(**data)

    def __str__(self):
        return "PCB: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', PCBXPos: '{}mm', PCBYPos: '{}mm',  PCBZPos: '{}mm', matrix: '{}', width: '{}mm', depth: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.partXPos.asMm(), self.partYPos.asMm(), self.partZPos.asMm(), self.matrix, self.width.asMm(), self.depth.asMm())


class Hole(Part):
    """A Part representing a Hole."""

    def __init__(self, moduleIdRef, title, partXPos, partYPos, matrix, diameter, attributes):
        super().__init__(moduleIdRef, title, partXPos, partYPos, matrix, False, attributes, None)  # It is not possible to have a Hole on the bottom. Isnt it?
        self.diameter = diameter
        if "drillDepth" not in self.params:
            raise AttributeError('A Hole must have the parameter \'drillDepth\'. Add a note like this to the PCB Layer: {{"attributes": {{"{}":{{"params":"drillDepth=50"}}}}\nNote that the diameter is extracted from the sketch, so it must not be set as attribute here.'.format(self.title))
        self.params['diameter'] = str(self.diameter)

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create this Hole from the given instanceXmlElement """
        global xmlRoot
        title = instanceXmlElement.find("./title").text

        xPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['x'])
        yPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['y'])

        diameterString = instanceXmlElement.find("./property[@name='hole size']").attrib['value']
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
        proto = Part.getPrototype(self.moduleIdRef)
        data = dict()

        data['svgWidth'] = proto['svgWidth'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['svgHeight'] = proto['svgHeight'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['xOffset'] = proto['xOffset'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['yOffset'] = proto['yOffset'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['svgZ'] = 1.0  # How tall should the groundplate be?

        data['module_name'] = self.module_name
        data['moduleIdRef'] = self.moduleIdRef
        data['title'] = self.title
        data['module'] = self.module_name
        data['partXPos'] = str(self.partXPos.asMm())
        data['partYPos'] = str(self.partYPos.asMm())
        data['partZPos'] = str(self.partZPos.asMm())
        data['attributes'] = self.attributes
        data['params'] = self.paramsAsString()

        global args
        if args.show_groundplate:
            data['groundplate'] = "%translate([{svgWidth}/2,-{svgHeight}/2,{partZPos}-{svgZ}/2]) cube([{svgWidth},{svgHeight},{svgZ}],true);".format(**data)
        else:
            data['groundplate'] = ""

        if self.matrix is not None:
            data['multmatrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"
        else:
            data['multmatrix'] = ""

#         return """// Hole: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}',
# translate([{partXPos},{partYPos},0]) //position
# {multmatrix}{{
#     {module}({params});
# }}""".format(**data)
        return"""// Hole: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}',
translate([{partXPos},{partYPos},{partZPos}]) //position on the PCB
{multmatrix}{{
    translate([{xOffset},{yOffset},0]) {module}({params}); {groundplate}
}}""".format(**data)

    def __str__(self):
        return "Hole: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', HoleXPos: '{}mm', HoleYPos: '{}mm', HoleZPos: '{}mm', matrix: '{}', diameter: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.partXPos.asMm(), self.partYPos.asMm(), self.partZPos.asMm(), self.matrix, self.diameter.asMm())


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

            if unit != "" and unitFromInput != "" and unit != unitFromInput:
                raise ValueError("Can't interpret input! The string has the unit '{}' but the unit given is '{}'.".format(unitFromInput, unit))
            elif unit == "" and unitFromInput != "":
                unit = unitFromInput
            else:  # (unit != "" and unitFromInput == "") or (unit == unitFromInput)
                # uint = unit
                pass
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

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

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
        if isinstance(other, Dimension):
            v = self.value * other.value
        else:
            v = self.value * other
        ret = Dimension(0)
        ret.value = v
        return ret

    def __truediv__(self, other):
        if isinstance(other, Dimension):
            v = self.value / other.value
        else:
            v = self.value / other
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

# ####################### WORKHORSES ########################


def getParts(xmlRoot, attributes=dict()):
    """Get a list of the parts ON this PCB"""
    boardsTitles = list()  # which of the parts are boards?
    for boardElement in xmlRoot.findall("./boards/board"):
        boardsTitles = boardsTitles + [boardElement.attrib['instance']]

    # relevant instances ON the pcb.
    # right now "on" means: geometry.z > 0
    # TODO: Find a better way to determine if the Part belongs to the
    # PCB.
    relevantParts = dict()

    # As xml.etree.ElementTree's XPath implementation does not allow
    # xmlRoot.findall("./instances/instance/views/pcbView/geometry[@z > 0]")
    # we need to help our self here by selecting them our self.

    for instance in xmlRoot.findall("./instances/instance"):
        try:
            if not txt_match_in_patternset(instance.find("./views/pcbView").attrib['layer'], pcbView_layer_whitelist_pattern):
                printConsole("INFO: Ignoring '{}' as it is not whitelisted!".format(instance.attrib['moduleIdRef']), 3)
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
                printConsole("INFO: Adding '{}' title='{}'".format(instance.attrib['moduleIdRef'], p.title), 2)
                relevantParts[p.title] = p
            else:
                printConsole("INFO: Strange! '{}' does not have XPath:'{}' that IS strange!".format(instance.attrib, "./views/pcbView/geometry"), 2)
        else:
            printConsole("INFO: Ignoring '{}' as it is blacklisted!".format(instance.attrib['moduleIdRef']), 2)
    return relevantParts


def getConfig(xmlRoot, moduleNameOrPrefix):
    """Extract the configuration from the sketch.
    TODO: Allow more than one note and merging of configuration notes"""
    ret = dict({"attributes": dict(), "modules": dict()})
    for instance in xmlRoot.findall("./instances/instance"):
        try:
            if instance.attrib['moduleIdRef'] == "NoteModuleID":  # TODO It would be more elegant to do this with XPath.
                title = instance.find("./title").text
                if title == "fzz2scad_config" or title.startswith("fzz2scad_config"):
                    txt = ""
                    txt = txt_from_note(instance)
                    try:
                        jsonData = json.loads(txt)
                    except ValueError as err:
                        printConsole("ERROR: Problem with json syntax from the note named: '{}':".format(instance.find("./title").text), 0)
                        printConsole(txt_prefix_each_line(txt, "    ", False, False), 0)
                        printConsole(err, 0)
                        raise err
                    if "attributes" in jsonData.keys():
                        ret["attributes"] = jsonData["attributes"]
                    if "modules" in jsonData.keys():
                        for moduleName in list(jsonData["modules"].keys()):
                            ret["modules"][moduleNameOrPrefix + "_" + moduleName] = jsonData["modules"].pop(moduleName)
        except AttributeError:
            pass
    if not ret["modules"]:  # empty?
        ret["modules"][moduleNameOrPrefix] = {"default": True}
    return ret


def xyInAbcd(xy=(), abcd=dict()):
    if xy is None or abcd is None:
        return False
    elif xy[0] < abcd[0] or abcd[1] < xy[0]:
        return False
    elif xy[1] < abcd[2] or abcd[3] < xy[1]:
        return False
    else:
        return True


def splitPartsToModules(xmlRoot, parts, configModules):
    ret = dict()
    defaultModuleName = None

    for moduleName, modelConfig in configModules.items():
        printConsole("INFO: Processing module '{}'.".format(moduleName), 2)
        ret[moduleName] = dict()
        if "frames" in modelConfig:
            printConsole("INFO: Found 'frames' list in configuration for module '{}'.".format(moduleName), 2)
            for frameTitle in modelConfig['frames']:
                # find frame from schema, find items in this frame, add to list
                printConsole("INFO: Looking for frame '{}'.".format(frameTitle), 2)
                instance = xmlRoot.find("./instances/instance[@moduleIdRef='SchematicFrameModuleID'][title='" + frameTitle + "']")
                if instance:
                    # get coordinates of the frame
                    geometry = instance.find(".views/schematicView/geometry")
                    x1 = Dimension(geometry.attrib["x"])
                    y1 = Dimension(geometry.attrib["y"])
                    x2 = x1 + Dimension(instance.find(".property[@name='width']").attrib["value"], unit="mm")
                    y2 = y1 + Dimension(instance.find(".property[@name='height']").attrib["value"], unit="mm")
                    abcd = (x1, x2, y1, y2)
                    printConsole("INFO: Found Frame '{}' for model '{}' with Coordinates '(x1,x2,y1,y2)={}'.".format(frameTitle, moduleName, abcd), 2)

                    # find parts that are in abcd
                    for partTitle in sorted(list(parts.keys())):
                        if xyInAbcd(parts[partTitle].schematicCoords, abcd):
                            printConsole("INFO: Part '{}' in Frame '{}' {}.".format(partTitle, frameTitle, str(parts[partTitle].schematicCoords)), 2)
                            ret[moduleName][partTitle] = parts.pop(partTitle)
                else:
                    printConsole("WARNING: Frame '{}' not found but it was set in the configuration for the model '{}'.".format(frameTitle, moduleName), 1)

        if "pcb" in modelConfig:
            # TODO find the pcb and the items on this pcb, add to list
            pass
        if "default" in modelConfig:
            defaultModuleName = moduleName
        if "parts" in modelConfig:
            printConsole("INFO: Found 'parts' list in cofiguration for module '{}'.".format(moduleName), 2)
            for partTitle in modelConfig["parts"]:
                if partTitle in parts:
                    printConsole("INFO: Adding Part '{}' to Module '{}' as it is set in the 'parts' list in the configuration.".format(partTitle, moduleName), 2)
                    ret[moduleName][partTitle] = parts.pop(partTitle)
                else:
                    printConsole("WARNING: Part '{}' not found but it was set in the configuration for the module '{}'.".format(partTitle, moduleName), 1)

    if defaultModuleName is not None:
        printConsole("INFO: Found the default module '{}'.".format(defaultModuleName), 2)
        for partTitle in list(parts.keys()):
            printConsole("INFO: Adding the part '{}' to the default module '{}'.".format(partTitle, defaultModuleName), 2)
            ret[defaultModuleName][partTitle] = parts.pop(partTitle)
    elif defaultModuleName is None and parts:  # parts is not empty
        printConsole("WARINING: There is no default module. But there are parts without a module.", 1)
        printConsole("WARINING: These parts do not belong to any module:\n          " + repr(parts.keys()) + "\n          Check your Sketch. You may add {\"default\" : true} to a module.", 1)
    return ret


def createModuleString(moduleName, moduleParts, center, configuration):
    moduleCommentTemplate = """
@created-with: fzz2scad v{version!s} (https://github.com/htho/fzz2scad)
{module-dependencies}
"""
    moduleTemplate = """{moduleComment}
module {module_name}(){{
    {translate}{{
        difference(){{
            union(){{
{parts}
            }}
{holes}
        }}
    }}
}}"""

    values = dict()
    values['version'] = VERSION

    values['module_name'] = moduleName

    translate = [0, 0, 0]
    if "modules" in configuration.keys():
        if moduleName in configuration["modules"].keys():
            module = configuration["modules"][moduleName]
            if "z" in module.keys():
                translate[2] = Dimension(module["z"]).asMm()
            if "center" in module.keys():
                if module["center"] in moduleParts.keys():
                    printConsole("INFO: centering '{}'".format(module["center"]), 3)
                    centerEntity = moduleParts[module["center"]]
                    if isinstance(centerEntity, PCB):
                        translate[0] = - (centerEntity.width.asMm() / 2) - centerEntity.partXPos.asMm()
                        translate[1] = (centerEntity.depth.asMm() / 2) - centerEntity.partYPos.asMm()
                    elif isinstance(centerEntity, Hole):
                        proto = Part.getPrototype("HoleModuleID")
                        translate[0] = -(centerEntity.partXPos.asMm() + proto['xOffset'].asMm() * Dimension(centerEntity.params["diameter"]).asMm())
                        translate[1] = -(centerEntity.partYPos.asMm() + proto['yOffset'].asMm() * Dimension(centerEntity.params["diameter"]).asMm())
#                    elif isinstance(centerEntity, Part):
#                         # TODO Test
#                         translate[0] = -(centerEntity.partXPos.asMm() + proto['xOffset'].asMm())
#                         translate[1] = -(centerEntity.partYPos.asMm() + proto['yOffset'].asMm())
                    else:
                        raise RuntimeError("Can only center PCBs and Holes.")
    values['translate'] = "translate({})".format(repr(translate))

    values['holes'] = []
    values['parts'] = []
    values['module-dependencies'] = []

    for partName, partInstance in moduleParts.items():
        if isinstance(partInstance, Hole):
            values['holes'].append(partInstance.asScad())
        else:
            values['parts'].append(partInstance.asScad())
        values['module-dependencies'].append("@module-dependency: " + partInstance.module_name)

    values['parts'] = sorted(values['parts'])
    values['parts'] = "\n\n\n".join(values['parts'])
    values['parts'] = txt_prefix_each_line(values['parts'], "                    ")

    values['holes'] = sorted(values['holes'])
    values['holes'] = "\n\n\n".join(values['holes'])
    values['holes'] = txt_prefix_each_line(values['holes'], "                    ")

    values['module-dependencies'] = sorted(set(values['module-dependencies']))
    values['module-dependencies'] = "\n".join(values['module-dependencies'])

    values['moduleComment'] = moduleCommentTemplate.format(**values)
    values['moduleComment'] = "/**\n" + txt_prefix_each_line(values['moduleComment'], " * ") + "\n */"
    return moduleTemplate.format(**values)

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
    parser.add_argument('-V', '--version', action='version', version="%(prog)s " + str(VERSION))
    parser.add_argument("-o", "--output", nargs="?", default=None, const="", help="Write output to an .scad File instead to console. (if not defined further 'foo.fzz' becomes 'foo.scad')")
    parser.add_argument("--override", action="store_true", help="Override existing output files without asking.")
    parser.add_argument("--dont-override", action="store_true", help="Do not override any existing output files - Print to console instead.")
    parser.add_argument("--ask", default="true", action="store_true", help="Ask if an existing file should be overwritten. (default)")

    args = parser.parse_args()

    printConsole("fzz2scad " + str(VERSION), 1)  # Say hi

    # get filename
    inputFzzFileName = args.INPUT_FILE

    outputFileName = determineOutFile(args.INPUT_FILE, None, ".scad")

    # get filename of the fz file in the fzz file
    inputFzFileName = getFilesThatEndWith(inputFzzFileName, ".fz")[0]  # We take the first and hope the best.

    printConsole("PROGRESS: Taking XML Root from input file...", 1)
    xmlRoot = getXMLRoot(inputFzzFileName, inputFzFileName)

    printConsole("PROGRESS: Taking the Configturation from the xml tree...", 1)

    if args.module_name is not None:
        moduleNameOrPrefix = args.module_name
    else:
        moduleNameOrPrefix = str(os.path.split(inputFzzFileName)[-1]).split(".")[0]

    configuration = getConfig(xmlRoot, moduleNameOrPrefix)
    printConsole("CONFIGURATION:" + json.dumps(configuration, sort_keys=True, indent=4), 1)

    printConsole("PROGRESS: Extracting Parts from the xml tree...", 1)
    parts = getParts(xmlRoot, configuration['attributes'])
    printConsole("PARTS:" + repr(parts), 1)

    printConsole("PROGRESS: Sorting parts into modules...", 1)
    modules = splitPartsToModules(xmlRoot, parts, configuration['modules'])
    for moduleName, moduleParts in modules.items():
        printConsole("MODULE '{}':".format(moduleName), 1)
        printConsole("    PARTS: {}".format(moduleParts.keys()), 1)

    # Execution depending on the given arguments

    # list parts and exit
    if args.list:
        printConsole("Parts:", 0)
        for part in parts:
            printConsole(part, 0)
        exit(0)

    fileCommentTemplate = """@filename: {filename}
@created-with: fzz2scad v{version!s} (https://github.com/htho/fzz2scad)
"""

    # The Template for the output file
    fileTemplate = """{fileComment}

{modules}
"""

    # Values to write into the output file.
    fileValues = dict()
    fileValues['version'] = VERSION

    # where to write to?
    fileValues['filename'] = outputFileName

    printConsole("PROGRESS: Creating modules...", 1)
    fileValues['modules'] = []
    for moduleName, moduleParts in modules.items():
        fileValues['modules'].append(createModuleString(moduleName, moduleParts, args.center, configuration))

    fileValues['modules'] = sorted(fileValues['modules'])
    fileValues['modules'] = "\n\n\n".join(fileValues['modules'])

    # The complete file as a string
    fileValues['fileComment'] = fileCommentTemplate.format(**fileValues)
    fileValues['fileComment'] = "/**\n" + txt_prefix_each_line(fileValues['fileComment'], " * ") + "\n */"

    outString = fileTemplate.format(**fileValues)

    outputHelper(outString, outputFileName)
    exit(0)
