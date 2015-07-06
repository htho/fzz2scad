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