import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { latLongToXyz } from "./threeGeoJSON.ts";
import { type Satellite } from "./satellite.ts";

export function genSatelliteTrail(satellite: Satellite) {
	const prevPosPoints = [];
	for (let prevPosition of satellite.previousPositions) {
		let [x, y, z] = latLongToXyz([prevPosition[1], prevPosition[0]], satellite.altitude / 6.371);
		prevPosPoints.push(x, z, y);
	}

	const prevPosGeometry = new LineGeometry();
	prevPosGeometry.setPositions(prevPosPoints);
	const lineMaterial = getTrailMaterial(satellite);
	const prevPosLine = new Line2(prevPosGeometry, lineMaterial);
	prevPosLine.computeLineDistances();
	return prevPosLine;
}

export function genGroundLine(x: number, y: number, z: number, satellite: Satellite) {
	const groundTrailPoints = [0, 0, 0, x, z, y];
	const groundLineGeom = new LineGeometry();
	groundLineGeom.setPositions(groundTrailPoints);
	const lineMaterial = getGroundLineMaterial(satellite);
	const groundLine = new Line2(groundLineGeom, lineMaterial);
	groundLine.computeLineDistances();
	return groundLine;
}

export function resizeCanvasToDisplaySize(
	canvas: HTMLCanvasElement,
	renderer: THREE.WebGLRenderer,
	camera: THREE.PerspectiveCamera
) {
	const visualWidth = canvas.clientWidth;
	const visualHeight = canvas.clientHeight;

	if (canvas.width !== visualWidth || canvas.height !== visualHeight) {
		renderer.setSize(visualWidth, visualHeight, false);
		camera.aspect = visualWidth / visualHeight;
		camera.updateProjectionMatrix();
	}
}

function getTrailMaterial(satellite: Satellite) {
	return new LineMaterial({
		color: satellite.colour,
		linewidth: 2,
		alphaToCoverage: true,
	});
}

function getGroundLineMaterial(satellite: Satellite) {
	return new LineMaterial({
		color: satellite.colour,
		linewidth: 1,
		alphaToCoverage: true,
		dashed: true,
		dashSize: 0.1,
		gapSize: 0.1,
	});
}

export function genSatelliteSelector(x: number, y: number, z: number, satellite: Satellite) {
	const baseSelectGeometry = new THREE.IcosahedronGeometry(0.15, 0);
	const baseSelectMaterial = new THREE.MeshBasicMaterial({
		color: 0x000000,
		transparent: true,
		opacity: 0,
	});

	const satSelect = new THREE.Mesh(baseSelectGeometry, baseSelectMaterial);
	satSelect.translateX(x);
	satSelect.translateY(z);
	satSelect.translateZ(y);
	satSelect.userData = satellite;
	return satSelect;
}

export function genSatellite(x: number, y: number, z: number, satellite: Satellite) {
	const satGeometry = new THREE.IcosahedronGeometry(0.06, 1);
	const satMaterial = new THREE.MeshBasicMaterial({ color: satellite.colour });
	let satMesh = new THREE.Mesh(satGeometry, satMaterial);
	satMesh.translateX(x);
	satMesh.translateY(z);
	satMesh.translateZ(y);
	satMesh.userData = satellite;

	return satMesh;
}
