export type Satellite = {
	prnNumber: number;
	network: string;
	elevation: number;
	azimuth: number;
	snr: number;
	lastSeen: Date;
	lat: number;
	long: number;
	colour: string;
	altitude: number;
	previousPositions: number[][];
};
