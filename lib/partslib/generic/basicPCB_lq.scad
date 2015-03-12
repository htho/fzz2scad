/* 
 * This work is licensed under the Creative Commons
 * Attribution-ShareAlike 4.0 International License.
 * To view a copy of this license, visit
 * http://creativecommons.org/licenses/by-sa/4.0/.
 * 
 * @license cc-by-sa
 * @author Hauke Thorenz <htho@thorenz.net>
 * @datasheet 
 * @fritzing 
 * @manufacturer 
 * @manufacturer-product 
 * @type 
 */

module basicPCB_lq(width, depth)
{
  height=1;

 mirror([0,-1,0])rotate([0,0,0]){ //rotating it so the orientation fits the Fritzing part 
    translate([width/2,depth/2,-height/2]){ //Translating so the center is on connector0
      cube([width, depth, height], true);
    }
  }
}

