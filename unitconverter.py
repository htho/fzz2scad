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
import fzz2scad


class ListAction(argparse.Action):
    def __call__(self, parser, *args, **kwargs):
        parser.exit(message="""
Available Input and Output Units
    pxI (px with isIllustrator)
    px (default input)
    pt
    pc

    cm
    mm (default output)

    in
    mil

""")

parser = argparse.ArgumentParser()

parser.add_argument("input", help="Any length with any of the supported units.")
parser.add_argument("-s", "--setunit", help="Set input unit", default="")
parser.add_argument("-o", "--outputunit", help="Specify the output unit (default: mm)", default="mm")
parser.add_argument("-a", "--appendunit", help="append unit to output", action="store_true")
parser.add_argument("--isillustrator", help="passes isIllustrator to the convert function. This affects the conversion from px. Fritzing developers might know what this does.", action="store_true")
parser.add_argument('-l', "--list", action=ListAction, nargs=0, help="List available units and exit.")
parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
parser.add_argument('-V', '--version', action='version', version="%(prog)s " + str(VERSION))

args = parser.parse_args()

fzz2scad.args = args

fzz2scad.printConsole("converter " + str(VERSION), 1)
fzz2scad.printConsole("From fzz2scad (https://github.com/htho/fzz2scad)\n", 1)

dimension = fzz2scad.Dimension(args.input, args.setunit, args.isillustrator)

outString = str(dimension.getAs(args.outputunit))
if args.appendunit:
    outString = outString + args.outputunit

fzz2scad.printConsole(outString, 0)

exit(0)
