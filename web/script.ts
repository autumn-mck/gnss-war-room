import * as THREE from "three";
import { latLongToXyz } from "./threeGeoJSON.ts";
import { SatelliteDisplay } from "./satelliteDisplay.ts";
import { createCamera, createControls, createEarth } from "./init.ts";
import {
	genSatelliteTrail,
	genGroundLine,
	resizeCanvasToDisplaySize,
	genSatelliteSelector,
	genSatellite,
} from "./renderUtils.ts";
import { type Satellite } from "./satellite.ts";
import { type GnssData } from "./gnssData.ts";

const svgContainer = document.getElementById("svgContainer") as HTMLDivElement;
const comboBox = document.getElementById("toDisplay") as HTMLSelectElement;
const canvas = document.getElementById("canvas") as HTMLCanvasElement;
const canvasContainer = document.getElementById("canvasContainer") as HTMLDivElement;
const satelliteDisplay = document.getElementById("satelliteDisplay") as SatelliteDisplay;

// hide combo box when embedded
if (window.navigator.userAgent == "WOPR") comboBox.style.display = "none";

const palette = await fetch("/palette.json").then((res) => res.json());

document.documentElement.style.setProperty("--background", palette.background);
document.documentElement.style.setProperty("--foreground", palette.foreground);

let selectedSatellite: Satellite | undefined = undefined;
let latestGnssData: GnssData | undefined = undefined;

const renderer = new THREE.WebGLRenderer({ antialias: true, canvas });
renderer.setClearColor(palette.background);
renderer.setPixelRatio(window.devicePixelRatio);

const camera = createCamera();
const controls = createControls(camera, canvas);

const onClickRaycaster = new THREE.Raycaster();
let mouseDownEvent: MouseEvent | undefined = undefined;

const scene = new THREE.Scene();
createEarth(scene, palette);

let satellitesObject = new THREE.Object3D();
scene.add(satellitesObject);

renderer.render(scene, camera);

let shouldRotate = true;
let lastTimestamp = 0;
function render(timestamp: DOMHighResTimeStamp) {
	controls.update();
	renderer.render(scene, camera);
	requestAnimationFrame(render);

	const timeMs = timestamp - lastTimestamp;
	lastTimestamp = timestamp;
	if (shouldRotate) scene.rotation.y += (-0.12 * timeMs) / 1000;
}
requestAnimationFrame(render);

function mouseDown(event: MouseEvent) {
	mouseDownEvent = event;
}

function mouseUp(event: MouseEvent) {
	if (!mouseDownEvent) return;

	// calc distance between mouse down and up
	const dx = mouseDownEvent.clientX - event.clientX;
	const dy = mouseDownEvent.clientY - event.clientY;
	const dist = Math.sqrt(dx * dx + dy * dy);
	const mouseThreshold = 3;

	// normalised pointer position (-1 to +1)
	const pointer = new THREE.Vector2(
		(event.clientX / window.innerWidth) * 2 - 1,
		-(event.clientY / window.innerHeight) * 2 + 1
	);

	onClickRaycaster.setFromCamera(pointer, camera);

	// calculate objects intersecting the picking ray
	const intersects = onClickRaycaster.intersectObjects(scene.children);

	if (intersects.length == 0 && dist < mouseThreshold) {
		selectedSatellite = undefined;
	}

	if (dist > mouseThreshold) return;

	for (let i = 0; i < intersects.length; i++) {
		let obj = intersects[i].object;
		if (obj.type !== "Mesh" || obj.geometry.type !== "IcosahedronGeometry") continue;
		selectedSatellite = obj.userData as Satellite;
		obj.material.color.set(0xff0000);
		obj.material.opacity = 1;
		break;
	}
	satelliteDisplay.update(selectedSatellite, latestGnssData);

	if (selectedSatellite) {
		let [x, y, z] = latLongToXyz(
			[selectedSatellite.long, selectedSatellite.lat],
			selectedSatellite.altitude / 6.371
		);
		satellitesObject.add(genGroundLine(x, y, z, selectedSatellite));
	}
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

	let gnssData = (await fetch("/api/gnss").then((res) => res.json())) as GnssData;
	latestGnssData = gnssData;
	selectedSatellite = findUpdatedSelectedSatellite(gnssData, selectedSatellite);
	satelliteDisplay.update(selectedSatellite, latestGnssData);
	satellitesObject.clear();

	const currentTime = Date.parse(gnssData.date);
	for (let satellite of gnssData.satellites) {
		let [x, y, z] = latLongToXyz([satellite.long, satellite.lat], satellite.altitude / 6.371);
		satellitesObject.add(genSatellite(x, y, z, satellite));
		satellitesObject.add(genSatelliteSelector(x, y, z, satellite));
		satellitesObject.add(...genSatelliteTrail(satellite, currentTime));

		if (
			satellite.prnNumber === selectedSatellite?.prnNumber &&
			satellite.network === selectedSatellite?.network
		) {
			satellitesObject.add(genGroundLine(x, y, z, satellite));
		}
	}
}

function findUpdatedSelectedSatellite(
	gnssData: GnssData,
	selectedSatellite: Satellite | undefined
) {
	if (selectedSatellite === undefined) return undefined;
	return gnssData.satellites.find(
		(satellite) =>
			selectedSatellite.prnNumber === satellite.prnNumber &&
			selectedSatellite.network === satellite.network
	);
}

update();
setInterval(async () => update(), 1000);
comboBox.addEventListener("change", async () => update());

resizeCanvasToDisplaySize(canvas, renderer, camera);
window.addEventListener("resize", () => resizeCanvasToDisplaySize(canvas, renderer, camera));
window.addEventListener("mousedown", mouseDown);
window.addEventListener("mouseup", mouseUp);
window.addEventListener("keydown", (event) => {
	if (event.key === "r") shouldRotate = !shouldRotate;
});

if (!customElements.get("satellite-display"))
	customElements.define("satellite-display", SatelliteDisplay);
