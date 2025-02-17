import { latLongToXyz } from "./threeGeoJSON.ts";

export class SatelliteDisplay extends HTMLElement {
	css = /*css*/ `
pre {
	margin: 0;
	font-size: 2rem;
	background: var(--background);
	border-top: 1px solid var(--foreground);
	border-left: 1px solid var(--foreground);
}
`;

	html = /*html*/ `
<pre id="satelliteInfo"></pre>
`;

	static observedAttributes = ["satelliteNetwork", "satellitePrn", "gnssData"];

	constructor() {
		super();

		const shadow = this.attachShadow({ mode: "open" });
		shadow.innerHTML = this.html;

		const styleSheet = new CSSStyleSheet();
		styleSheet.replaceSync(this.css);

		shadow.adoptedStyleSheets = [styleSheet];
	}

	update(satellite: any, gnssData: any) {
		if (!satellite || !gnssData) {
			this.shadowRoot!.getElementById("satelliteInfo")!.innerText = "";
			return;
		}

		let roundLat = Math.round(satellite.lat * 100000) / 100000;
		let roundLong = Math.round(satellite.long * 100000) / 100000;

		let distToSatellite = this.calcDistanceToSatellite(
			satellite,
			gnssData.latitude,
			gnssData.longitude,
			gnssData.altitude
		);

		this.shadowRoot!.getElementById("satelliteInfo")!.innerText = `PRN: ${satellite.prnNumber}
Orbit height: ${satellite.altitude}km
Dist from receiver: ${distToSatellite}km
Network: ${satellite.network}
Lat: ${roundLat}
Long: ${roundLong}
SNR: ${satellite.snr}
Last update: ${satellite.lastSeen}`;
	}

	calcDistanceToSatellite(satellite: any, lat: number, long: number, altitude: number) {
		let [x1, y1, z1] = latLongToXyz([lat, long], 6.371 + altitude / 1000);
		let [x2, y2, z2] = latLongToXyz([satellite.lat, satellite.long], satellite.altitude);
		let dist = Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2);
		dist = Math.round(dist * 100) / 100;
		return dist;
	}
}
