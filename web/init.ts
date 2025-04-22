import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/Addons.js";
import { type LineMaterialParameters } from "three/addons/lines/LineMaterial.js";
import { type Palette } from "./palette.ts";
import { drawGeoJSON } from "./geoJSON.ts";

export function createCamera() {
	const fov = 30;
	const aspect = 2;
	const near = 0.01;
	const far = 50;
	const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
	camera.position.x = 14;
	camera.position.y = 5;

	return camera;
}

export function createControls(camera: THREE.Camera, canvas: HTMLCanvasElement) {
	const controls = new OrbitControls(camera, canvas);
	controls.enableDamping = true;
	controls.dampingFactor = 0.1;
	controls.minDistance = 1.1;
	controls.maxDistance = 40;
	controls.update();

	return controls;
}

export function createEarth(scene: THREE.Scene, palette: Palette) {
	const baseSphereGeometry = new THREE.SphereGeometry(0.99);
	const baseSphereMaterial = new THREE.MeshBasicMaterial({ color: palette.background });
	const baseSphere = new THREE.Mesh(baseSphereGeometry, baseSphereMaterial);
	scene.add(baseSphere);

	const geojsonContainer = new THREE.Object3D();
	geojsonContainer.rotateX((-90 * Math.PI) / 180);
	scene.add(geojsonContainer);

	loadGeojson("/continents.geojson", geojsonContainer, { color: palette.continentsBorder });
	// loadGeojson("/borders.geojson", geojsonContainer, { color: palette.admin0Border });
}

async function loadGeojson(
	from: string,
	to: THREE.Object3D,
	materialOptions: LineMaterialParameters
) {
	const response = await fetch(from);
	const json = await response.json();
	drawGeoJSON(json, 1, materialOptions, to);
}
