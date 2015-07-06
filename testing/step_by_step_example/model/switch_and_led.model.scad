/**
 * @filename: switch_and_led.model.scad
 * @module-dependency: switch_and_led
 * 
 */
$fa=0.5; // default minimum facet angle is now 0.5
$fs=0.5; // default minimum facet size is now 0.5 mm

/** !!!!! DUMMY ENTITY !!!!! */
commonLegLength = (5); /* Origin: None */

/** !!!!! DUMMY ENTITY !!!!! */
commonLegDiameter = (.4); /* Origin: None */

include <switch_and_led.model.lib.scad>
include <switch_and_led.mapping.scad>
include <switch_and_led.scad>

switch_and_led();

