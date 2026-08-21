import { spineForAthleteSession } from "../lib/athlete-data";
import { hrvResponseForSession } from "../lib/recovery-data";
for (const [id, m] of [["fischer","hsr"],["werner","hsr"],["hofmann","totalDistance"]] as const) {
  const s = spineForAthleteSession(id, "s-2026-07-18-dortmund");
  const r = s.rows.find(x=>x.metricId===m)!;
  console.log(id, m, r.value, r.reference, r.unit, r.deltaPct, r.bandLoPct, r.bandHiPct);
}
console.log("lange hrv", JSON.stringify(hrvResponseForSession("lange","s-2026-07-18-dortmund")));
