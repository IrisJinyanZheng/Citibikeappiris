function truckLayers(map, mapboxgl, url2, icon1, icon2) {
	//	var url = 'http://ec2-54-196-202-203.compute-1.amazonaws.com/vehiclegeojson'

	window.setInterval(function() {
		map.getSource('vehicles').setData(url2);
	}, 60000); // update every minute

	map.addSource('vehicles', {
		type: 'geojson',
		data: url2
	});
	

	map.addLayer({
		"id": "vehicles",
		"type": "symbol",
		"source": "vehicles",
		"layout": {
			"icon-image": icon1
		}
	});
	
		map.addLayer({
		"id": "vehiclesClick",
		"type": "symbol",
		"source": "vehicles",
		"layout": {
			"icon-image": icon2
		}
		,"filter": ["==", "vID", " "]
	});
//	

	



	var popup = new mapboxgl.Popup({
		closeButton: false,
		closeOnClick: false
	});

	var layerID = ['vehicles', "vehiclesClick"]

	//show popup when hover
	for(l in layerID) {
		map.on('mouseenter', layerID[l], function(e) {
			// Change the cursor style as a UI indicator.
			map.getCanvas().style.cursor = 'pointer';

			// Populate the popup and set its coordinates
			// based on the feature found.
			feature = e.features[0]
			popup.setLngLat(e.features[0].geometry.coordinates)
				.setHTML('<b> ' + feature.properties.vID + '</b> <small>&nbsp' + feature.properties.dID1 + " " + feature.properties.dID2 + "</small>" +
					"<br /> Capacity: " + feature.properties.capacity +
					"<br /> Bike on vehicle: " + feature.properties.vBike +
					"<br /> Next Station: " + feature.properties.vNXsID +
					"<br /> Current Task ID: " + feature.properties.tID)
				.addTo(map);
		});

//		map.on('mouseleave', layerID[l], function() {
//			map.getCanvas().style.cursor = '';
//			popup.remove();
//		});

	}
	map.on('mouseleave', "vehicles", function() {
			map.getCanvas().style.cursor = '';
			popup.remove();
		});
}

function taskLayer(map, mapboxgl, url3) {
	window.setInterval(function() {
		map.getSource('tasks').setData(url3);
	}, 60000); // update every min

	map.addSource('tasks', {
		type: 'geojson',
		data: url3
	});

	map.addLayer({
		"id": "tasks",
		"type": "line",
		"source": "tasks",
		"layout": {
			"line-join": "round",
			"line-cap": "round"
		},
		"paint": {
			"line-color": "#888",
			"line-width": 3
		},
		"filter": ["==", "vID", ""]
	});

	map.addLayer({
		"id": "tasksClick",
		"type": "line",
		"source": "tasks",
		"layout": {
			"line-join": "round",
			"line-cap": "round"
		},
		"paint": {
			"line-color": "#888",
			"line-width": 3
		},
		"filter": ["==", "vID", ""]
	});

	//Click & remove popup & task
	map.on('click', 'vehicles', function(e) {
//		console.log()
		map.setFilter("vehiclesClick", ["==", "vID", e.features[0].properties.vID]);
		map.setFilter("tasksClick", ["==", "vID", e.features[0].properties.vID]);
	});

	map.on('click', 'vehiclesClick', function(e) {
		map.setFilter("vehiclesClick", ["==", "vID", ""]);
		map.setFilter("tasksClick", ["==", "vID", ""]);
	});
	
	// hover show task
	map.on('mouseenter', "vehicles", function(e) {
		map.setFilter("tasks", ["==", "vID", e.features[0].properties.vID]);
	});

	map.on('mouseleave', "vehicles", function() {
		map.setFilter("tasks", ["==", "vID", '']);
	});
}

function nystationsLayer(map, mapboxgl, url, icon1, icon2, icon3) {

	window.setInterval(function() {
		map.getSource('nystations').setData(url);
	}, 60000); // update every minute

	map.addSource('nystations', {
		type: 'geojson',
		data: url
	});

	map.addLayer({
		"id": "nystations",
		"type": "symbol",
		"source": "nystations",
		"layout": {
			"icon-image": icon1
		}
	});

	map.addLayer({
		"id": "nystationsOS",
		"type": "symbol",
		"source": "nystations",
		"layout": {
			"icon-image": icon2
		},
		"filter": ["==", "statusKey", 3]
	});

	map.addLayer({
		"id": "nystationsClick",
		"type": "symbol",
		"source": "nystations",
		"layout": {
			"icon-image": icon3
		},
		"filter": ["==", "id", ""]
	});

	// Create a popup, but don't add it to the map yet.
	var popup = new mapboxgl.Popup({
		closeButton: false,
		closeOnClick: false
	});

	var layerID = ['nystations', "nystationsOS", "nystationsClick"]

	//show popup when hover
	for(l in layerID) {
		map.on('mouseenter', layerID[l], function(e) {
			// Change the cursor style as a UI indicator.
			map.getCanvas().style.cursor = 'pointer';

			// Populate the popup and set its coordinates
			// based on the feature found.
			feature = e.features[0]
			popup.setLngLat(e.features[0].geometry.coordinates)
				.setHTML('<b> ' + feature.properties.id + '</b> <small>&nbsp' + feature.properties.stationName + "</small>" +
					"<br /> Available Bikes: " + feature.properties.availableBikes +
					"<br /> Available Docks: " + feature.properties.availableDocks +
					"<br /> Total Docks: " + feature.properties.totalDocks)
				.addTo(map);
		});

	}

	//Click & remove popup 
	for(i = 0; i < 2; i++) {
		map.on('click', layerID[i], function(e) {
			map.setFilter("nystationsClick", ["==", "id", e.features[0].properties.id]);
		});

		map.on('mouseleave', layerID[i], function() {
			map.getCanvas().style.cursor = '';
			popup.remove();
		});

	}

	map.on('click', 'nystationsClick', function(e) {
		map.setFilter("nystationsClick", ["==", "id", ""]);
	});

}

////	//https://cors-anywhere.herokuapp.com/
// <!--<div id='menu'>
//			<input id='basic' type='radio' name='rtoggle' value='basic'>
//			<label for='basic'>basic</label>
//			<input id='streets' type='radio' name='rtoggle' value='streets'>
//			<label for='streets'>streets</label>
//			<input id='bright' type='radio' name='rtoggle' value='bright'>
//			<label for='bright'>bright</label>
//			<input id='light' type='radio' name='rtoggle' value='light'>
//			<label for='light'>light</label>
//			<input id='dark' type='radio' name='rtoggle' value='dark' checked='checked'>
//			<label for='dark'>dark</label>
//			<input id='satellite' type='radio' name='rtoggle' value='satellite'>
//			<label for='satellite'>satellite</label>
//		</div>-->
//
//
///
//<div id='menu'>
//			<input id='basic' type='radio' name='rtoggle' value='basic'>
//			<label for='basic'>basic</label>
//			<input id='streets' type='radio' name='rtoggle' value='streets'>
//			<label for='streets'>streets</label>
//			<input id='bright' type='radio' name='rtoggle' value='bright'>
//			<label for='bright'>bright</label>
//			<input id='light' type='radio' name='rtoggle' value='light'>
//			<label for='light'>light</label>
//			<input id='dark' type='radio' name='rtoggle' value='dark' checked='checked'>
//			<label for='dark'>dark</label>
//			<input id='satellite' type='radio' name='rtoggle' value='satellite'>
//			<label for='satellite'>satellite</label>
//		</div>
//		
//		var layerList = document.getElementById('menu');
//			var inputs = layerList.getElementsByTagName('input');
//
//			function switchLayer(layer) {
//				var s = map.getStyle()
//				var layerId = layer.target.id;
//				map.setStyle('mapbox://styles/mapbox/' + layerId + '-v9');
//				
//			}
//
//			for(var i = 0; i < inputs.length; i++) {
//				inputs[i].onclick = switchLayer;
//			}
//
//		
//		
//	this.map.on('style.load', function () {
//		console.log(1)
//  this.pastInitialLoad = true;
//  this.map.addSource("nystations2", {
//      "type": "geojson",
//      "data": url }
//  );
//  this.map.addLayer({
//      "id": "nystations",
//      "type": "symbol",
//      "source": "nystations2",
//      "interactive": true,
//      "layout": {
//          "icon-image": "bicycle-15"
//      }
//  });
//  
//  if (this.layers) {
//      this.overlayLayer(this.layers);
//  }
//}.bind(this));