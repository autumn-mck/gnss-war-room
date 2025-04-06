import { type Satellite } from "./satellite.ts";

export type GnssData = {
	satellites: Satellite[];
	latitude: number;
	longitude: number;
	date: string;
	lastRecordedTime: Date;
	altitude: number;
	altitudeUnit: string;
	geoidSeparation: number;
	geoidSeparationUnit: string;
	pdop: number;
	hdop: number;
	vdop: number;
	interference: number;
	fixQuality: number;
};
