/*
 * basiclib.scad from fzz2scad: A basic library for .scad files created
 * with fzz2scad.
 * 
 * Copyright (C) 2015  Hauke Thorenz <htho@thorenz.net>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

//You might want to tweak this to really get "high quality"
// http://www.tridimake.com/2014/09/how-to-use-openscad-tricks-and-tips-to.html
$fa=0.5; // default minimum facet angle is now 0.5
$fs=0.5; // default minimum facet size is now 0.5 mm 

/* Global variables which are used by the hq models. */
//hq globals
commonLegDiameter = 0.5;
commonLegLength = 5;

/* Global variables which are used by the do models. */
//do globals
commonDrillDepth = 20;

//The parts to use
/* These are all parts in all qualities currently available. This is good
 * for testing purposes. But not the way the libraries ought to be used.
 * Better include only the modules you need */
include <partslib/specific/JTP_1130_do.scad>
include <partslib/specific/JTP_1130_hq.scad>
include <partslib/specific/JTP_1130_lq.scad>

include <partslib/specific/JTP_1130_stretched_do.scad>
include <partslib/specific/JTP_1130_stretched_hq.scad>
include <partslib/specific/JTP_1130_stretched_lq.scad>

include <partslib/specific/ESP10XX_do.scad>
include <partslib/specific/ESP10XX_hq.scad>
include <partslib/specific/ESP10XX_lq.scad>

include <partslib/generic/led5mm_do.scad>
include <partslib/generic/led5mm_hq.scad>
include <partslib/generic/led5mm_lq.scad>

include <partslib/generic/basicPCB_lq.scad>
include <partslib/generic/perfboardPCB_lq.scad>

//translating from Fritzing based Modulenames to The Libraries Modulenames
/* This is where the magic happes!
 * This maps the module calls to the right modules.
 * An example: I have a supplier for the ESP10XX Switches. So I use
 * the model which is pin compatible with the switch in Fritzing. */

//High Quality
module m5mmColorLEDModuleID(){led5mm_hq();}
module m1238DBDC00_toggle_switch(){ESP10XX_hq();}
module m20A9BBEE34_ST(){JTP_1130_stretched_hq();}
module mRectanglePCBModuleID(width, depth){basicPCB_lq(width, depth);}// only available in lq
module mTwoLayerRectanglePCBModuleID(width, depth){basicPCB_lq(width, depth);}// only available in lq

////Low Quality
//module m5mmColorLEDModuleID(){led5mm_lq();}
//module m1238DBDC00_toggle_switch(){ESP10XX_lq();}
//module m20A9BBEE34_ST(){JTP_1130_stretched_lq();}
//module mRectanglePCBModuleID(width, depth){basicPCB_lq(width, depth);}// only available in lq
//module mTwoLayerRectanglePCBModuleID(width, depth){basicPCB_lq(width, depth);}// only available in lq

////Drills only
//module m5mmColorLEDModuleID(){led5mm_do();}
//module m1238DBDC00_toggle_switch(){ESP10XX_do();}
//module m20A9BBEE34_ST(){JTP_1130_stretched_do();}
//module mRectanglePCBModuleID(width, depth){basicPCB_do(width, depth);}// only available in lq
//module mTwoLayerRectanglePCBModuleID(width, depth){basicPCB_do(width, depth);}// only available in lq

