// var map = L.map('map').setView([39.904202, 115.83023], 4);
var map_markers = [];
var pointIcon = L.divIcon({
    iconSize: [10, 10],
    iconAnchor: [10, 10],
    popupAnchor: [-5, -11],
    shadowSize: [0, 0],
    className: 'point-icon',
    html: ''
});
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data © OpenStreetMap contributors',
    maxZoom: 15
}).addTo(map);
for (i = 0; i < map_marker_data.length; i++) {
    marker = L.marker(map_marker_data[i].latlng, {
        icon: pointIcon,
        title: map_marker_data[i].title
    }).addTo(map);
    marker.bindPopup(map_marker_data[i].popup).on('click', mapClickZoom);
    map_markers.push(marker);
}
$('a.map-item').click(function() {
    mapMarkerFunction($(this)[0].id);
});

function mapClickZoom(e) {
    map.setView(e.target.getLatLng(), 9);
}

function mapMarkerFunction(id) {
    for (var i in map_markers) {
        var markerID = map_markers[i].options.title;
        var position = map_markers[i].getLatLng();
        if (markerID == id) {
            map.setView(position);
            map_markers[i].openPopup();
        }
    }
}
