import Globe from 'globe.gl';
import * as THREE from 'three';

const map = document.getElementById("map");
const globe = document.getElementById("globe");
const comboBox = document.getElementById("toDisplay");

const earth = createEarth();
const satGeometry = new THREE.IcosahedronGeometry(8, 1);

async function update() {
	const toFetch = comboBox.value;
	if (toFetch === "globe") {
		updateGlobe();
	} else {
		updateSvg();
	}
}

async function updateSvg() {
	const toFetch = comboBox.value;
	globe.style.display = "none";
	map.style.display = "block";

	const response = await fetch(`/${toFetch}`);
	const svg = await response.text();
	map.innerHTML = svg;
}

async function updateGlobe() {
	globe.style.display = "block";
	map.style.display = "none";

	let gnssData = await fetch('/api/gnss').then(res => res.json());

	let satellites = gnssData.satellites.map(satellite => ({
		latitude: satellite.lat + gnssData.latitude,
		longitude: satellite.long + gnssData.longitude,
		altitude: satellite.altitude / 6.371,
		label: `${satellite.network} ${satellite.prnNumber}`,
		colour: satellite.colour,
	}));

	earth.objectsData(satellites);
}

function createEarth() {
	const earth = new Globe(globe, { animateIn: false })
		.globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
		.objectLat("latitude")
		.objectLng("longitude")
		.objectLabel("label")
		.objectAltitude("altitude")
		.objectFacesSurface(false);

	earth.objectThreeObject(satellite => {
		const satMaterial = new THREE.MeshLambertMaterial({ color: satellite.colour });
		return new THREE.Mesh(satGeometry, satMaterial)
	});

	// ideally this shouldn't be hardcoded - ether remove or fix
	setTimeout(() => earth.pointOfView({ altitude: 10, lat: 54, lng: -5 }));

	return earth;
}

update();
setInterval(async () => update(), 1000);
comboBox.addEventListener("change", async () => update());

