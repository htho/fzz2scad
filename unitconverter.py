'''
    unitconverter.py from fzz2scad: Converts lengths with the given unit
    as a string to another unit.
    
    Copyright (C) 2015  Hauke Thorenz <htho@thorenz.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
VERSION = 0.1
import argparse

def printConsole(s, minimumVerbosityLevel):
	global args
	if args.verbosity >= minimumVerbosityLevel:
		print(s)

def in2mm(v):
	return v*25.4


#Ported from https://github.com/fritzing/fritzing-app/blob/master/src/utils/textutils.cpp
def convertToInches(value, orgUnit, isIllustrator=False, overrideUnit=None, fallbackUnit="px"):
	orgUnit = orgUnit.lower() #workaround for caseInsensetive
	divisor = 1.0
	
	if overrideUnit is not None:
		printConsole("Overriding original unit '{}' with '{}'!".format(orgUnit, overrideUnit), 1)
	
	if orgUnit == "":
		printConsole("No unit given, falling back to '{}'!".format(fallbackUnit), 1)
		unit = fallbackUnit
	else:
		unit = orgUnit

	if (unit == ("cm")):
		divisor = 2.54
	elif (unit == ("mm")):
		divisor = 25.4
	elif (unit == ("in")):
		divisor = 1.0
	elif (unit == ("px")):
		if (isIllustrator):
			divisor = 72.0
		else:
			divisor = 90.0
	elif (unit == ("mil")):
		divisor = 1000.0
		chop = 3
	elif (unit == ("pt")):
		divisor = 72.0
	elif (unit == ("pc")):
		divisor = 6.0
	else:
		#default to Qt's standard internal units if all else fails
		divisor = 90.0
		printConsole("Unknown original unit '{}' using divisor={!s}!".format(orgUnit, divisor), 0)

	result = float(value)
	printConsole("result={}, divisor={}, return=(result/divisor)={}in".format(result, divisor, (result / divisor)), 2)
	
	return result / divisor


class ListAction(argparse.Action):
    def __call__(self, parser, *args, **kwargs):
        parser.exit(message="""
Available Input Units
	px (default if no unit is given)
	pt
	pc

	cm
	mm

	in
	mil

Available Output Units
	mm (default)
	in
	px
""")

parser = argparse.ArgumentParser()

parser.add_argument("input", help="Any length with any unit")
parser.add_argument("-s", "--setunit", help="Override/Set input unit")
parser.add_argument("-o", "--outputunit", help="Specify the output unit (default: mm)", default="mm")
parser.add_argument("-a", "--appendunit", help="append unit to output", action="store_true")
parser.add_argument("--isillustrator", help="passes isIllustrator to the convert function. This affects the conversion from px. Fritzing developers might know what this does.", action="store_true")
parser.add_argument('-l', "--list", action=ListAction, nargs=0, help="List available units and exit.")
parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase output verbosity")
parser.add_argument('-V', '--version', action='version', version="%(prog)s "+str(VERSION))

args = parser.parse_args()

printConsole("converter "+str(VERSION), 1)
printConsole("From fzz2scad (https://github.com/htho/fzz2scad)\n", 1)

orgUnit = ""
valueWithoutUnit = args.input

while not valueWithoutUnit[-1].isdigit():
	orgUnit = valueWithoutUnit[-1] + orgUnit
	valueWithoutUnit = valueWithoutUnit[:-1]

printConsole("Converting from '{}' to '{}'".format(orgUnit, args.outputunit), 1)

inchValue = convertToInches(valueWithoutUnit, orgUnit, args.isillustrator)
if args.appendunit:
	appendix = args.outputunit
else:
	appendix = ""

if(args.outputunit == "mm"):
	printConsole(str(in2mm(inchValue))+appendix,0)
elif(args.outputunit == "in"):
	printConsole(str(inchValue)+appendix, 0)
else:
	printConsole("Can't convert to '{}' unknown output unit! Use -l to see the known units.".format(args.outputunit), 0)

exit(0)
