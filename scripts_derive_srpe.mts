import { getRosterSnapshot, getSessions, buildAthleteDayRecords } from './src/lib/demo-library.ts';

const roster = getRosterSnapshot();
const sessions = getSessions();
const dor = sessions.find(s => s.id === 's-2026-07-04-dortmund');
console.log('dortmund:', dor.dateISO, dor.type, 'collect:', dor.srpeCollected);

// Build all records for all athletes
const submitters = [];
for (const a of roster) {
  const recs = buildAthleteDayRecords(a.id);
  const rec = recs.find(r => r.sessionId === dor.id);
  if (rec && rec.srpeAU != null) submitters.push({ id: a.id, au: rec.srpeAU, min: rec.minutes, rating: rec.srpeRating });
}
console.log('submitters:', submitters.length);
const sum = submitters.reduce((s,x)=>s+x.au,0);
console.log('avg sRPE AU (over submitters, dortmund):', (sum/submitters.length).toFixed(1));
console.log('min/max:', Math.min(...submitters.map(x=>x.au)), Math.max(...submitters.map(x=>x.au)));

// Typical match-day: all matches in window except dortmund? typical daytype ≈ average across matches?
const matches = sessions.filter(s => s.type === 'match' && s.dateISO >= '2026-06-01' && s.dateISO <= '2026-07-19');
console.log('matches in window:', matches.map(m=>m.dateISO));

const perSessionAvg = [];
for (const s of matches) {
  const vals = [];
  for (const a of roster) {
    const recs = buildAthleteDayRecords(a.id);
    const rec = recs.find(r => r.sessionId === s.id);
    if (rec && rec.srpeAU != null) vals.push(rec.srpeAU);
  }
  if (vals.length) perSessionAvg.push({ date: s.dateISO, id: s.id, n: vals.length, avg: vals.reduce((a,b)=>a+b,0)/vals.length });
}
console.table(perSessionAvg.map(x=>({date:x.date, n:x.n, avg:x.avg.toFixed(1)})));

// typical match ≈ mean of match-day averages excluding dortmund
const others = perSessionAvg.filter(x => x.id !== dor.id);
const typMatch = others.reduce((a,b)=>a+b.avg,0)/others.length;
console.log('typical match (mean of non-dortmund match avgs):', typMatch.toFixed(1));

// typical daytype = same as typical_match for a match session
// last_match: most recent prior match
const priorMatches = perSessionAvg.filter(x => x.date < '2026-07-18').sort((a,b)=>a.date.localeCompare(b.date));
console.log('last match:', priorMatches.at(-1));
const last5 = priorMatches.slice(-5);
console.log('last_5 avg:', (last5.reduce((a,b)=>a+b.avg,0)/last5.length).toFixed(1));

// training day type — for completeness — average across training sessions
const trainings = sessions.filter(s => s.type !== 'match' && s.dateISO >= '2026-06-01' && s.dateISO <= '2026-07-19');
const tAvgs = [];
for (const s of trainings) {
  const vals = [];
  for (const a of roster) {
    const recs = buildAthleteDayRecords(a.id);
    const rec = recs.find(r => r.sessionId === s.id);
    if (rec && rec.srpeAU != null) vals.push(rec.srpeAU);
  }
  if (vals.length) tAvgs.push(vals.reduce((a,b)=>a+b,0)/vals.length);
}
console.log('training day-type avg:', (tAvgs.reduce((a,b)=>a+b,0)/tAvgs.length).toFixed(1));
