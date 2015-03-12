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

module perfboardPCB_lq(width, depth)
{
  rm = 2.54;
  rmWidth = floor(width/rm)*rm;
  rmDepth = floor(depth/rm)*rm;
  height = 1;
  dDrill = 1;
  hDrill = height+2;

    mirror([0,-1,0])
    //translate([width/2,depth/2,-height/2])
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


