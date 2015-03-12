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
 * @todo: make the legs more true to the original
 * @note this version is stretched so it fits into the standard 2.54rm.
 */
module proto_JTP_1130_stretched_hq(L, I){
  rm = 2.54;
  cubeSize = 6;
  legDepth = 0.3;
  
  legDistanceFromPartCenterX = (3*rm)/2;
  legDistanceFromPartCenterY = (2*rm)/2;
  proto_JTP_1130_centerDistanceParam_hq(L, I, legDistanceFromPartCenterX, legDistanceFromPartCenterY);
}

module proto_JTP_1130_centerDistanceParam_hq(L, I, legDistanceFromPartCenterX, legDistanceFromPartCenterY)
{
 //Globals:
 //commonLegDiameter
 //commonLegLength
  
 	cubeSize = 6;
  cubeHeight = 3.6;
  legHeight = 3.5;
  legDepth = 0.3;
  legWidth = 0.7;
  rm = 2.54;

  rotate([0,0,0]){ //rotating it so the orientation fits the Fritzing part 
    translate([-legDistanceFromPartCenterX,legDistanceFromPartCenterY,(cubeHeight/2)]){ //Translating so the center is on connector0
      cube([cubeSize,cubeSize,cubeHeight],true); //Body
      translate([0,0,cubeHeight/2]) cylinder(h=L-cubeHeight, r1=3.5/2, r2=I/2); //moving part

      mirror([0,0,0])translate([-legDistanceFromPartCenterX,-legDistanceFromPartCenterY,-legHeight]) proto_JTP_1130_hq_leg();
      mirror([0,0,0])translate([-legDistanceFromPartCenterX,+legDistanceFromPartCenterY,-legHeight]) proto_JTP_1130_hq_leg();
      mirror([1,0,0])translate([-legDistanceFromPartCenterX,-legDistanceFromPartCenterY,-legHeight]) proto_JTP_1130_hq_leg();
      mirror([1,0,0])translate([-legDistanceFromPartCenterX,+legDistanceFromPartCenterY,-legHeight]) proto_JTP_1130_hq_leg();
    }
  }
}
module proto_JTP_1130_hq_leg(){
  legHeight = 3.5;
  legWidth = 0.7;
  legDepth = 0.3;
  topPartLength = 0.75;
  bottomPartLength = 0.75;
  legCenterDistance = 4.5;
  rotate([0,0,90]){
    translate([0,0,1+topPartLength/2]) cube([legWidth,legDepth,0.75],true);//top part
    rotate([45,0,0]) translate([0,0.7,0]) cube([legWidth,legDepth,1.2],true);//upper bended part
    rotate([-45,0,0]) translate([0,0.7,0]) cube([legWidth,legDepth,1.2],true);//lower bended part
    translate([0,0,-1-bottomPartLength/2]) cube([legWidth,legDepth,0.75],true);//bottom part
  }
}

/* Table from the datasheet:
 * Bauteil-Nr.	L (mm)	I (mm)	Betätigerfarbe
 * JTP-1130	    4,30	  3,50	  Schwarz
 * JTP-1130A	  5,00	  3,50	  Schwarz
 * JTP-1130B	  9,50	  3,10	  Schwarz
 * JTP-1130C	  8,00	  3,20	  Schwarz
 * JTP-1130D	  13,00	  2,87	  Schwarz
 * JTP-1130E	  7,30	  3,25	  Schwarz
 * JTP-1130F	  7,00	  3,30	  Schwarz
 * JTP-1130P	  8,50	  3,09	  Schwarz
 * JTP-1130L	  17,0	  2,80	  Schwarz
 * JTP-1130M	  6,00	  3,40	  Schwarz
 */

module JTP_1130_stretched_hq(){proto_JTP_1130_stretched_hq(4.30, 3.50);}
module JTP_1130A_stretched_hq(){proto_JTP_1130_stretched_hq(5.00, 3.50);}
module JTP_1130B_stretched_hq(){proto_JTP_1130_stretched_hq(9.50, 3.10);}
module JTP_1130C_stretched_hq(){proto_JTP_1130_stretched_hq(8.00, 3.20);}
module JTP_1130D_stretched_hq(){proto_JTP_1130_stretched_hq(13.00, 2.87);}
module JTP_1130E_stretched_hq(){proto_JTP_1130_stretched_hq(7.30, 3.25);}
module JTP_1130F_stretched_hq(){proto_JTP_1130_stretched_hq(7.00, 3.30);}
module JTP_1130P_stretched_hq(){proto_JTP_1130_stretched_hq(8.50, 3.09);}
module JTP_1130L_stretched_hq(){proto_JTP_1130_stretched_hq(17.0, 2.80);}
module JTP_1130M_stretched_hq(){proto_JTP_1130_stretched_hq(6.00, 3.40);}
