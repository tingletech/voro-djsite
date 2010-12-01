var CDL = {};
CDL.DSC = {};
CDL.DSC.OAC = {};

CDL.DSC.OAC.mapns = function() {
    return {
        arkobjects:{}, //Ark indexed list of data store markers here too
        marker_bounds:  new GLatLngBounds(),//needed to stretch view of map
    
    linkarkstomap: function () {
        var links = document.body.getElementsByTagName('a');
        for (i=0;i<links.length;i++) {
            if ( links[i].href.indexOf('ark:') > 0) {
                ark = links[i].href.substring(links[i].href.indexOf('ark:'), links[i].href.lastIndexOf('/'));
                //links[i].setAttribute('onClick',  "CDL.DSC.OAC.mapns.showMap('" + ark +"'); return false;"); //IE NOT SUPPORT
                links[i].onclick = function(evt) {
                    if (!evt) evt = window.event;
                    if (!evt.currentTarget) {
                        targ = evt.srcElement;
                    }
                    else {
                        targ = evt.currentTarget;
                    }
                    ark_lcl = targ.href.substring(targ.href.indexOf('ark:'), targ.href.lastIndexOf('/'));
                    CDL.DSC.OAC.mapns.showMap(ark_lcl);
                    return false;
                };
            }
        }
    },

    handleMoveEnd: function() {
        for (var ark in CDL.DSC.OAC.mapns.arkobjects) {
            if (CDL.DSC.OAC.mapns.arkobjects[ark].marker instanceof GMarker) { 
                var marker = CDL.DSC.OAC.mapns.arkobjects[ark].marker;
                var latlng = marker.getLatLng();
                if (window.map.getBounds().containsLatLng(latlng)) {
                    if (marker.isHidden()) {
                        zoomCurrent = window.map.getZoom();
                        if (marker.zoom != zoomCurrent) {
                            var arkobject = CDL.DSC.OAC.mapns.arkobjects[ark];
                            label = CDL.DSC.OAC.mapns.make_ark_object_label(ark, arkobject);
                            CDL.DSC.OAC.mapns.arkobjects[ark].marker = CDL.DSC.OAC.mapns.createImageMarker(marker.getLatLng(), ark, arkobject, label, zoomCurrent, marker.infoWinOpen, marker.selected);

                            window.map.addOverlay(CDL.DSC.OAC.mapns.arkobjects[ark].marker);
                            if (marker.infoWinOpen) {
                                CDL.DSC.OAC.mapns.arkobjects[ark].marker.openInfoWindowHtml(label);
                            }
                            window.map.removeOverlay(marker);
                        }
                        else {
                            marker.show();
                        }
                    }
                }
                else {
                    marker.hide();//or remove?
                }
            }
        }
    },

    handleZoomEnd: function(oldLevel, newLevel) {
        for (var ark in CDL.DSC.OAC.mapns.arkobjects) {
            if (CDL.DSC.OAC.mapns.arkobjects[ark].marker instanceof GMarker) {
                var marker = CDL.DSC.OAC.mapns.arkobjects[ark].marker;
                var latlng = marker.getLatLng();
                if (window.map.getBounds().containsLatLng(latlng)) {
                    var arkobject = CDL.DSC.OAC.mapns.arkobjects[ark];
                    label = CDL.DSC.OAC.mapns.make_ark_object_label(ark, arkobject);
                    CDL.DSC.OAC.mapns.arkobjects[ark].marker = CDL.DSC.OAC.mapns.createImageMarker(marker.getLatLng(), ark, arkobject, label, window.map.getZoom(), marker.infoWinOpen, marker.selected);
                    window.map.addOverlay(CDL.DSC.OAC.mapns.arkobjects[ark].marker);
                    if (marker.infoWinOpen) {
                        CDL.DSC.OAC.mapns.arkobjects[ark].marker.openInfoWindowHtml(label);
                    }
                    window.map.removeOverlay(marker);
                }
                else {
                    marker.hide();//or remove?
                }
            }
        }
    },

    handleNoFlash: function (errorCode) {
          if (errorCode === GStreetviewPanorama.ErrorValues.NO_NEARBY_PANO) {
            CDL.DSC.OAC.mapns.streetviewPanel.setBody('<div><h2>No streetview available at this location</h2></div>');
          }
          if (errorCode === GStreetviewPanorama.ErrorValues.FLASH_UNAVAILABLE) {
            CDL.DSC.OAC.mapns.streetviewPanel.setBody('<div><h2>Error: Flash doesn\'t appear to be supported by your browser');
        }
    },
    
    panelcleanup: function (type, args, x) {
        x.myPano.hide();
        x.myPano.remove();
        x.hide();
    },

    handleInfoWindowBeforeClose: function (errorCode) {
        CDL.DSC.OAC.mapns.panelcleanup('typeproxy', 'argsproxy', CDL.DSC.OAC.mapns.streetviewPanel);
    },

    show_streetview: function (lat, lon, ark, id_elem) {
        var loc = new GLatLng(lat, lon);
        var panoramaOptions = { latlng:loc };
        CDL.DSC.OAC.mapns.streetviewPanel = new YAHOO.widget.Panel("streetview_panel", {
            width: '600px',
            height: '400px',
            fixedcenter: true, 
            constraintoviewport: true, 
            underlay: "shadow", 
            close: true, 
            visible: true, 
            draggable: true,
            dragOnly: true,
            modal: false,
            zindex: 1111
        });
        svPanel = CDL.DSC.OAC.mapns.streetviewPanel;
        svPanel.setHeader("Current Streetview");
        //svPanel.setBody('<div style="width: 100%; height: 100%;" id="' + id_elem + '"></div>'); //IE IS BROKE WITH THIS, want to test?
        svPanel.setBody('<div style="width: 580px; height: 360px; margin-right:auto; margin-left:auto; margin-top:auto; margin-bottom:auto;" id="' + id_elem + '"></div>');
        svPanel.render("mapPanel");
        svPanel.myPano = new GStreetviewPanorama(svPanel.body.firstChild, panoramaOptions);
        GEvent.addListener(svPanel.myPano, "error", CDL.DSC.OAC.mapns.handleNoFlash);
        svPanel.myPano.show();
        svPanel.myPano.checkResize();
        GEvent.addListener(CDL.DSC.OAC.mapns.arkobjects[ark].marker, 'infowindowbeforeclose', CDL.DSC.OAC.mapns.handleInfoWindowBeforeClose);
        svPanel.beforeHideEvent.subscribe(CDL.DSC.OAC.mapns.panelcleanup, svPanel);
        CDL.DSC.OAC.mapns.mapPanel.beforeHideEvent.subscribe(CDL.DSC.OAC.mapns.panelcleanup, svPanel);
        svPanel.show();
    },
    
    calcResize: function(h_img, w_img, h_max, w_max) {
        //resize image calculation
        //retains aspect ratio and makes larger dim == max
        ratio_img = h_img/w_img;
        ratio_max = h_max/w_max;
        if (ratio_img > ratio_max) {//image taller
            img_height = h_max;
            img_width = Math.round(img_height/ratio_img);
        }
        else if (ratio_img < ratio_max) {//panel taller
            img_width = w_max;
            img_height = Math.round(img_width*ratio_img);
            }
        else {//image and panel same ratio
            img_width = w_max;
            img_height = h_max;
        }
        return { width:img_width, height:img_height };
    },

    calcShrink: function(h_img, w_img, h_max, w_max) {
        img_height = h_img;
        img_width = w_img;
        if (h_img > h_max || w_img > w_max) {
            return CDL.DSC.OAC.mapns.calcResize(h_img, w_img, h_max, w_max);
        }
        else {
            return { width:img_width, height:img_height };
        }
    },

    panelImageLoaded: function() {
        h_img = CDL.DSC.OAC.mapns.imgInPanel.height;
        w_img = CDL.DSC.OAC.mapns.imgInPanel.width;
        h_panel = CDL.DSC.OAC.mapns.mapPanel.body.clientHeight-30;
        w_panel = CDL.DSC.OAC.mapns.mapPanel.body.clientWidth-10;
        img_size = CDL.DSC.OAC.mapns.calcShrink(h_img, w_img, h_panel, w_panel);
        CDL.DSC.OAC.mapns.contentPanel.setBody('<img src="' + CDL.DSC.OAC.mapns.imgInPanel.src + '" width="'+ img_size.width + 'px" height="' + img_size.height + 'px" onClick="CDL.DSC.OAC.mapns.contentPanel.destroy();"/>');
        CDL.DSC.OAC.mapns.contentPanel.render(document.body);
        CDL.DSC.OAC.mapns.contentPanel.show();
   },

    openContentPanel: function (ark, image_src) {
        CDL.DSC.OAC.mapns.contentPanel = new YAHOO.widget.Panel("contentPanel",         {
        width: panelWidth + 'px',
        height: panelHeight + 'px',
        fixedcenter: true, 
        //constraintoviewport: true, 
        underlay: "shadow", 
        close: true, 
        visible: true, 
        draggable: true,
        dragOnly: true,
        modal: true,
        //context: [ 'mapPanel', 'tl', 'br', null, [10, 10] ],
        zindex:1000
        });
        CDL.DSC.OAC.mapns.contentPanel.setHeader(CDL.DSC.OAC.mapns.arkobjects[ark].title);
        //CDL.DSC.OAC.mapns.contentPanel.setFooter('');
        CDL.DSC.OAC.mapns.contentPanel.setBody('<img src="'+ image_src+ '" width="100%" height="100%"/>');
        CDL.DSC.OAC.mapns.imgInPanel = new Image();
        CDL.DSC.OAC.mapns.imgInPanel.onload = CDL.DSC.OAC.mapns.panelImageLoaded ;
        CDL.DSC.OAC.mapns.imgInPanel.src = image_src;
    },

    make_ark_object_label: function (ark, arkobject) {
            label = '<div id="infoballoon" class="balloon">';
            //if thumbnail too big, resize
            h_max = w_max = 250;
            if (arkobject.thumbnail.width > w_max || arkobject.thumbnail.height > h_max) {
                img_size = CDL.DSC.OAC.mapns.calcShrink(arkobject.thumbnail.height, arkobject.thumbnail.width, h_max, w_max);
                h_img = img_size.height;
                w_img = img_size.width;
            } else {
                h_img = arkobject.thumbnail.height;
                w_img = arkobject.thumbnail.width;
            }
            label = label + '<img src="' + arkobject.thumbnail.src + '" width="' + w_img + 'px" height="' + h_img + 'px" onClick="mapns.openContentPanel(\'' + ark + '\',\''+ arkobject.image.src + '\');return false;" onmouseover="this.style.cursor=\'pointer\';"</img>';
            label = label +  '<h1>Title:</h1><p>' + arkobject.title + '</p>';
            if (arkobject.date) {
                label = label + '<h2>Date:</h2><p>'+ arkobject.date + '</p>';
            }
            label = label + '<p><a href="http://content.cdlib.org/' + ark + '" target="_blank">Go to image page</a></p>';
            if (!arkobject.exact) {
                label = label + '<p>Location is approximate.<a target="_blank" href="/themed_collections/pdf/how_we_mapped.pdf">(Learn more)</a></p>';
            }
            //TODO: Is there a street view available?
            label = label + '<p><a href="" onclick="mapns.show_streetview('+ arkobject.lat + ', ' + arkobject.lon + ', \'' + ark + '\', \'streetview_' + ark + '\'); return false;">Current street view of location</a></p>';
            label = label + "</div>";
            return label;
    },
    
    markerSize : function(zoom) {
        //return size of marker for zoom.
        var size = 18;
        //size it according to zoom
        //probably want a map?
        if ( zoom > 6 ) {
            switch (zoom) {
                case 7:
                    size = 24;
                    break;
                case 8:
                    size = 30;
                    break;
                case 9:
                    size = 34;
                    break;
                case 10:
                    size = 38;
                    break;
                case 11:
                    size = 42;
                    break;
                case 12:
                    size = 46;
                    break;
                case 13:
                    size = 50;
                    break;
                case 14:
                    size = 56;
                    break;
                case 15:
                    size = 60;
                    break;
                case 16:
                    size = 66;
                    break;
                case 17:
                    size = 68;
                    break;
                default: //zoomed in
                    size = 70
            }
        }
        return size;
    },

    createImageMarker : function(point, ark, arkobj, label, zoom, infoWinOpen, selected) {
        icon = new GIcon(G_DEFAULT_ICON);
        icon.image = "http://www.google.com/mapfiles/ms/micons/blue.png";
        icon.shadow = "";
        icon.image = arkobj.thumbnail.src;
        var size = CDL.DSC.OAC.mapns.markerSize(window.map.getZoom());
        icon.iconSize = new GSize(size, size);
        icon.iconAnchor = new GPoint(Math.floor(size/2), size-1);
        icon.imageMap = [0,0, (size-1),0, (size-1),(size-1), 0,(size-1)];
        icon.infoWindowAnchor = new GPoint(Math.floor(size/2), 2);
        if (selected) {
            zIndex = function (marker, b) {
                return 9999;
            };
            var marker = new GMarker(point, {draggable:false, icon : icon, zIndexProcess:zIndex});
        } else {
            var marker = new GMarker(point, {draggable:false, icon : icon});
        }
        marker.ark = ark; //DUP of parent info, but needed for event listener
        marker.label = label;
        marker.zoom = zoom;
        marker.infoWinOpen = infoWinOpen;
        marker.selected = selected;
      
      GEvent.addListener(marker, "click", function() {
              //as were clicked, want to change zindex. need to mod
            var marker_new = CDL.DSC.OAC.mapns.createImageMarker(this.getLatLng(), this.ark, CDL.DSC.OAC.mapns.arkobjects[this.ark], this.label, window.map.getZoom(), true, true);
            for (var ark in CDL.DSC.OAC.mapns.arkobjects) {
                if (CDL.DSC.OAC.mapns.arkobjects[ark].marker instanceof GMarker) { 
                  //deselect others
                  CDL.DSC.OAC.mapns.arkobjects[ark].marker.selected = false;
                }
            }
            CDL.DSC.OAC.mapns.arkobjects[this.ark].marker = marker_new;
            window.map.addOverlay(marker_new);
            marker_new.openInfoWindowHtml(marker_new.label);
            window.map.removeOverlay(this);
        });
      GEvent.addListener(marker, "infowindowopen", function() {
            this.infoWinOpen = true;
        });
      GEvent.addListener(marker, "infowindowclose", function() {
            this.infoWinOpen = false;
        });
      return marker;
    },
    
    showMap: function (ark) {
        CDL.DSC.OAC.mapns.mapPanel.show();
        if (typeof ark === 'string' && ark.indexOf('ark:') > -1) {
        //if (ark) {
            //NOTE: the event listener doesn't seem to work
            // is it already loaded?
            //GEvent.addListener(window.map, "load", function () {
            //    marker = CDL.DSC.OAC.mapns.arkobjects[ark].marker;
            //    marker.openInfoWindowHtml(marker.label);
            //});
            if (window.map.isLoaded()) {
                marker = CDL.DSC.OAC.mapns.arkobjects[ark].marker;
                GEvent.trigger(marker, 'click');
                window.map.setCenter(marker.getLatLng(), 8);
            }
        }
        else {
            window.map.setCenter(CDL.DSC.OAC.mapns.marker_bounds.getCenter(), map.getBoundsZoomLevel(CDL.DSC.OAC.mapns.marker_bounds));
            window.map.closeInfoWindow();
        }
        return false;
    },
    
    load: function (centerLat, centerLon ) {
        if (GBrowserIsCompatible() ) {
            var AjaxObject = {
                handleSuccess:function(o) {
                    // This member handles the success response
                    // and passes the response object o to AjaxObject's
                    // processResult member.
                    this.processResult(o);
                },
                
                handleFailure:function(o) {
                    // Failure handler
                    document.getElementById("showMap").disabled=true;
                },
                
                processResult:function(o) {
                    // This member is called by handleSuccess
                    CDL.DSC.OAC.mapns.arkobjects = eval('(' + o.responseText + ')');
                    window.map = new GMap2(document.getElementById("map_canvas"),size=GSize(300,300) );
                    window.map.addControl(new GLargeMapControl());
                    window.map.addControl(new GMapTypeControl());
                    //window.map.setMapType(G_HYBRID_MAP);
            
                    var zoomLevel = 6;
            
                    window.map.setCenter(new GLatLng(o.argument[0], o.argument[1]), zoomLevel);
                    for (var ark_x in CDL.DSC.OAC.mapns.arkobjects) {
                        if (typeof CDL.DSC.OAC.mapns.arkobjects[ark_x] !== 'function') { 
                        arkobject = CDL.DSC.OAC.mapns.arkobjects[ark_x];
                        label = CDL.DSC.OAC.mapns.make_ark_object_label(ark_x, arkobject);
                        if (arkobject.lat) {
                            var point = new GLatLng(arkobject.lat, 
                                                    arkobject.lon);
                
                            i = new Image();
                            i.src = arkobject.thumbnail.src;

                            CDL.DSC.OAC.mapns.marker_bounds.extend(point);
                            var marker = CDL.DSC.OAC.mapns.createImageMarker(point, ark_x, arkobject, label, window.map.getZoom(), false, false);
                            window.map.addOverlay(marker);
                            CDL.DSC.OAC.mapns.arkobjects[ark_x].marker = marker;
                        }
                    }
                  }
                CDL.DSC.OAC.mapns.linkarkstomap();
                GEvent.addListener(map, "zoomend", CDL.DSC.OAC.mapns.handleZoomEnd);
                GEvent.addListener(map, "moveend", CDL.DSC.OAC.mapns.handleMoveEnd);
                map.setCenter(CDL.DSC.OAC.mapns.marker_bounds.getCenter(), map.getBoundsZoomLevel(CDL.DSC.OAC.mapns.marker_bounds));
                document.getElementById("showMap").disabled=false;
                document.getElementById("showMap_img").src="/images/themed_collections/view_map_icon.gif";
                document.getElementById("view_all_images_btn").disabled=false;
                document.getElementById("view_all_images_img").src="/images/themed_collections/view_all_images_btn.gif";
                YAHOO.util.Event.addListener("showMap", "click", CDL.DSC.OAC.mapns.showMap);
                },
                
                startRequest:function() {
                   //alert('get json->'+window.location+'/json/');
                   var url_json = window.location.toString();
                   YAHOO.util.Connect.asyncRequest('GET', url_json.replace(/\/$/,'')+'/json/', callback, null);
                }
            };
            
            var callback = {
                success:AjaxObject.handleSuccess,
                failure:AjaxObject.handleFailure,
                argument:[ centerLat, centerLon ],
                scope: AjaxObject
            };
            
            //disable the map button until ready
            document.getElementById("showMap").disabled=true;
            document.getElementById("view_all_images_btn").disabled=true;
            // Start the transaction.
            AjaxObject.startRequest();
        }
    },
    
    init: function () {
        //DO nifty here, minimizes delay of rounding
        if(NiftyCheck()) {
            Rounded("div.nifty1","all","transparent","#FFF","border #83A3A3");
            Rounded("div.nifty2","all","transparent","#F2F8F8","border #9EB8B8");
            Rounded("div.nifty3","all","transparent","#FFF","border #FCAFA0");
            Rounded("div.nifty4","all","transparent","#E9E9E9","border #CDCDCD");
            Rounded("div.nifty5","all","transparent","#FEF4E0","border #FCAFA0");
            Rounded("div.nifty6","all","transparent","#FFF","border #DBD9D5");
            Rounded("div.nifty7","all","transparent","#FFF","border #A6A39C");
            Rounded("div.nifty8","all","transparent","#83a3a3","border #83a3a3");
            Rounded("div.nifty9","all","transparent","#fff","border #fff");
            window.NiftyCheck = function() { return false;};
        }

        panelWidth = Math.floor(YAHOO.util.Dom.getViewportWidth()*.9);
        panelHeight = Math.floor(YAHOO.util.Dom.getViewportHeight()*.9);
        CDL.DSC.OAC.mapns.mapPanel = new YAHOO.widget.Panel("mapPanel", {
            width: panelWidth+ 'px',
            height: panelHeight + 'px',
            fixedcenter: true, 
            constraintoviewport: true, 
            underlay: "shadow", 
            close: true, 
            visible: false, 
            //draggable: true,
            modal: true
        });
 
        //Handle click off map panel as a close event
        YAHOO.util.Event.addListener(document, "click", function(e) {
                        var el = YAHOO.util.Event.getTarget(e);
                        var maskEl = CDL.DSC.OAC.mapns.mapPanel.mask;

                        if (el === maskEl ) { //&& !YAHOO.util.Dom.isAncestor(maskEl, el) ) {
                            CDL.DSC.OAC.mapns.mapPanel.hide();
                        }
        });
        CDL.DSC.OAC.mapns.mapPanel.render();
        CDL.DSC.OAC.mapns.load(37.8086906,-122.267541);
    }


    };//namespace return wrapper
}();

YAHOO.util.Event.onDOMReady(CDL.DSC.OAC.mapns.init);
var mapns = CDL.DSC.OAC.mapns;
