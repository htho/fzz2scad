# fzz2scad

Create a 3D Model/Frontplate (OpenSCAD) of/for the PCB in a Fritzing Sketch.

The models are meant to be used to create front plates for 3D-Printed casings.
They might  also be used to create complete 3D-Models of a PCB -
depending on the parts library used.

## Note:
This tool is quite young and I did not have a chance yet to actually print
a case or a frontplate. Please share your experiences with me at the
[Issues Page](https://github.com/htho/fzz2scad/issues).

## The Problem
Fritzing does not support creating front plates for the PCBs created.
Creating a front plate for a PCB from a sketch is almost impossible because there is no
way to get the exact position of the area of a part that needs a hole in
the casing.

## How Does it Work?
fzz2scad opens Fritzings .fzz file, and extracts the coordinates,
rotation and the type of each part on the PCB to an .scad File, which
can be interpreted by OpenSCAD. 

## What do I need?
  * Fritzing (not necessary, but useful)
  * The Fritzing File you want to build a casing for.
  * OpenSCAD
  * The knowledge to use OpenSCAD.
  * A Library with 3D-Models of the parts on your PCB.
  (see: [fzz2scad-lib](https://github.com/htho/fzz2scad-lib))

## Quick Start
	Try this:
	
     $ python fzz2scad.py testing/some_buttons_leds_and_a_switch.fzz --instance --partslib lib/examplelib.scad --output

## Usage

     $ python fzz2scad.py -h
     
     usage: fzz2scad.py [-h] [-o [OUTPUT]] [-p PARTSLIB] [-m MODULE_NAME] [-i] [-g]
                        [-c] [-v] [-l] [-V]
                        INPUT_FILE
     
     Creates a 3D Model (OpenSCAD) of the PCB in a Fritzing Sketch.
     
     positional arguments:
       INPUT_FILE            The Fritzing Sketch File (.fzz) to use.
     
     optional arguments:
       -h, --help            show this help message and exit
       -o [OUTPUT], --output [OUTPUT]
                             Write output to an .scad File instead to console. (if
                             not defined further 'foo.fzz' becomes 'foo.scad')
       -p PARTSLIB, --partslib PARTSLIB
                             The file where modules are stored. If you don't
                             provide a library, you need to include/define the
                             modules yourself.
       -m MODULE_NAME, --module-name MODULE_NAME
                             The name of the OpenSCAD module that will be created.
                             (default: 'foo.fzz' creates 'module foo()')
       -i, --instance        By default, fzz2scad just creates a module. For
                             previewing and debugging purposes, the module can be
                             instanced.
       -g, --show-groundplate
                             Show a 'groundplate' for each part. This might be
                             helpful when creating and testing new models.
       -c, --center          Center the PCB in the coordinate system (not
                             implemented yet).
       -v, --verbose         -v -vv- -vvv increase output verbosity
       -l, --list            List the parts, their position and rotation in the
                             given input file and exit.
       -V, --version         show program's version number and exit
  
# Parts Libraries
fzz2scad does not do much, it simply extracts and transforms the coordinates.

In Fritzing each part has a unique name. This name is tranlated into a
valid OpenSCAD module name. OpenSCAD ignores modules it does not know,
so fzz2scad simply dumps everything on the PCB to the file.

Depending on the quality of the models in the library, there might be a
simple cube, representing a button, or a whole set of cubes and cylinders
describing each detail of the part.

[fzz2scad-lib](https://github.com/htho/fzz2scad-lib) provides a library
and the tools to create a library-file that resolves all the dependencies
for your model.

The library in [fzz2scad-lib](https://github.com/htho/fzz2scad-lib) is a structured
collection of models that may be used with fzz2scad. Referencing every
needed file from this library would be a tedious task. Instead a
library-file that contains all the necessary modules needs to be created.
This library-file file also maps the names that come from Fritzing to the actual
module names in the library.

Visit the [HowTo](HOWTO.md) to learn how to create a model/frontplate
from an fzz file.

# unitconverter.py
A simple script and wrapper around the functions that convert coordinates
in fzz2scad. This script is meant to be used by people who want to
create parts for the libraries. Although it shouldn't even be necessary
to use it at the moment.

## Usage

    $ python unitconverter.py -h
    
    usage: unitconverter.py [-h] [-s SETUNIT] [-o OUTPUTUNIT] [-a]
                            [--isillustrator] [-l] [-v] [-V]
                            input
    
    positional arguments:
      input                 Any length with any unit
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SETUNIT, --setunit SETUNIT
                            Override/Set input unit
      -o OUTPUTUNIT, --outputunit OUTPUTUNIT
                            Specify the output unit (default: mm)
      -a, --appendunit      append unit to output
      --isillustrator       passes isIllustrator to the convert function. This
                            affects the conversion from px. Fritzing developers
                            might know what this does.
      -l, --list            List available units and exit.
      -v, --verbosity       increase output verbosity
      -V, --version         show program's version number and exit

#TODO

See the [Issues](https://github.com/htho/fzz2scad/issues).
