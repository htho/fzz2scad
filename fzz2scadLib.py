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
import xml.etree.ElementTree as ET
import html
import os
import math
import re
import sys
import collections
import copy
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

# ####################### HELPERS #####################################


def update(d, u):
    # from http://stackoverflow.com/a/3233356/1635906
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

# static dictionary with information about the different parts.
# key: moduleIdRef
# value: dict() (see getPrototype())
partPrototypes = dict()


def getPrototype(moduleIdRef):
    """Get static Information about this part.
    return dict('svgWidth':?, 'svgHeihgt':?, 'svgOffsetX':?. 'svgOffsetY':?)
    svgWidth/Height: Size of the SVG that represents this parts PCB
    footprint. Needed for rotation.
    Offset: Position of connector0 IN the SVG
    """
    if moduleIdRef not in partPrototypes:
        printConsole("INFO: Creating Prototype for moduleIdRef='" + moduleIdRef + "'...", 2)
        partPrototypes[moduleIdRef] = dict()

        if moduleIdRef == "HoleModuleID":
            # Fetching information from https://github.com/fritzing/fritzing-app/blob/master/resources/parts/svg/core/pcb/hole.svg
            partPrototypes[moduleIdRef]['svgWidth'] = Dimension("0.075in")
            partPrototypes[moduleIdRef]['svgHeight'] = Dimension("0.075in")

            # position of center IN the svg.
            partPrototypes[moduleIdRef]['svgOffsetX'] = Dimension("27.7") * (Dimension("0.075in") / Dimension("75"))
            partPrototypes[moduleIdRef]['svgOffsetY'] = -(Dimension("27.7") * (Dimension("0.075in") / Dimension("75")))

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
            partPrototypes[moduleIdRef]['svgWidth'] = Dimension(svgRoot.find(".").attrib['width'])
            partPrototypes[moduleIdRef]['svgHeight'] = Dimension(svgRoot.find(".").attrib['height'])

            # position of connector0 IN the svg.
            partPrototypes[moduleIdRef]['svgOffsetX'] = Dimension(svgConnector0Element.attrib['cx']) * viewBoxWidthOfAUnit
            partPrototypes[moduleIdRef]['svgOffsetY'] = Dimension(svgConnector0Element.attrib['cy']) * viewBoxHeightOfAUnit

            # negating on purpose! We need to transform the coordinate system from positive y to negative y:
            partPrototypes[moduleIdRef]['svgOffsetY'] = -partPrototypes[moduleIdRef]['svgOffsetY']

        printConsole("      Prototype '" + moduleIdRef + "': " + repr(partPrototypes[moduleIdRef]), 2)

    return partPrototypes[moduleIdRef]

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


class AbstractPart:
    def __init__(self, moduleIdRef, title, xPos, yPos, matrix, attributes):
        """Create a new part instance. This Constructor will seldom be
        called directly."""

        self.moduleIdRef = moduleIdRef
        self.module_name = "m" + moduleIdRef
        for c in self.module_name:
            if c not in frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"):
                self.module_name = self.module_name.replace(c, "_")

        self.title = title

        self.xPos = xPos
        self.yPos = yPos

        self.matrix = matrix

        self.attributes = dict()
        for titleExpression, attribute_data in attributes.items():
            titlePattern = re.compile(titleExpression)
            if titlePattern.fullmatch(self.title):
                self.attributes = update(self.attributes, copy.deepcopy(attribute_data))
        self.zPos = Dimension(0)

        if "z" in self.attributes.keys():
            self.zPos = Dimension(self.attributes.pop("z"))

        self.params = dict()
        if "params" in self.attributes.keys():
            self.params = self.attributes.pop("params")

    def export(self, internal_name):
        if internal_name == "title":
            return self.title
        elif internal_name == "x":
            return self.xPos.asMm()
        elif internal_name == "y":
            return self.yPos.asMm()
        elif internal_name == "z":
            return self.zPos.asMm()
        elif internal_name == "xyz":
            return [self.export("x"), self.export("y"), self.export("z")]
        elif internal_name == "rotation":
            return None
        else:
            return None

    def paramsAsString(self):
        ret = []
        for k, v in self.params.items():
            v = Dimension(v)
            ret.append("{}={}".format(k, v.asMm()))
        return ",".join(ret)

    def _getInfoText(self):
        data = dict()

        data['module_name'] = self.module_name

        # Information extracted from the sketch
        data['moduleIdRef'] = self.moduleIdRef
        data['title'] = self.title
        data['xPos'] = self.xPos.asMm()
        data['yPos'] = self.yPos.asMm()
        data['zPos'] = self.zPos.asMm()

        # Information extracted from the configuration
        data['attributes'] = self.attributes
        data['params'] = self.paramsAsString()

        data['matrix'] = ""
        if self.matrix is not None:
            data['matrix'] = "multmatrix(m=" + txt_prefix_each_line(self.matrix, "    ", ignorefirst=True, ignorelast=True) + ") //rotation and translation\n"

        return data


class Part(AbstractPart):
    """A Part (e.g. Switch or LED)."""

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create a Part from the given instance Element in the tree of
        of an .fz file.
        """

        moduleIdRef = instanceXmlElement.attrib['moduleIdRef']

        xPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['x'])
        yPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['y'])

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
        yPos = -yPos
        return Part(
            moduleIdRef,
            instanceXmlElement.find("./title").text,
            xPos,
            yPos,
            transformElement2MatrixString(instanceXmlElement.find("./views/pcbView/geometry/transform")),
            attributes,
            bottom,
            schematicCoords
        )

    def __init__(self, moduleIdRef, title, xPos, yPos, matrix, attributes, bottom, schematicCoords):
        """Create a new part instance. This Constructor will seldom be
        called directly."""
        super().__init__(moduleIdRef, title, xPos, yPos, matrix, attributes)
        self.bottom = bottom
        self.schematicCoords = schematicCoords
        self.prototype = getPrototype(self.moduleIdRef)

    def export(self, internal_name):
        if internal_name == "isBottom":
            if self.bottom:
                return 1
            else:
                return 0
        else:
            return AbstractPart.export(self, internal_name)

    def _getInfoText(self, showGroundplate=False):
        data = AbstractPart._getInfoText(self)

        # Information about the prototype
        data['svgWidth'] = self.prototype['svgWidth'].asMm()
        data['svgHeight'] = self.prototype['svgHeight'].asMm()
        data['svgOffsetX'] = self.prototype['svgOffsetX'].asMm()
        data['svgOffsetY'] = self.prototype['svgOffsetY'].asMm()

        data['bottom_handling'] = ""
        if self.bottom:
            data['bottom_handling'] = "mirror([0,0,1])"

        data['groundplateHeight'] = 1.0  # How tall should the groundplate be?
        data['groundplate'] = ""
        if showGroundplate:
            data['groundplate'] = "%translate([{svgWidth}/2,-{svgHeight}/2,{zPos}-{groundplateHeight}/2]) cube([{svgWidth},{svgHeight},{groundplateHeight}],true);".format(**data)

        return data

    def asScad(self, showGroundplate=False):
        """get a string representation to be used in an scad file."""
        data = self._getInfoText(showGroundplate)
        data["selfStr"] = str(self)
        return """// {selfStr}
translate([{xPos},{yPos},{zPos}]) //position on the PCB
{matrix}{{
    {bottom_handling} translate([{svgOffsetX},{svgOffsetY},0]) {module_name} ({params}); {groundplate}
}}""".format(**data)

    def __str__(self):
        data = self._getInfoText()
        return "Part: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}', xPos: '{xPos}mm', yPos: '{yPos}mm', zPos: '{zPos}mm'".format(**data)


class Hole(AbstractPart):
    """A Part representing a Hole."""

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, attributes):
        """Create this Hole from the given instanceXmlElement """
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

    def __init__(self, moduleIdRef, title, xPos, yPos, matrix, diameter, attributes):
        super().__init__(moduleIdRef, title, xPos, yPos, matrix, attributes)
        self.diameter = diameter

        if "drillDepth" not in self.params:
            raise AttributeError('A Hole must have the parameter \'drillDepth\'. Add a note like this to the PCB Layer: {{"attributes": {{"{}":{{"params":"drillDepth=50"}}}}\nNote that the diameter is extracted from the sketch, so it must not be set as attribute here.'.format(self.title))
        self.params['diameter'] = str(self.diameter)

        self.prototype = getPrototype(moduleIdRef)

    def export(self, internal_name):
        if internal_name == "diameter":
            return self.diameter.asMm()
        else:
            return AbstractPart.export(self, internal_name)

    def _getInfoText(self, showGroundplate=False):
        data = AbstractPart._getInfoText(self)

        # Information about the prototype
        data['svgWidth'] = self.prototype['svgWidth'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['svgHeight'] = self.prototype['svgHeight'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['svgOffsetX'] = self.prototype['svgOffsetX'].asMm() * Dimension(self.params["diameter"]).asMm()
        data['svgOffsetY'] = self.prototype['svgOffsetY'].asMm() * Dimension(self.params["diameter"]).asMm()

        data['groundplateHeight'] = 1.0  # How tall should the groundplate be?
        data['groundplate'] = ""
        if showGroundplate:
            data['groundplate'] = "%translate([{svgWidth}/2,-{svgHeight}/2,{zPos}-{groundplateHeight}/2]) cube([{svgWidth},{svgHeight},{groundplateHeight}],true);".format(**data)

        return data

    def asScad(self, showGroundplate=False):
        """get a string representation to be used in an scad file."""
        data = self._getInfoText(showGroundplate)
        data["selfStr"] = str(self)
        return"""// {selfStr}
translate([{xPos},{yPos},{zPos}]) //position on the PCB
{matrix}{{
    translate([{svgOffsetX},{svgOffsetY},0]) {module_name}({params}); {groundplate}
}}""".format(**data)

    def __str__(self):
        return "Hole: module_name: '{}', moduleIdRef: '{}', title: '{}', attributes: '{}', params: '{}', HoleXPos: '{}mm', HoleYPos: '{}mm', HoleZPos: '{}mm', matrix: '{}', diameter: '{}mm'".format(self.module_name, self.moduleIdRef, self.title, self.attributes, self.params, self.xPos.asMm(), self.yPos.asMm(), self.zPos.asMm(), self.matrix, self.diameter.asMm())


class PCB(AbstractPart):
    """A Part representing a PCB with the given dimensions."""

    @staticmethod
    def buildFromInstanceXmlElement(instanceXmlElement, xmlRoot, attributes):
        """Create this PCB from the given instanceXmlElement """
        title = instanceXmlElement.find("./title").text
        boardXmlElement = xmlRoot.find("./boards/board[@instance='" + title + "']")

        xPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['x'])
        yPos = Dimension(instanceXmlElement.find("./views/pcbView/geometry").attrib['y'])

        # negating on purpose! We need to transform the coordinate system
        # from positive y to negative y:
        yPos = -yPos

        return PCB(
            instanceXmlElement.attrib['moduleIdRef'],
            title,
            xPos,
            yPos,
            transformElement2MatrixString(instanceXmlElement.find("./views/pcbView/geometry/transform")),
            Dimension(boardXmlElement.attrib['width']),
            Dimension(boardXmlElement.attrib['height']),
            attributes
        )

    def __init__(self, moduleIdRef, title, xPos, yPos, matrix, width, depth, attributes):
        # A PCB can't be on the bottom. It is not represented in the schematic.
        super().__init__(moduleIdRef, title, xPos, yPos, matrix, attributes)
        self.width = width
        self.depth = depth

        self.params['width'] = str(self.width)
        self.params['depth'] = str(self.depth)
        if "pcbHeight" not in self.params.keys():
            raise AttributeError('A PCB must have the parameter \'pcbHeight\'. Add a note like this to the PCB Layer: {{"attributes": {{"{}":{{"params":"{{"pcbHeight"="1.2mm"}}}}}}}}'.format(self.title))

    def export(self, internal_name):
        if internal_name == "width":
            return self.width.asMm()
        elif internal_name == "depth":
            return self.depth.asMm()
        elif internal_name == "pcbHeight":
            return Dimension(self.params["pcbHeight"]).asMm()
        elif internal_name == "wdh":
            return [self.export("width"), self.export("depth"), self.export("pcbHeight")]
        else:
            return AbstractPart.export(self, internal_name)

    def _getInfoText(self, showGroundplate=False):
        data = AbstractPart._getInfoText(self)

        data['width'] = str(self.width)
        data['depth'] = str(self.depth)
        data['pcbHeight'] = str(Dimension(self.params['pcbHeight']))

        return data

    def asScad(self):
        """get a string representation to be used in an scad file."""
        data = self._getInfoText()
        data["selfStr"] = str(self)
        return """// {selfStr}
translate([{xPos},{yPos},{zPos}]) //position
{matrix}{{
    {module_name} ({params});
}}""".format(**data)

    def __str__(self):
        data = self._getInfoText()
        return "PCB: module_name: '{module_name}', moduleIdRef: '{moduleIdRef}', title: '{title}', attributes: '{attributes}', params: '{params}', xPos: '{xPos}mm', yPos: '{yPos}mm',  zPos: '{zPos}mm', matrix: '{matrix}', width: '{width}mm', depth: '{depth}mm', pcbHeight: '{pcbHeight}mm'".format(**data)


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


def transformMatrixElement2AngleAndTranslationVector(element):
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

    translation = [data['m31'], data['m32'], 0]

    printConsole(math.degrees(math.acos(float(data['m11']))), 0)
    printConsole(math.degrees(-math.asin(float(data['m12']))), 0)
    printConsole(math.degrees(math.asin(float(data['m21']))), 0)
    printConsole(math.degrees(math.acos(float(data['m22']))), 0)

#    if math.acos(data['m11']) == -math.asin(data['m12']) == math.asin(data['m21']) == math.acos(data['m22']):
#        angle = math.degrees(math.acos(data['m11']))
#    else:
#        raise RuntimeError("Could not calculate angle from matrix. The values are inconsistent.")
    return (math.degrees(math.acos(Dimension(data['m11']).asMm())), translation)


def transformElement2MatrixString(element):
    """Get a OpenSCAD compatible 4x4 matrix of the given 3x3 Qtransform Matrix.
    http://qt-project.org/doc/qt-4.8/qtransform.html
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#multmatrix
    http://forum.openscad.org/Multmatrix-and-its-mysterious-4th-row-for-idiots-td10506.html"""

    # printErrorConsole(transformMatrixElement2AngleAndTranslationVector(element), 0)

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
    boardsTitles = list()  # which of the parts are boards?
    for boardElement in xmlRoot.findall("./boards/board"):
        boardsTitles = boardsTitles + [boardElement.attrib['instance']]

    relevantParts = dict()

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
                    p = PCB.buildFromInstanceXmlElement(instance, xmlRoot, attributes)
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
    for instance in xmlRoot.findall("./instances/instance[@moduleIdRef='NoteModuleID']"):
        try:
            title = instance.find("./title").text
            if title == "fzz2scad_config" or title.startswith("fzz2scad_config"):
                txt = txt_from_note(instance)
                try:
                    jsonData = json.loads(txt)
                except ValueError as err:
                    printConsole("ERROR: Problem with json syntax from the note named: '{}':".format(instance.find("./title").text), 0)
                    printConsole(txt_prefix_each_line(txt, "    ", False, False), 0)
                    printConsole(err, 0)
                    raise err
                if "attributes" in jsonData.keys():
                    update(ret["attributes"], jsonData["attributes"])
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
                        if isinstance(parts[partTitle], Part) and xyInAbcd(parts[partTitle].schematicCoords, abcd):
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


def createModuleString(moduleName, moduleParts, configuration):
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
}}
{export}
"""

    values = dict()
    values['version'] = VERSION

    values['module_name'] = moduleName

    values["export"] = list()

    translate = [0, 0, 0]
    if "modules" in configuration.keys():
        if moduleName in configuration["modules"].keys():
            module = configuration["modules"][moduleName]
            if "z" in module.keys():
                translate[2] = Dimension(module["z"]).asMm()
            if "export" in module.keys():
                for internal_name, external_name in module["export"].items():
                    if internal_name == "z":
                        values["export"].append("{} = ({});".format(external_name, Dimension(module["z"]).asMm()))
            if "center" in module.keys():
                if module["center"] in moduleParts.keys():
                    printConsole("INFO: centering '{}'".format(module["center"]), 3)
                    centerEntity = moduleParts[module["center"]]
                    if isinstance(centerEntity, PCB):
                        translate[0] = - (centerEntity.width.asMm() / 2) - centerEntity.xPos.asMm()
                        translate[1] = (centerEntity.depth.asMm() / 2) - centerEntity.yPos.asMm()
                    elif isinstance(centerEntity, Hole):
                        proto = Part.getPrototype("HoleModuleID")
                        translate[0] = -(centerEntity.xPos.asMm() + proto['xOffset'].asMm() * Dimension(centerEntity.params["diameter"]).asMm())
                        translate[1] = -(centerEntity.yPos.asMm() + proto['yOffset'].asMm() * Dimension(centerEntity.params["diameter"]).asMm())
#                    elif isinstance(centerEntity, Part):
#                         # TODO Test
#                         translate[0] = -(centerEntity.xPos.asMm() + proto['xOffset'].asMm())
#                         translate[1] = -(centerEntity.yPos.asMm() + proto['yOffset'].asMm())
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

    values["export"] = "\n".join(values["export"])

    return moduleTemplate.format(**values)


def createExportString(parts, configuration):
    export = list()
    if "attributes" in configuration.keys():
        for entityName, entityConfig in configuration["attributes"].items():
            if entityName in parts.keys() and "export" in entityConfig.keys():
                for internal_name, external_name in entityConfig["export"].items():
                    exp = parts[entityName].export(internal_name)
                    if exp is not None:
                        export.append("{} = ({});".format(external_name, exp))
    return "\n".join(export)
