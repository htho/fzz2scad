/** @filename: 	switch_and_led.mapping.scad */



/**
 * A Mapping from 'm5mmColorLEDModuleID' to 'led5mm_do'
 * @module-dependency: led5mm_do 	
 * @argument: 	drillDepth
 * @argument: 	distanceFromPCB
 */
module m5mmColorLEDModuleID(drillDepth, distanceFromPCB){/* Origin: None */
    led5mm_do(drillDepth=drillDepth, distanceFromPCB=distanceFromPCB);
}

/**
 * A Mapping from 'm1238DBDC00_toggle_switch' to 'ESP10XX_do'
 * @module-dependency: ESP10XX_do 	
 * @argument: 	drillDepth
 */
module m1238DBDC00_toggle_switch(drillDepth){/* Origin: None */
    ESP10XX_do(drillDepth=drillDepth);
}