# Libraries
*Disclaimer: The whole library structure and concept still is a work
in progress.*

There are two key concepts:

 1. The Parts-Library
 2. Library-Instances

The *Parts-Library* is a file structure that provides models of parts.

A *Library-Instance* is collection of aliases, references and settings
defining a file which can be used with he .scad file created by fzz2scad.

 * *Aliases* map between the module-names in the .scad files created by
   fzz2scad and the module-names in the Parts-Library.
 * The file includes *references* to the files in the Parts-Library that
   define the modules. (In fact they are modules that call other modules.)
 * Rhe *settings* apply to global variables that should be used by the
   modules that model parts. E.g. length of legs or depth of drills,
   but also the quality (`$fa` and `$fs`).

##Files and Folder Structure
 * `./lib/`  
    The Library Folder contains files that define a library.
    
    * `./lib/*.scad`  
      Library-Instances.
    
    * `./lib/basiclib.scad`  
      is an Example Library-Instance, which can be used with the
      example files in `./testing/*.fzz`. Look at the comments in this
      file to create your own library.

    * `./lib/partslib/`  
      The Parts-Library

        * `./lib/partslib/template_{do,lq,hq}.scad`  
          Templates to be used to create new models.

        * `./lib/partslib/generic/`  
          Holds generic parts like LEDs.  
          Different manufacturers may have different product names.
          But in the end, they all look the same and have the same model.  
          Chose names that make identifying the part as easy as possible.
          Take `led5mm_do.scad` as an example.

            * `./lib/partslib/generic/*_do.scad`  
              `do` means "*d*rills *o*nly". An LED for example needs a
              drill with an diameter of 5mm. `*_do.scad` only specify
              these drills. No more.

            * `./lib/partslib/generic/*_lq.scad`  
              `lq` means "*l*ow *q*uality". A very simple model of the
              part. In Case of an LED, make a cylinder with the diameter
              of the LED. A Button is most likely a cube.

            * `./lib/partslib/generic/*_hq.scad`  
              `hq` means "*h*igh *q*uality". A detailed model of the part.
              An LED has a sphere on top and a socket below the main
              cylinder. The socket is flattened on the side with the cathode.

        * `./lib/specific/`  
          This is the place for all the unique parts that most likely
          have only one or a handful of manufacturers.  
          Chose unique file- and module names that stick to the name of
          the product series. You may see `./lib/specific/ESP10XX_*.scad`
          and `./lib/specific/JTP_1130_*.scad` as examples.
          
            * `./lib/partslib/specific/*_{do,lq,hq}.scad`  
              The same quality rules apply as for generic parts.

#Creating Modules for the Parts-Library

## Functional requirements for modules
  1. modules have their origin on `connector0` of a part and in `z = 0`.
  2. modules have the same orientation as the parts in Fritzing

### Origin on `connector0`
This sounds a little odd at first. But one has to know, that coordinates
in Fritzing are unintuitive. This counts at least for the coordinates
that are shown in the right panel and stored in the fz file.
These coordinates point at the edges of the SVG-Image that contains
silkscreen and the connector pads. This is odd when modeling a part
using a datasheet.

An Example:
An standard 5mm LED like [this](https://cdn-reichelt.de/documents/datenblatt/A500/LED_5MM_GE.pdf) 
has a diameter of 5mm (obviously). Where? At the Part with the dome!

There is a socket below that. It has a diameter of 5.8mm and is flattened
on the side with the cathode down to the main cylinder.

As the the first maximal dimension is 5.8mm and the second maximal 
dimension is 5.4mm, one might think the module should have a ground area
of 5.8mmm times 5.4mm. The truth is: Fritzings part has a ground area of
6.20014mm times 6.20014mm (=0.2441in according to [`svg.pcb.5mm_LED.svg`](https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/5mm_LED.svg))

BUT: The LED isn't even centered on the image! It is rotated so the
flattened side is on the upper side of the image and at the edge of the
canvas. There is a lot of Space below the LED.

*Connectors are universal!*  
When modeling a part using the datasheet, the positions of the connectors
are at hand, size of the svg and position on it are not. So we use the
connectors as common ground.

### Rotations
Parts are most likely modeled with the datasheet in hand.
A certain orientation seems natural. But the parts in Fritzing might have
a different orientation.
(I modeled the LED from the example above with the flattened side
on the right. The Fritzing part has the flattened side on top.)
To get the default orientation simply drag the part on the PCB in Fritzing.
Use the same orientation for your part.

## Organizational requirements for modules
You may or may not meet these requirements for the parts you use for
your project. These are the current requirements for parts contributed
to this library.

  1. module names are the same as the filenames except for series.
  2. a file contains only one module except for series.
  3. the templates should be used.
  4. comments should be used.
  5. give sources for the datasheet and the svg
  
### Module- and File-Names and Modules per File
*One module per file* and to *name modules and files the same* are simple
conventions that help to keep things consistent.

####Series
Series are a special case. The files may contain multiple modules.

An example are the pushbuttons in
`./lib/partslib/specific/JTP_1130_hq.scad`_
There is a parametric prototype of the module. The actual modules are
named after the correct name for the part according to the datasheet.
The correctly named modules instantiate the Prototype.

### Template Usage
The Templates give a good starting point.

### Comments
The Comments help collecting all the helpful information.
Maybe in the future, the information may be used in some kind of database
setup/info script.

### Source
Providing the sources is helpful to understand the part.

## How to create a Part-Module?
Part-Modules are created using the datasheet. All the necessary dimensions
should be present. To be compatible, connector0 needs to be in the origin
with the body beginning at y=0. Simply imagine the PCB to have its surface
in y=0.

###Which one is connector0?
Good question. I assume it is the one that has the gray "(1)" in the tooltip
for the connector in Fritzing. 

# Creating Library-Instances
In general `./lib/basiclib.scad`  is a good starting point.

### Module Names
The Fritzing program itself does not provide unique names for the parts
via its GUI.
The unique names in stored in the .fz file. fzz2scad extracts them.

You can list them with `python fzz2scad.py myfzz.fzz -l`

Implementation Info:
The module names are the `moduleIdRef` attribute prefixed with an 'm' for
Module. All non characters, and non didgets are replaced with an underscore,
as OpenSCAD only allows these chars in module names.
