/** @filename: 	switch_and_led.model.lib.scad */



/** !!!!! DUMMY ENTITY !!!!! */
module mResistorModuleID(){/* Origin: None */

}

/**
 * A 5mm LED. High Quality Version.
 * @author: 	Hauke Thorenz <htho@thorenz.net>
 * @note: 	fzz2scad-compatible, see https://github.com/htho/fzz2scad
 * @param: distanceFromPCB 	Sometimes the LED does not touch the pcb.
 * @tag-list: 	ed, 5mm, hq, fzz2scad-compatible
 * @version: 	0.1
 * @license-link: 	http://creativecommons.org/licenses/by-sa/4.0/
 * @license: 	This work is licensed under the Creative Commons
 * Attribution-ShareAlike 4.0 International License.
 * To view a copy of this license, visit
 * http://creativecommons.org/licenses/by-sa/4.0/.
 * @variable-dependency: commonLegLength 	
 * @variable-dependency: commonLegDiameter 	
 * @license-short: 	cc-by-sa-4.0
 * @uri: 	https://github.com/htho/fzz2scad-lib/lib/electronic_components/active/semiconductors/diodes/leds/standard5mm.scad
 * @category-list: 	electronic_component, active, semiconductor, led
 * @fritzing: 	https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/5mm_LED.svg
 * @datasheet: 	https://cdn-reichelt.de/documents/datenblatt/A500/LED_5MM_GE.pdf
 */
module led5mm_hq(distanceFromPCB=0){/* Origin: '../../../scadlib-electronic-components/active/semiconductors/diodes/leds/standard5mm.scad'(44:1) */
    
      rm = 2.54;
      
      dSocket=5.8;
      hSocket=1.0;
      
      dMain=5.0;
      hMain=7.7;
      
      hCathode=commonLegLength-commonLegLength/2;  
      hAnode=commonLegLength;
    
      dCathodeAnode = commonLegDiameter;
      translate([0,0,distanceFromPCB]) //moving according to distanceFromPCB
      rotate([0,0,90]){ //rotating it so the flat edge is on the "upper" side (2D) which is the "back" side in 3D 
      translate([-(rm/2),0,0]){ //Translating so the center is on connector0
        union(){
          difference(){
            cylinder(hSocket, d=dSocket); //Socket
              translate([dSocket/2,0,hSocket/2]) cube([(dSocket-dMain), dSocket, hSocket+1], true);
            }
          
            translate([0,0,hSocket]) cylinder(hMain-(dMain/2), d=dMain); //main
            translate([0,0,hSocket]) translate([0,0,hMain-(dMain/2)]) sphere(d=dMain);
          
            translate([-(rm/2),0,-hAnode/2]) cube([dCathodeAnode,dCathodeAnode,hAnode], true); //anode
            translate([+(rm/2),0,-hCathode/2]) cube([dCathodeAnode,dCathodeAnode,hCathode], true); //cathode
          }
        }
      }
}

/**
 * A simple parametric perfboard.
 * 
 * Spacing is 100mil = 2.54mm = 0.1in
 * @author: 	Hauke Thorenz <htho@thorenz.net>
 * @license-link: 	http://creativecommons.org/licenses/by-sa/4.0/
 * @license: 	This work is licensed under the Creative Commons
 * Attribution-ShareAlike 4.0 International License.
 * To view a copy of this license, visit
 * http://creativecommons.org/licenses/by-sa/4.0/.
 * @note: 	fzz2scad-compatible, see https://github.com/htho/fzz2scad
 * @license-short: 	cc-by-sa-4.0
 * @tag-list: 	perfboard, pcb, prototyping, fzz2scad-compatible
 * @uri: 	https://github.com/htho/fzz2scad-lib/lib/electronic_components/electromechanical/other/printed_circuit_boards/perfboards.scad
 * @param: depth 	Depth of this PCB
 * @param: width 	Width of this PCB
 * @param: height 	Height of this PCB (1.2mm and 1.6mm are common heights)
 * @category-list: 	electronic_component, electromechanical, other, printed_circuit_board
 * @version: 	0.1
 */
module perfboardPCB_100mil(width, depth, height){/* Origin: '../../../scadlib-electronic-components/electromechanical/other/printed_circuit_boards/perfboards.scad'(43:1) */
    
      rm = 2.54;
      rmWidth = floor(width/rm)*rm;
      rmDepth = floor(depth/rm)*rm;
      dDrill = 1;
      hDrill = height+2;
    
        mirror([0,-1,0])
        difference(){
          translate([width/2,depth/2,-height/2]) cube([width, depth, height], true);
          
          union(){
            for (i = [0:rm:+rmWidth]){
              for (j = [0:rm:+rmDepth]){
                translate([i,j,-height/2]) cylinder(h=hDrill, d=dDrill,center=true);
              }
            }
          }
        }
    
}

/**
 * ESP10XX a slide switch. High quality Version.
 * @author: 	Hauke Thorenz <htho@thorenz.net>
 * @note: 	fzz2scad-compatible, see https://github.com/htho/fzz2scad
 * @note: 	THIS IS NOT THE FRITZINGS STANDARD SPDT SWITCH! It is pin
 * compatible but slightly bigger and has a different slide mechanism.
 * @tag-list: 	SPDT, slide switch, fzz2scad-compatible, hq
 * @version: 	0.1
 * @license-link: 	http://creativecommons.org/licenses/by-sa/4.0/
 * @license: 	This work is licensed under the Creative Commons
 * Attribution-ShareAlike 4.0 International License.
 * To view a copy of this license, visit
 * http://creativecommons.org/licenses/by-sa/4.0/.
 * @variable-dependency: commonLegLength 	
 * @variable-dependency: commonLegDiameter 	
 * @license-short: 	cc-by-sa-4.0
 * @uri: 	https://github.com/htho/fzz2scad-lib/lib/electronic_components/electromechanical/switches/switches/SPDT/ESP10XX.scad
 * @category-list: 	electronic_component, electromechanical, switch, SPDT
 * @manufacturer: 	EXCEL CELL ELECTRONIC
 * @manufacturer-product: 	ESP10XX
 * @source: 	https://cdn-reichelt.de/documents/datenblatt/C200/DS_ESP_SERIE.pdf
 * @source: 	https://github.com/sparkfun/Pro_Micro/blob/master/Hardware/Pro_Micro.brd
 * @source: 	https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/jumper_3_100mil.svg
 */
module ESP10XX_hq(){/* Origin: '../../../scadlib-electronic-components/electromechanical/switches/switches/SPDT/ESP10XX.scad'(47:1) */
    
      rm = 2.54;
      
      widthSocket=10;
      depthSocket=2.5;
      heightSocket=4.5;
      
      widthLeg=0.6;
      depthLeg=0.5;
      heightLeg=commonLegLength;
      
      sliderWidth = 8.4;
      sliderHeight = 1.5;
      
      rotate([0,0,-90]){ //rotating it so the orientation fits the Fritzing part 
        translate([rm,0,0]){ //Translating so the center is on connector0
          translate([0,0,heightSocket/2]) cube([widthSocket, depthSocket, heightSocket], true); //body
          
          translate([-rm,0,-commonLegLength/2]) cube([commonLegDiameter, commonLegDiameter, commonLegLength],true); //leg
          translate([0,0,-commonLegLength/2]) cube([commonLegDiameter, commonLegDiameter, commonLegLength],true); //leg
          translate([rm,0,-commonLegLength/2]) cube([commonLegDiameter, commonLegDiameter, commonLegLength],true); //leg
          
          //slider
          translate([0,0,heightSocket]) cube([sliderWidth, depthSocket, sliderHeight], true);
    
        }
      }
}