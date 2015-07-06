/**
 * @filename: switch_and_led.scad
 * @created-with: fzz2scad v0.1 (https://github.com/htho/fzz2scad)
 */

/**
 * 
 * @created-with: fzz2scad v0.1 (https://github.com/htho/fzz2scad)
 * @module-dependency: m1238DBDC00_toggle_switch
 * @module-dependency: m5mmColorLEDModuleID
 * @module-dependency: mResistorModuleID
 * @module-dependency: mTwoLayerRectanglePCBModuleID
 */
module switch_and_led(){
    {
        // PCB: module_name: 'mTwoLayerRectanglePCBModuleID', moduleIdRef: 'TwoLayerRectanglePCBModuleID', title: 'PCB', attributes: '{}', params: 'pcbHeight=1.2,width=18.8579,depth=16.7126'
        translate([0.03167069555555555,-0.0,0]) //position
        {
            mTwoLayerRectanglePCBModuleID(pcbHeight=1.2,width=18.8579,depth=16.7126);
        }
        
        
        // Part: module_name: 'm1238DBDC00_toggle_switch', moduleIdRef: '1238DBDC00-toggle-switch', title: 'SWITCH'
        translate([8.382,-8.382,0]) //position on the PCB
        multmatrix(m=[
            [ 0         , -1        , 0         , -2.54     ],
            [ 1         , 0         , 0         , -6.096    ],
            [ 0         , 0         , 1         , 0         ],
            [ 0         , 0         , 0         , 1         ]
        ]) //rotation and translation
        {
             translate([1.778,-1.778,0]) m1238DBDC00_toggle_switch(drillDepth=50.0); 
        }
        
        
        // Part: module_name: 'm5mmColorLEDModuleID', moduleIdRef: '5mmColorLEDModuleID', title: 'LED'
        translate([7.059929999999999,-0.1309511111111111,0]) //position on the PCB
        multmatrix(m=[
            [ -1        , 0         , 0         , 6.20014   ],
            [ 0         , -1        , 0         , -6.20014  ],
            [ 0         , 0         , 1         , 0         ],
            [ 0         , 0         , 0         , 1         ]
        ]) //rotation and translation
        {
             translate([3.10007,-1.251091111111111,0]) m5mmColorLEDModuleID(distanceFromPCB=0.9999999999999999,drillDepth=50.0); 
        }
        
        
        // Part: module_name: 'mResistorModuleID', moduleIdRef: 'ResistorModuleID', title: 'R1'
        translate([9.2075,-6.5278,0]) //position on the PCB
        multmatrix(m=[
            [ 0         , -1        , 0         , 4.940299999999999],
            [ 1         , 0         , 0         , -7.124700000000001],
            [ 0         , 0         , 1         , 0         ],
            [ 0         , 0         , 0         , 1         ]
        ]) //rotation and translation
        {
             translate([0.9524999999999999,-1.0921999999999998,0]) mResistorModuleID(); 
        }
    }
}
