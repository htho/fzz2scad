/* 
 * This work is licensed under the Creative Commons
 * Attribution-ShareAlike 4.0 International License.
 * To view a copy of this license, visit
 * http://creativecommons.org/licenses/by-sa/4.0/.
 * 
 * @license cc-by-sa
 * @author Hauke Thorenz <htho@thorenz.net>
 * @datasheet https://cdn-reichelt.de/documents/datenblatt/C200/TASTER93XX.pdf
 * @fritzing https://github.com/fritzing/fritzing-parts/blob/master/svg/core/pcb/switch-4lead.svg
 * @manufacturer NAMAE
 * @manufacturer-product JTP-1130
 * @type pushbutton, 4pin
 * @todo make the drills cones too. For long Buttons, the gap becomes quite big. But what is a sane offset?
 */

module proto_JTP_1130_stretched_do(){
  rm = 2.54;
  cubeSize = 6;
  legDepth = 0.3;
  
  legDistanceFromPartCenterX = (3*rm)/2;
  legDistanceFromPartCenterY = (2*rm)/2;
  proto_JTP_1130_centerDistanceParam_do(legDistanceFromPartCenterX, legDistanceFromPartCenterY);
}

module proto_JTP_1130_do(){
  cubeSize = 6;
  legDepth = 0.3;
  legDistanceFromPartCenterX = (cubeSize/2)+(legDepth/2);
  legDistanceFromPartCenterY = (4.5/2); //see datasheet
  proto_JTP_1130_centerDistanceParam_do(legDistanceFromPartCenterX, legDistanceFromPartCenterY);
}

module proto_JTP_1130_centerDistanceParam_do(legDistanceFromPartCenterX, legDistanceFromPartCenterY)
{
 //Globals:
 //commonDrillDepth
 
 	cubeSize = 6;
  cubeHeight = 3.6;
  legHeight = 3.5;
  legDepth = 0.3;
  legWidth = 0.7;
  legCenterDistance = 4.5;
  rm = 2.54;

  rotate([0,0,0]){ //rotating it so the orientation fits the Fritzing part 
    translate([-legDistanceFromPartCenterX,legDistanceFromPartCenterY,0]){ //Translating so the center is on connector0
      translate([0,0,]) cylinder(h=commonDrillDepth, d=3.5); //moving part
    }
  }
}

module JTP_1130_do(){proto_JTP_1130_do();}
module JTP_1130A_do(){proto_JTP_1130_do();}
module JTP_1130B_do(){proto_JTP_1130_do();}
module JTP_1130C_do(){proto_JTP_1130_do();}
module JTP_1130D_do(){proto_JTP_1130_do();}
module JTP_1130E_do(){proto_JTP_1130_do();}
module JTP_1130F_do(){proto_JTP_1130_do();}
module JTP_1130P_do(){proto_JTP_1130_do();}
module JTP_1130L_do(){proto_JTP_1130_do();}
module JTP_1130M_do(){proto_JTP_1130_do();}

module JTP_1130_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130A_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130B_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130C_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130D_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130E_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130F_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130P_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130L_stretched_do(){proto_JTP_1130_stretched_do();}
module JTP_1130M_stretched_do(){proto_JTP_1130_stretched_do();}
