#This will bundle up the map_themed_collection.js with other 
#required files.
# run from the djsite dir
java -jar util/yuicompressor-2.4.2.jar -o site_media/js/map_themed_collection-min.js site_media/js/map_themed_collection.js 
cat site_media/js/yahoo*js site_media/js/connection_core-min.js site_media/js/container-min.js site_media/js/map_themed_collection-min.js > site_media/js/map_themed_collection-all-min.js
