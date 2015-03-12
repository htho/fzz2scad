/* 
 * This work is licensed under the Creative Commons
 * Attribution-ShareAlike 4.0 International License.
 * To view a copy of this license, visit
 * http://creativecommons.org/licenses/by-sa/4.0/.
 * 
 * @license cc-by-sa
 * @author Hauke Thorenz <htho@thorenz.net>
 * @datasheet https://cdn-reichelt.de/documents/datenblatt/A500/LED_5MM_GE.pdf
 * @fritzing https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/5mm_LED.svg
 * @manufacturer 
 * @manufacturer-product 
 * @type led
 */

module led5mm_hq()
{
  //Globals:
  //commonLegDiameter
  //commonLegLength
  
  rm = 2.54;
  
  dSocket=5.8;
  hSocket=1.0;
  
  dMain=5.0;
  hMain=7.7;
  
  hCathode=commonLegLength-commonLegLength/2;  
  hAnode=commonLegLength;

  dCathodeAnode = commonLegDiameter;
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

