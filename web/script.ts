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

let selectedSatellite: Satellite | undefined = undefined;
let latestGnssData: GnssData | undefined = undefined;

const renderer = new THREE.WebGLRenderer({ antialias: true, canvas });
renderer.setPixelRatio(window.devicePixelRatio);

const camera = createCamera();
const controls = createControls(camera, canvas);

const onClickRaycaster = new THREE.Raycaster();

const scene = new THREE.Scene();
createEarth(scene);

let satellitesObject = new THREE.Object3D();
scene.add(satellitesObject);

renderer.render(scene, camera);

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

	onClickRaycaster.setFromCamera(pointer, camera);

	// calculate objects intersecting the picking ray
	const intersects = onClickRaycaster.intersectObjects(scene.children);

	if (intersects.length == 0) {
		selectedSatellite = undefined;
	}

	for (let i = 0; i < intersects.length; i++) {
		let obj = intersects[i].object;
		if (obj.type !== "Mesh" || obj.geometry.type !== "IcosahedronGeometry") continue;
		selectedSatellite = obj.userData as Satellite;
		obj.material.color.set(0xff0000);
		obj.material.opacity = 1;
		break;
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
		let [x, y, z] = latLongToXyz([satellite.long, satellite.lat], satellite.altitude / 6.371);
		satellitesObject.add(genSatellite(x, y, z, satellite));
		satellitesObject.add(genSatelliteSelector(x, y, z, satellite));
		satellitesObject.add(genGroundLine(x, y, z, satellite));
		satellitesObject.add(genSatelliteTrail(satellite));
	}
}

update();
setInterval(async () => update(), 1000);
comboBox.addEventListener("change", async () => update());

resizeCanvasToDisplaySize(canvas, renderer, camera);
window.addEventListener("resize", () => resizeCanvasToDisplaySize(canvas, renderer, camera));
window.addEventListener("click", onclick);

if (!customElements.get("satellite-display"))
	customElements.define("satellite-display", SatelliteDisplay);
