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

module led5mm_lq()
{
  rm = 2.54;
  dCyl = 5;
  hCyl = 8.7;
  
  rotate([0,0,90]){ //rotating it so the flat edge is on the "upper" side (2D) which is the "back" side in 3D 
    translate([-(rm/2),0,0]){ //Translating so the center is on connector0
      cylinder(h=hCyl, d=dCyl); //create the object.
    }
  }
}
