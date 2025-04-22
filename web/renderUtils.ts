import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { latLongToXyz } from "./geoJSON.ts";
import { type Satellite } from "./satellite.ts";

export function genSatelliteTrail(satellite: Satellite, currentTime: number) {
	const prevPosPoints: number[][] = [];
	const lines: Line2[] = [];

	for (let index = 0; index < satellite.previousPositions.length; index++) {
		let position = satellite.previousPositions[index];
		const measureTime = Date.parse(position[0] as string);
		const timeSinceMeasurementHours = (currentTime - measureTime) / 1000 / 60 / 60;

		let latLong = position[1] as [number, number];
		let [x, y, z] = latLongToXyz([latLong[1], latLong[0]], satellite.altitude / 6.371);
		y = -y;

		let fadeStartTime = 0;
		let fadeEndTime = 1.2;
		let opacity = 1 - (timeSinceMeasurementHours - fadeStartTime) / (fadeEndTime - fadeStartTime);
		opacity = Math.max(0, opacity);
		opacity = Math.min(1, opacity);

		if (index > 0 && opacity > 0) {
			let prevPos = prevPosPoints[index - 1];
			let lineGeom = new LineGeometry();
			lineGeom.setPositions([x, z, y].concat(prevPos));
			let lineMaterial = getTrailMaterial(satellite);
			lineMaterial.opacity = opacity;
			let line = new Line2(lineGeom, lineMaterial);
			line.computeLineDistances();
			lines.push(line);
		}

		prevPosPoints.push([x, z, y]);
	}

	return lines;
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
	const baseSelectGeometry = new THREE.IcosahedronGeometry(0.12, 0);
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
