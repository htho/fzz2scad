# How To Create a Frontplate from a .fzz File.

### Overview

  1. Create the PCB Design using Fritzing
  2. Create the OpenSCAD file from the Sketch
    1. Create a configuration for fzz2scad in the sketch
    2. Use fzz2scad.py to create the file
  3. Create the main .scad file that includes the model and (later) the library. It may hold some personal adjustments.
  4. Select or create a .json file that contains the mapping from the module names in the .scad file and the actual model names in the library.
  5. Compile the library and include it in the main file
  6. Move the dummy modules, variables and functions from the library to the main file and set the appropriate values.
  7. Enjoy your model!

## 1. Design your Sketch
I really can't help you here!

Some Hints:

  * Set the title for the parts (The first field of the Inspektor) 
  That makes it easier to address them in the configuration.
  * There is a Problem with Fritzings generic 4-Pin Pushbutton. 
  When aligning to the grid it is not determinable which pin actually
  is aligned and which pins are somewhere between the grid. A workaround
  is to use
  [the stretched version](https://github.com/htho/fritzing-parts/tree/master/core-pushbutton-stretched)
  I created.

## 2. Create the OpenSCAD Model

### 2.1. fzz2scad-configuation in Sketch

### 2.2. fzz2scad.py

## 3. Main File

## 4. Mapping

## 5. Compilation

## 6. Adjustments and Re-Compilation

## 7. What's Next?