import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/Addons.js";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineMaterial, type LineMaterialParameters } from "three/addons/lines/LineMaterial.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { drawThreeGeo, latLongToXyz } from "./threeGeoJSON.ts";
import { SatelliteDisplay } from "./satelliteDisplay.ts";

const svgContainer = document.getElementById("svgContainer") as HTMLDivElement;
const comboBox = document.getElementById("toDisplay") as HTMLSelectElement;
const canvas = document.getElementById("canvas") as HTMLCanvasElement;
const canvasContainer = document.getElementById("canvasContainer") as HTMLDivElement;
const satelliteDisplay = document.getElementById("satelliteDisplay") as SatelliteDisplay;

let selectedSatellite: any = null;
let latestGnssData: any = null;

const renderer = new THREE.WebGLRenderer({ antialias: true, canvas });
renderer.setPixelRatio(window.devicePixelRatio);

const camera = createCamera();
const controls = createControls(camera, canvas);

const raycaster = new THREE.Raycaster();

const scene = new THREE.Scene();
createEarth(scene);

let satellitesObject = new THREE.Object3D();
scene.add(satellitesObject);
const satGeometry = new THREE.IcosahedronGeometry(0.06, 1);

renderer.render(scene, camera);

function resizeCanvasToDisplaySize() {
	const visualWidth = canvas.clientWidth;
	const visualHeight = canvas.clientHeight;

	if (canvas.width !== visualWidth || canvas.height !== visualHeight) {
		renderer.setSize(visualWidth, visualHeight, false);
		camera.aspect = visualWidth / visualHeight;
		camera.updateProjectionMatrix();
	}
}

function render(timeMs: number) {
	controls.update();
	renderer.render(scene, camera);
	requestAnimationFrame(render);
}
requestAnimationFrame(render);

function onclick(event: MouseEvent) {
	// normalised pointer position (-1 to +1)
	const pointer = new THREE.Vector2(
		(event.clientX / window.innerWidth) * 2 - 1,
		-(event.clientY / window.innerHeight) * 2 + 1
	);

	raycaster.setFromCamera(pointer, camera);

	// calculate objects intersecting the picking ray
	const intersects = raycaster.intersectObjects(scene.children);

	if (intersects.length == 0) {
		selectedSatellite = undefined;
	}

	for (let i = 0; i < intersects.length; i++) {
		let obj = intersects[i].object;
		if (obj.type !== "Mesh" || obj.geometry.type !== "IcosahedronGeometry") continue;
		selectedSatellite = obj.userData;
		obj.material.color.set(0xff0000);
		obj.material.opacity = 1;
	}
	satelliteDisplay.update(selectedSatellite, latestGnssData);
}

async function update() {
	const toFetch = comboBox.value;
	if (toFetch === "globe") {
		updateGlobe();
	} else {
		updateSvg();
	}
}

async function updateSvg() {
	canvasContainer.style.display = "none";
	satelliteDisplay.style.display = "none";
	svgContainer.style.display = "block";

	const toFetch = comboBox.value;
	const response = await fetch(`/${toFetch}`);
	const svg = await response.text();
	svgContainer.innerHTML = svg;
}

async function updateGlobe() {
	svgContainer.innerHTML = "";
	canvasContainer.style.display = "block";
	satelliteDisplay.style.display = "block";
	svgContainer.style.display = "none";

	let gnssData = await fetch("/api/gnss").then((res) => res.json());
	latestGnssData = gnssData;
	// TODO update selected satellite
	satelliteDisplay.update(selectedSatellite, latestGnssData);
	satellitesObject.clear();

	for (let satellite of gnssData.satellites) {
		const satMaterial = new THREE.MeshBasicMaterial({ color: satellite.colour });
		let satMesh = new THREE.Mesh(satGeometry, satMaterial);
		let [x, y, z] = latLongToXyz([satellite.long, satellite.lat], satellite.altitude / 6.371);
		satMesh.translateX(x);
		satMesh.translateY(z);
		satMesh.translateZ(y);
		satMesh.userData = satellite;

		const baseSelectGeometry = new THREE.IcosahedronGeometry(0.15, 0);
		const baseSelectMaterial = new THREE.MeshBasicMaterial({
			color: 0x000000,
			transparent: true,
			opacity: 0,
		});

		let satSelect = new THREE.Mesh(baseSelectGeometry, baseSelectMaterial);
		satSelect.translateX(x);
		satSelect.translateY(z);
		satSelect.translateZ(y);
		satSelect.userData = satellite;
		satellitesObject.add(satSelect);

		const trailMaterial = new LineMaterial({
			color: satellite.colour,
			linewidth: 2,
			alphaToCoverage: true,
		});

		const groundLineMaterial = new LineMaterial({
			color: satellite.colour,
			linewidth: 1,
			alphaToCoverage: true,
			dashed: true,
			dashSize: 0.1,
			gapSize: 0.1,
		});

		drawGroundLine(x, y, z, groundLineMaterial);
		drawSatelliteTrail(satellite, trailMaterial);

		satellitesObject.add(satMesh);
	}
}

function drawSatelliteTrail(satellite: any, lineMaterial: LineMaterial) {
	const prevPosPoints = [];
	for (let prevPosition of satellite.previousPositions) {
		let [x, y, z] = latLongToXyz([prevPosition[1], prevPosition[0]], satellite.altitude / 6.371);
		prevPosPoints.push(x, z, y);
	}

	const prevPosGeometry = new LineGeometry();
	prevPosGeometry.setPositions(prevPosPoints);
	const prevPosLine = new Line2(prevPosGeometry, lineMaterial);
	prevPosLine.computeLineDistances();
	satellitesObject.add(prevPosLine);
}

function drawGroundLine(x: number, y: number, z: number, lineMaterial: LineMaterial) {
	const groundTrailPoints = [0, 0, 0, x, z, y];
	const groundLineGeom = new LineGeometry();
	groundLineGeom.setPositions(groundTrailPoints);
	const groundLine = new Line2(groundLineGeom, lineMaterial);
	groundLine.computeLineDistances();
	satellitesObject.add(groundLine);
}

function createCamera() {
	const fov = 30;
	const aspect = 2;
	const near = 0.01;
	const far = 50;
	const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
	camera.position.x = 14;
	camera.position.y = 5;

	return camera;
}

function createControls(camera: THREE.Camera, canvas: HTMLCanvasElement) {
	const controls = new OrbitControls(camera, canvas);
	controls.enableDamping = true;
	controls.dampingFactor = 0.1;
	controls.minDistance = 1.1;
	controls.maxDistance = 40;
	controls.update();

	return controls;
}

// function generateGroundLine(lineMaterial, )

update();
setInterval(async () => update(), 1000);
comboBox.addEventListener("change", async () => update());

resizeCanvasToDisplaySize();
window.addEventListener("resize", resizeCanvasToDisplaySize);
window.addEventListener("click", onclick);

if (!customElements.get("satellite-display"))
	customElements.define("satellite-display", SatelliteDisplay);

function createEarth(scene: THREE.Scene) {
	const baseSphereGeometry = new THREE.SphereGeometry(0.99);
	const baseSphereMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
	const baseSphere = new THREE.Mesh(baseSphereGeometry, baseSphereMaterial);
	scene.add(baseSphere);

	const geojsonContainer = new THREE.Object3D();
	geojsonContainer.rotateX((-90 * Math.PI) / 180);
	scene.add(geojsonContainer);

	loadGeojson("/continents.geojson", geojsonContainer, { color: 0x63f68d });
	// loadGeojson("/borders.geojson", geojsonContainer, { color: 0xffffff });
}

async function loadGeojson(
	from: string,
	to: THREE.Object3D,
	materialOptions: LineMaterialParameters
) {
	const response = await fetch(from);
	const json = await response.json();
	drawThreeGeo(json, 1, materialOptions, to);
}
