import { demoRecords, demoSessions, demoAthletes, recordsForSession } from '../src/lib/demo-library';

const dor = demoSessions.find(s => s.id === 's-2026-07-04-dortmund')!;
console.log('dortmund:', dor.dateISO, dor.type, 'collect:', dor.srpeCollected);

const dorRecs = recordsForSession(dor.id).filter(r => r.srpeAU != null);
console.log('submitters:', dorRecs.length);
const avg = dorRecs.reduce((s, r) => s + (r.srpeAU as number), 0) / dorRecs.length;
console.log('AVG sRPE AU over submitters (dortmund):', avg.toFixed(1));
console.log('min/max:', Math.min(...dorRecs.map(r=>r.srpeAU!)), Math.max(...dorRecs.map(r=>r.srpeAU!)));

const matches = demoSessions.filter(s => s.type === 'match' && s.dateISO >= '2026-06-01' && s.dateISO <= '2026-07-19');
const perMatch = matches.map(s => {
  const rs = recordsForSession(s.id).filter(r => r.srpeAU != null);
  return { date: s.dateISO, id: s.id, n: rs.length, avg: rs.length ? rs.reduce((a,r)=>a+r.srpeAU!,0)/rs.length : 0 };
}).filter(x => x.n > 0);
console.log('match averages:');
for (const x of perMatch) console.log(' ', x.date, 'n='+x.n, 'avg='+x.avg.toFixed(1));

const others = perMatch.filter(x => x.id !== dor.id);
console.log('TYPICAL_MATCH (mean others):', (others.reduce((a,b)=>a+b.avg,0)/others.length).toFixed(1));

const prior = perMatch.filter(x => x.date < '2026-07-18').sort((a,b)=>a.date.localeCompare(b.date));
console.log('LAST_MATCH:', prior.at(-1)?.avg.toFixed(1));
const last5 = prior.slice(-5);
console.log('LAST_5:', (last5.reduce((a,b)=>a+b.avg,0)/last5.length).toFixed(1));

const trainings = demoSessions.filter(s => s.type !== 'match' && s.dateISO >= '2026-06-01' && s.dateISO <= '2026-07-19');
const tAvgs: number[] = [];
for (const s of trainings) {
  const rs = recordsForSession(s.id).filter(r => r.srpeAU != null);
  if (rs.length) tAvgs.push(rs.reduce((a,r)=>a+r.srpeAU!,0)/rs.length);
}
console.log('TYPICAL_DAYTYPE_TRAINING avg:', (tAvgs.reduce((a,b)=>a+b,0)/tAvgs.length).toFixed(1));
