function load() {
    if (GBrowserIsCompatible() ) {
        window.map = new GMap2(document.getElementById("map_canvas"),size=GSize(300,300) );
        window.map.addControl(new GLargeMapControl());
        window.map.addControl(new GMapTypeControl());
        //window.map.setMapType(G_HYBRID_MAP);

        var zoomLevel = 6;


        window.map.setCenter(new GLatLng(37.80738,-122.247147), zoomLevel);
        for (var ark_x in window.arkobjects) {
            if (typeof window.arkobjects[ark_x] !== 'function') { 
            arkobject = window.arkobjects[ark_x];
            //label = CDL.DSC.OAC.mapns.make_ark_object_label(ark_x, arkobject);
            if (arkobject.lat) {
                var point = new GLatLng(arkobject.lat, 
                                        arkobject.lon);
    
                i = new Image();
                i.src = arkobject.thumbnail.src;

                //CDL.DSC.OAC.mapns.marker_bounds.extend(point);
                var marker = new GMarker(point, {draggable:false, });
                //var marker = CDL.DSC.OAC.mapns.createImageMarker(point, ark_x, arkobject, label, window.map.getZoom(), false, false);
                window.map.addOverlay(marker);
                window.arkobjects[ark_x].marker = marker;
            }
        }
      }
//map.setCenter(CDL.DSC.OAC.mapns.marker_bounds.getCenter(), map.getBoundsZoomLevel(CDL.DSC.OAC.mapns.marker_bounds));
    }
}
