import { demoSessions, demoRecords } from "./demo-library";
const winMatches = demoSessions.filter(s => s.type === "match" && s.id !== "s-2026-07-04-dortmund" && s.dateISO >= "2026-06-22" && s.dateISO <= "2026-07-19");
for (const m of winMatches) {
  const rs = demoRecords.filter(r => r.sessionId === m.id);
  const starters = rs.filter(r => r.participation === "Full").map(r => r.athleteId).sort();
  const parts = rs.filter(r => r.participation === "Part").map(r => r.athleteId).sort();
  console.log(m.dateISO, "starters(" + starters.length + "):", starters.join(","));
  console.log("  parts(" + parts.length + "):", parts.join(","));
}
