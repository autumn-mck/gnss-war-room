import * as THREE from "three";
import type { GeoJSON, Position } from "geojson";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial, type LineMaterialParameters } from "three/addons/lines/LineMaterial.js";

export function drawGeoJSON(
	json: GeoJSON,
	sphereRadius: number,
	lineOptions: LineMaterialParameters,
	container: THREE.Object3D
) {
	const geometries = geojsonToGeometries(json);
	for (let geometry of geometries) {
		if (geometry.type == "MultiLineString") {
			drawCoordinatesAsLines(container, geometry.coordinates, sphereRadius, lineOptions);
		} else if (geometry.type == "MultiPolygon") {
			for (let polygon of geometry.coordinates) {
				drawCoordinatesAsLines(container, polygon, sphereRadius, lineOptions);
			}
		}
	}
}

function drawCoordinatesAsLines(
	container: THREE.Object3D,
	coordinates: Position[][],
	sphereRadius: number,
	lineOptions: LineMaterialParameters
) {
	for (let coordinate of coordinates) {
		const xyzVals: number[] = [];

		for (let point of coordinate) {
			xyzVals.push(...latLongToXyz(point, sphereRadius));
		}

		const line = drawLine(xyzVals, lineOptions);
		container.add(line);
	}
}

function drawLine(xyzVals: number[], lineOptions: LineMaterialParameters) {
	const lineGeo = new LineGeometry();
	lineGeo.setPositions(xyzVals);

	const lineMaterial = new LineMaterial(lineOptions);

	const line = new Line2(lineGeo, lineMaterial);
	line.computeLineDistances();

	return line;
}

function geojsonToGeometries(json: GeoJSON) {
	if (json.type == "FeatureCollection") {
		return json.features.map((feature) => feature.geometry);
	} else if (json.type == "GeometryCollection") {
		return json.geometries;
	} else {
		throw new Error("Invalid or unsupported GeoJSON");
	}
}

export function latLongToXyz(latLong: number[], sphereRadius: number) {
	const lon = (latLong[0] * Math.PI) / 180;
	const lat = (latLong[1] * Math.PI) / 180;
	return [
		Math.cos(lat) * Math.cos(lon) * sphereRadius,
		Math.cos(lat) * Math.sin(lon) * sphereRadius,
		Math.sin(lat) * sphereRadius,
	];
}
