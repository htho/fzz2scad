/** @filename: 	switch_and_led.mapping.scad */



/**
 * A Mapping from 'mTwoLayerRectanglePCBModuleID' to 'perfboardPCB_100mil'
 * @module-dependency: perfboardPCB_100mil 	
 * @argument: 	width
 * @argument: 	depth
 * @argument: 	pcbHeight
 */
module mTwoLayerRectanglePCBModuleID(width, depth, pcbHeight){/* Origin: None */
    perfboardPCB_100mil(width=width, depth=depth, height=pcbHeight);
}

/**
 * A Mapping from 'm5mmColorLEDModuleID' to 'led5mm_hq'
 * @module-dependency: led5mm_hq 	
 * @argument: 	distanceFromPCB
 */
module m5mmColorLEDModuleID(distanceFromPCB){/* Origin: None */
    led5mm_hq(distanceFromPCB=distanceFromPCB);
}

/**
 * A Mapping from 'm1238DBDC00_toggle_switch' to 'ESP10XX_hq'
 * @module-dependency: ESP10XX_hq 	
 */
module m1238DBDC00_toggle_switch(){/* Origin: None */
    ESP10XX_hq();
}