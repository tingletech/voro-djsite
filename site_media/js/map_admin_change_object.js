var icon = new GIcon(G_DEFAULT_ICON);
icon.image = "http://www.google.com/mapfiles/ms/micons/blue-dot.png";
icon.iconSize = new GSize(32, 32);//first is x-horizontal number`
icon.iconAnchor = new GPoint(15, 31);
icon.infoWindowAnchor = new GPoint(15, 2);

/*
var icon_other_inst = new GIcon(G_DEFAULT_ICON);
//icon_other_inst.image = "http://www.google.com/mapfiles/ms/micons/blue-dot.png";
icon_other_inst.iconSize = new GSize(16, 16);//first is x-horizontal number`
icon_other_inst.iconAnchor = new GPoint(15, 31);
icon_other_inst.infoWindowAnchor = new GPoint(15, 2);
*/

var map;

function createMarker(point, label, zindex) {
        
    if (zindex) {
            zIndex = function (marker, b) {
                return zindex;
            };
    }
    else {
        zIndex = null;
    }

    var marker = new GMarker(point, {draggable:true, icon : icon,  zIndexProcess:zIndex});
    marker.enableDragging();

    GEvent.addListener(marker, "click", function() {
        marker.openInfoWindowHtml(label);
    });
    GEvent.addListener(marker, "dragend", function() {
            //fill in form for submittal.....
            //maybe easier in main admin page
        //marker.openInfoWindowHtml(marker.getLatLng().toUrlValue());
        //get form elements and put latlng in them
	    var latitude = document.getElementById("id_xtf-geopoint-content_type-object_id-0-lat");
	    var longitude = document.getElementById("id_xtf-geopoint-content_type-object_id-0-lon");
        latitude.value = marker.getLatLng().lat();
        longitude.value = marker.getLatLng().lng();
    
    });
    return marker;
}

function createMarkerFixed(point, label) {
    var marker = new GMarker(point);//, { icon : icon_other_inst});
    GEvent.addListener(marker, "click", function() {
        marker.openInfoWindowHtml(label);
    });
    return marker;
}

function makeMarkerLabel(institutes, institute) {
    var label = '<span style="font-family:Arial;font-size:12px;"><strong>';
    label += institutes[institute].name;
    label += '</strong><br/>';
    label += institutes[institute].address + '<br/>';
    label += institutes[institute].city + ', CA ';
    label += institutes[institute].zip4 + '<br/><br/>';
    label += 'Get directions to this place from:<br/>';
    label += '<form onsubmit="loadDirections(';
    label += institutes[institute].lat + ',' + institutes[institute].lng;
    label += ',this); return false;">';
    label += '<input type="text" name="from" value="" size="25"/></form><br/>';
    label += '<a href="javascript:loadCollection(\'' + institute;
    label += '\')">Browse the collections</a>';
    label += '</span>';
    return label;
}

function initAdminMap(lat, lng, name) {
  if (GBrowserIsCompatible() ) {
    map = new GMap2(document.getElementById("map"));
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    map.setMapType(G_HYBRID_MAP);

    var zoomLevel = 6;
    var point = new GLatLng(lat, lng);
    map.checkResize();
    map.setCenter(point, zoomLevel);
    map.addOverlay(createMarker(point, name, 9999));
  }
}

function load(name) {
  if (GBrowserIsCompatible() ) {
//    map = new GMap2(document.getElementById("map"));
//    map.addControl(new GLargeMapControl());
//    map.addControl(new GMapTypeControl());
//    map.setMapType(G_HYBRID_MAP);
//
//    var zoomLevel = 12;
////    alert("latlng="+ lat + " : " + lng);
//    var point = new GLatLng(lat, lng);
//    map.setCenter(point, zoomLevel);
//    map.addOverlay(createMarker(point, name));

    //if the following exists show map, else register with the 
    //add another button click event to show map
	var latitude = document.getElementById("id_xtf-geopoint-content_type-object_id-0-lat");
    if (latitude) {
	    var longitude = document.getElementById("id_xtf-geopoint-content_type-object_id-0-lon");
        document.getElementById("map").style.display = 'block';
        initAdminMap(latitude.value, longitude.value, name);
    }
    else {
        //attach init to the click on the add
        var rows = "#xtf-geopoint-content_type-object_id-group .tabular.inline-related tbody tr";
        //find the add button
        //alert(django.jQuery(rows));
        //alert(django.jQuery(rows.formset));
        var addButton;
        f = django.jQuery(rows).formset();
        //alert("F "+f);
        //alert("F TAG: "+f.attr("tagName"));
        //alert("F parent"+f.parent().attr("tagName"));
        //this needs to happen after the admin js has run
        if (f.attr("tagName") == "TR") {
            addButton = f.parent().find("tr:last a");
        }
        else {
            addButton = f.filter(":last").next().find("a");
        }
        addButton.click(function() {
                //alert("CLICKED IT");
	        var latitude = document.getElementById("id_xtf-geopoint-content_type-object_id-0-lat");
	        var longitude = document.getElementById("id_xtf-geopoint-content_type-object_id-0-lon");
            document.getElementById("map").style.display = 'block';
            initAdminMap(latitude.value, longitude.value, name);
        });
    }
  }
}

function loadOtherMarker(lat, lng, name) {
    var point = new GLatLng(lat, lng);
    map.addOverlay(createMarkerFixed(point, name));
}

window.onunload = GUnload();

