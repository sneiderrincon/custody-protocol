export type CustodyEventType =
  | "MANUFACTURED"
  | "QC_RELEASED"
  | "DISPATCHED"
  | "IN_TRANSIT_SCAN"
  | "RECEIVED"
  | "STERILIZED"
  | "RECALLED";

export type CustodyEvent = {
  claimId: string;
  unitId: string;
  eventType: CustodyEventType;
  actor: string;
  actorType: "Manufacturer" | "Distributor" | "Hospital" | "Regulator";
  occurredAt: string;
  streamVersion: number;
  globalPosition: number;
  location: string;
  evidenceDigest: string;
  status: "accepted" | "review" | "quarantined";
};

export type DeviceSnapshot = {
  unitId: string;
  deviceName: string;
  manufacturer: string;
  currentOwner: string;
  currentLocation: string;
  currentStatus: string;
  lastEvent: CustodyEventType;
  lastUpdate: string;
  streamVersion: number;
  globalPosition: number;
};
