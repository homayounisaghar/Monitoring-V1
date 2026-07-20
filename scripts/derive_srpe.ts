import { getRosterSnapshot, getSessions, buildAthleteDayRecords } from '../src/lib/demo-library';

const roster = getRosterSnapshot();
const sessions = getSessions();
const dor = sessions.find(s => s.id === 's-2026-07-04-dortmund')!;
console.log('dortmund:', dor.dateISO, dor.type, 'collect:', dor.srpeCollected);

const submitters: {id:string;au:number;min:number}[] = [];
for (const a of roster) {
  const recs = buildAthleteDayRecords(a.id);
  const rec = recs.find(r => r.sessionId === dor.id);
  if (rec && rec.srpeAU != null) submitters.push({ id: a.id, au: rec.srpeAU, min: rec.minutes });
}
console.log('submitters:', submitters.length);
const sum = submitters.reduce((s,x)=>s+x.au,0);
console.log('AVG sRPE AU over submitters (dortmund):', (sum/submitters.length).toFixed(1));
console.log('min/max:', Math.min(...submitters.map(x=>x.au)), Math.max(...submitters.map(x=>x.au)));

const matches = sessions.filter(s => s.type === 'match' && s.dateISO >= '2026-06-01' && s.dateISO <= '2026-07-19');
const perSessionAvg: {date:string;id:string;n:number;avg:number}[] = [];
for (const s of matches) {
  const vals: number[] = [];
  for (const a of roster) {
    const recs = buildAthleteDayRecords(a.id);
    const rec = recs.find(r => r.sessionId === s.id);
    if (rec && rec.srpeAU != null) vals.push(rec.srpeAU);
  }
  if (vals.length) perSessionAvg.push({ date: s.dateISO, id: s.id, n: vals.length, avg: vals.reduce((a,b)=>a+b,0)/vals.length });
}
console.log('match session averages:');
for (const x of perSessionAvg) console.log(' ', x.date, 'n='+x.n, 'avg='+x.avg.toFixed(1));

const others = perSessionAvg.filter(x => x.id !== dor.id);
console.log('TYPICAL_MATCH (mean of non-dortmund match avgs):', (others.reduce((a,b)=>a+b.avg,0)/others.length).toFixed(1));

const prior = perSessionAvg.filter(x => x.date < '2026-07-18').sort((a,b)=>a.date.localeCompare(b.date));
console.log('LAST_MATCH:', prior.at(-1)?.avg.toFixed(1));
const last5 = prior.slice(-5);
console.log('LAST_5:', (last5.reduce((a,b)=>a+b.avg,0)/last5.length).toFixed(1));

const trainings = sessions.filter(s => s.type !== 'match' && s.dateISO >= '2026-06-01' && s.dateISO <= '2026-07-19');
const tAvgs: number[] = [];
for (const s of trainings) {
  const vals: number[] = [];
  for (const a of roster) {
    const recs = buildAthleteDayRecords(a.id);
    const rec = recs.find(r => r.sessionId === s.id);
    if (rec && rec.srpeAU != null) vals.push(rec.srpeAU);
  }
  if (vals.length) tAvgs.push(vals.reduce((a,b)=>a+b,0)/vals.length);
}
console.log('TYPICAL_DAYTYPE_TRAINING avg:', (tAvgs.reduce((a,b)=>a+b,0)/tAvgs.length).toFixed(1));
