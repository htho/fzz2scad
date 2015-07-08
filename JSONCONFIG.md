# JSON Configuration in Fritzing Sketches
**This document is a reference and not a tutorial. For a tutorial see [HOWTO.md](HOWTO.md) and [TUTORIAL.md](testing/step_by_step_example/TUTORIAL.md)**

The configuration is an integral part of the model creation process.
It is very powerful.

In general the configuration is stored in a Note on the PCB layer.
The name of that note starts with "fzz2scad_config" otherwise it won't be interpreted.
The configuration is stored JSON Encoded which allows human and machine
readable and writable storage of the data.

**NOTE that all dimensions/values that are set in this file need a unit!**

The configuration ("object") has two sections ("members"): "attributes" and "modules":

```json
{
    "attributes": {},
    "modules": {}
}
```

## Units
fzz2scad needs to handle different units. All dimensions are converted to
inches internally. If there is no unit given with a dimension, the assumed
unit is px.

Available Units:

    px
    pt
    pc

    cm
    mm

    in
    mil

just append the unit to the value.

## `attributes`
Each part on the PCB may have attributes.
These attributes are available

```json
{
    "attributes": {
        "PARTNAME": {"params": {}, "export": {}, "z": ""}
    },
    "modules": {}
}
```

### `params`
`..."PARTNAME": {"params": {"pcbHeight": "VALUE"} }...`

Some models of parts need parameters that can not be extracted from the
sketch. For example PCBs may have different heights (=z dimension). There
is no way to extract this information as there are 1.2mm and 1.6mm PCBs.

#### `params` for Parts
  * `drillDepth`: mandatory for drill only models
  * `distanceFromPCB`: currently for the pro_micro and leds.
  * ?: In general the models define their parameters.

#### `params` for Holes
  * `drillDepth`: probably just a little more than `pcbHeight`

#### `params` for PCBs
  * `pcbHeight`: The height of this PCB
  

### `export` PARTLY IMPLEMENTED
`..."PARTNAME": {"export": {"INTERNAL_NAME": "EXTERNAL_NAME"} }...`

Sometimes some parameters of the model are needed outside of the model
as a variable.


#### Exportable Values for Parts
  * `x` (x Position of connector0) NOT IMPLEMENTED YET!
  * `y` (y Position of connector0) NOT IMPLEMENTED YET!
  * `z` (y Position of connector0 depending on the z position of the module and the z attribute of this part) NOT IMPLEMENTED YET!
  * `rotation` NOT IMPLEMENTED YET!
  * `title`
  * `isBottom` (0=top; 1=bottom)

#### Exportable Values for Holes
  * `diameter`
  * `x` (x Position of the center) NOT IMPLEMENTED YET!
  * `y` (y Position of the center) NOT IMPLEMENTED YET!
  * `z` (y Position of the center depending on the z position of the module and the z attribute of this hole) NOT IMPLEMENTED YET!
  * `rotation` NOT IMPLEMENTED YET!
  * `title`

#### Exportable Values for PCBs
  * `width` (horizontal dimension `x` in Fritzing and OpenSCAD)
  * `height` (vertical dimension `y` in Fritzing and OpenSCAD (=depth in OpenSCAD))
  * `pcbHeight` (taken from the `params`, dimension `z` OpenSCAD (=height in OpenSCAD))
  * `x` (x Position of the top left corner) NOT IMPLEMENTED YET!
  * `y` (y Position of the top left corner) NOT IMPLEMENTED YET!
  * `z` (z Position of the top left corner depending on the z position of the module and the z attribute of this pcb) NOT IMPLEMENTED YET!
  * `rotation` NOT IMPLEMENTED YET!
  * `title`

### `z`
`..."PARTNAME": {"z": "VALUE" }...`
The distance from the PCB/Module.


## `modules`
All parts in the sketch (naturally) are part of a module.
There may be more than one module in a sketch. For example if there are
multiple PCBs.

This section is optional, but necessary to center a module.

```json
{
    "attributes": {},
    "modules": {
        "MODULENAME": {"default": true, "frames": [], "parts": [], "center": "", "z": "", "export": {} },
    }
}
```

### `default`
If `..."MODULENAME": {"default": true}...` all parts that don't belong to any other
module belong to this module.

### `frames`
`..."MODULENAME": {"frames": ["FRAMENAME"]}...`

In the schematic layer, frames can be defined. All parts in that frame
belong to that frame. This is a list of the frames. The parts in these
frames belong to this module.

### `pcbs` NOT IMPLEMENTED YET
`..."MODULENAME": {"pcbs": ["PCBNAME"]}...`

All parts and holes on this PCB belong to this module.

### `parts`
`..."MODULENAME": {"parts": ["PARTNAME|PCBNAME|HOLENAME"]}...`

Some parts are not represented in the schematic view (eg. PCBs and Holes)
these can be added to the model here.

### `center`
`..."MODULENAME": {"center": "PCBNAME|HOLENAME"}...`

Translates the whole module in a way that the center of the given PCB or Hole is in the origin ([0,0,0]).

### `z`
`..."MODULENAME": {"z": "VALUE"}...`

translate the whole module on the z axis.

### `export`
`..."MODULENAME": {"export": {"INTERNAL_NAME": "EXTERNAL_NAME"} }...`

currently only the z Value of a module can be exported.
