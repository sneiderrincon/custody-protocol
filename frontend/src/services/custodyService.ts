import type { CustodyEvent, DeviceSnapshot } from "../types/custody";

export const snapshot: DeviceSnapshot = {
  unitId: "udi_di:00812345678901/serial:MX-2048-1190",
  deviceName: "Sterile implantable infusion port",
  manufacturer: "Andean Medical Manufacturing",
  currentOwner: "Hospital Universitario San Ignacio",
  currentLocation: "Bogota DC / OR-7 sterile storage",
  currentStatus: "In custody",
  lastEvent: "RECEIVED",
  lastUpdate: "2026-08-05 14:38 UTC",
  streamVersion: 18,
  globalPosition: 8214605,
};

export const custodyEvents: CustodyEvent[] = [
  {
    claimId: "clm_018fb24d-086e-7e47-87a2-244df6a916af",
    unitId: snapshot.unitId,
    eventType: "MANUFACTURED",
    actor: "Andean Medical Manufacturing",
    actorType: "Manufacturer",
    occurredAt: "2026-08-01 09:12 UTC",
    streamVersion: 14,
    globalPosition: 8214560,
    location: "Medellin GMP Plant / Line 4",
    evidenceDigest: "6f38a9c11d4478e8b6af746d9a6c3e5c2f901be21a1bbfb3d4410972c47fd940",
    status: "accepted",
  },
  {
    claimId: "clm_018fb31c-2a10-70d4-a923-9b53730a122e",
    unitId: snapshot.unitId,
    eventType: "QC_RELEASED",
    actor: "Quality Assurance Unit",
    actorType: "Manufacturer",
    occurredAt: "2026-08-02 16:44 UTC",
    streamVersion: 15,
    globalPosition: 8214579,
    location: "Medellin GMP Plant / QA Vault",
    evidenceDigest: "9d1f29ee4d4a6cc076d6f71cead985a4072f1abaf8d3a67031ce1f402e73e925",
    status: "accepted",
  },
  {
    claimId: "clm_018fb42f-88ad-7471-b8e0-5db993a0fe22",
    unitId: snapshot.unitId,
    eventType: "DISPATCHED",
    actor: "Cold Chain Distributor SAS",
    actorType: "Distributor",
    occurredAt: "2026-08-03 11:05 UTC",
    streamVersion: 16,
    globalPosition: 8214591,
    location: "Bogota bonded logistics hub",
    evidenceDigest: "3ff81ce154612750abe037020a41b4cd31fafc0d3277c87893d899d3d3f1df63",
    status: "accepted",
  },
  {
    claimId: "clm_018fb51a-3ffe-7e56-a12d-a72a9165b0a3",
    unitId: snapshot.unitId,
    eventType: "IN_TRANSIT_SCAN",
    actor: "Airport Bonded Warehouse",
    actorType: "Distributor",
    occurredAt: "2026-08-04 03:21 UTC",
    streamVersion: 17,
    globalPosition: 8214598,
    location: "El Dorado custody checkpoint",
    evidenceDigest: "cb89e9bb83361a9ddc176283cb0ab8fa3286e5b841438f16d084ad98a6d186d9",
    status: "review",
  },
  {
    claimId: "clm_018fb6b2-47a6-7e18-91e1-3a6dd8fb3a21",
    unitId: snapshot.unitId,
    eventType: "RECEIVED",
    actor: "Hospital Universitario San Ignacio",
    actorType: "Hospital",
    occurredAt: "2026-08-05 14:38 UTC",
    streamVersion: 18,
    globalPosition: 8214605,
    location: "Bogota DC / OR-7 sterile storage",
    evidenceDigest: "ac47dd06377559cdbb2c2b56d533a650b15cd793e52ed415aa40409220ff14f2",
    status: "accepted",
  },
];

export async function fetchDeviceCustody(unitId: string) {
  await new Promise((resolve) => window.setTimeout(resolve, 260));
  return {
    snapshot: { ...snapshot, unitId },
    events: custodyEvents.map((event) => ({ ...event, unitId })),
  };
}
