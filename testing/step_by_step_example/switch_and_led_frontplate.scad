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

// ------ INCLUDED/USED ------
//include <switch_and_led.model.lib.scad>
// ---------------------------
    /** @filename: 	switch_and_led.model.lib.scad */
    
    
    
    /** !!!!! DUMMY ENTITY !!!!! */
    module mResistorModuleID(){/* Origin: None */
    
    }
    
    /** !!!!! DUMMY ENTITY !!!!! */
    module mTwoLayerRectanglePCBModuleID(){/* Origin: None */
    
    }
    
    /**
     * A 5mm LED. Drill Only Version.
     * @uri: 	https://github.com/htho/fzz2scad-lib/lib/electronic_components/active/semiconductors/diodes/leds/standard5mm.scad
     * @note: 	fzz2scad-compatible, see https://github.com/htho/fzz2scad
     * @license: 	This work is licensed under the Creative Commons
     * Attribution-ShareAlike 4.0 International License.
     * To view a copy of this license, visit
     * http://creativecommons.org/licenses/by-sa/4.0/.
     * @license-short: 	cc-by-sa-4.0
     * @category-list: 	electronic_component, active, semiconductor, led
     * @license-link: 	http://creativecommons.org/licenses/by-sa/4.0/
     * @param: distanceFromPCB 	Sometimes the LED does not touch the pcb.
     * @param: drillDepth 	The depth of the drill for this part.
     * @version: 	0.1
     * @author: 	Hauke Thorenz <htho@thorenz.net>
     * @tag-list: 	led, 5mm, do, fzz2scad-compatible
     * @source: 	https://cdn-reichelt.de/documents/datenblatt/A500/LED_5MM_GE.pdf
     * @source: 	https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/5mm_LED.svg
     */
    module led5mm_do(drillDepth, distanceFromPCB=0){/* Origin: '../../../scadlib-electronic-components/active/semiconductors/diodes/leds/standard5mm.scad'(100:1) */
        
          rm = 2.54;
          dCyl = 5;
        
          translate([0,0,distanceFromPCB]) //moving according to distanceFromPCB
          rotate([0,0,90]){ //rotating it so the flat edge is on the "upper" side (2D) which is the "back" side in 3D
            translate([-(rm/2),0,0]){ //Translating so the center is on connector0
              cylinder(h=drillDepth, d=dCyl); //create the object.
            }
          }
    }
    
    /**
     * ESP10XX a slide switch. Drill Only Version.
     * @uri: 	https://github.com/htho/fzz2scad-lib/lib/electronic_components/electromechanical/switches/switches/SPDT/ESP10XX.scad
     * @note: 	fzz2scad-compatible, see https://github.com/htho/fzz2scad
     * @note: 	THIS IS NOT THE FRITZINGS STANDARD SPDT SWITCH! It is pin
     * compatible but slightly bigger and has a different slide mechanism.
     * @license: 	This work is licensed under the Creative Commons
     * Attribution-ShareAlike 4.0 International License.
     * To view a copy of this license, visit
     * http://creativecommons.org/licenses/by-sa/4.0/.
     * @license-short: 	cc-by-sa-4.0
     * @category-list: 	electronic_component, electromechanical, switch, SPDT
     * @license-link: 	http://creativecommons.org/licenses/by-sa/4.0/
     * @param: drillDepth 	The depth of the drill for this part.
     * @version: 	0.1
     * @author: 	Hauke Thorenz <htho@thorenz.net>
     * @tag-list: 	SPDT, slide switch, fzz2scad-compatible, do
     * @source: 	https://cdn-reichelt.de/documents/datenblatt/C200/DS_ESP_SERIE.pdf
     * @source: 	https://github.com/sparkfun/Pro_Micro/blob/master/Hardware/Pro_Micro.brd
     * @source: 	https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/jumper_3_100mil.svg
     * @manufacturer-product: 	ESP10XX
     * @manufacturer: 	EXCEL CELL ELECTRONIC
     */
    module ESP10XX_do(drillDepth){/* Origin: '../../../scadlib-electronic-components/electromechanical/switches/switches/SPDT/ESP10XX.scad'(145:1) */
        
          rm = 2.54;
          widthSocket=10;
          depthSocket=2.5;  
          rotate([0,0,-90]){ //rotating it so the orientation fits the Fritzing part 
            translate([rm,0,0]){ //Translating so the center is on connector0
              translate([0,0,drillDepth/2]) cube([widthSocket, depthSocket, drillDepth], true); //body
            }
          }
    }
// ---------------------------

// ------ INCLUDED/USED ------
//include <switch_and_led.mapping.scad>
// ---------------------------
    /** @filename: 	switch_and_led.mapping.scad */
    
    
    
    /**
     * A Mapping from 'm5mmColorLEDModuleID' to 'led5mm_do'
     * @module-dependency: led5mm_do 	
     * @argument: 	drillDepth
     * @argument: 	distanceFromPCB
     */
    module m5mmColorLEDModuleID(drillDepth, distanceFromPCB){/* Origin: None */
        led5mm_do(drillDepth=drillDepth, distanceFromPCB=distanceFromPCB);
    }
    
    /**
     * A Mapping from 'm1238DBDC00_toggle_switch' to 'ESP10XX_do'
     * @module-dependency: ESP10XX_do 	
     * @argument: 	drillDepth
     */
    module m1238DBDC00_toggle_switch(drillDepth){/* Origin: None */
        ESP10XX_do(drillDepth=drillDepth);
    }
// ---------------------------

// ------ INCLUDED/USED ------
//include <switch_and_led.scad>
// ---------------------------
    /**
     * @filename: switch_and_led.scad
     * @created-with: fzz2scad v0.1 (https://github.com/htho/fzz2scad)
     */
    
    /**
     * 
     * @created-with: fzz2scad v0.1 (https://github.com/htho/fzz2scad)
     * @module-dependency: m1238DBDC00_toggle_switch
     * @module-dependency: m5mmColorLEDModuleID
     * @module-dependency: mResistorModuleID
     * @module-dependency: mTwoLayerRectanglePCBModuleID
     */
    module switch_and_led(){
        {
            // PCB: module_name: 'mTwoLayerRectanglePCBModuleID', moduleIdRef: 'TwoLayerRectanglePCBModuleID', title: 'PCB', attributes: '{}', params: 'pcbHeight=1.2,width=18.8579,depth=16.7126'
            translate([0.03167069555555555,-0.0,0]) //position
            {
                mTwoLayerRectanglePCBModuleID(pcbHeight=1.2,width=18.8579,depth=16.7126);
            }
            
            
            // Part: module_name: 'm1238DBDC00_toggle_switch', moduleIdRef: '1238DBDC00-toggle-switch', title: 'SWITCH'
            translate([8.382,-8.382,0]) //position on the PCB
            multmatrix(m=[
                [ 0         , -1        , 0         , -2.54     ],
                [ 1         , 0         , 0         , -6.096    ],
                [ 0         , 0         , 1         , 0         ],
                [ 0         , 0         , 0         , 1         ]
            ]) //rotation and translation
            {
                 translate([1.778,-1.778,0]) m1238DBDC00_toggle_switch(drillDepth=50.0); 
            }
            
            
            // Part: module_name: 'm5mmColorLEDModuleID', moduleIdRef: '5mmColorLEDModuleID', title: 'LED'
            translate([7.059929999999999,-0.1309511111111111,0]) //position on the PCB
            multmatrix(m=[
                [ -1        , 0         , 0         , 6.20014   ],
                [ 0         , -1        , 0         , -6.20014  ],
                [ 0         , 0         , 1         , 0         ],
                [ 0         , 0         , 0         , 1         ]
            ]) //rotation and translation
            {
                 translate([3.10007,-1.251091111111111,0]) m5mmColorLEDModuleID(distanceFromPCB=0.9999999999999999,drillDepth=50.0); 
            }
            
            
            // Part: module_name: 'mResistorModuleID', moduleIdRef: 'ResistorModuleID', title: 'R1'
            translate([9.2075,-6.5278,0]) //position on the PCB
            multmatrix(m=[
                [ 0         , -1        , 0         , 4.940299999999999],
                [ 1         , 0         , 0         , -7.124700000000001],
                [ 0         , 0         , 1         , 0         ],
                [ 0         , 0         , 0         , 1         ]
            ]) //rotation and translation
            {
                 translate([0.9524999999999999,-1.0921999999999998,0]) mResistorModuleID(); 
            }
        }
    }
// ---------------------------


difference(){
  translate([0,-16.7126,0]) cube([18.8579, 16.7126, 1]);
  translate([0,0,-5]) switch_and_led();
}