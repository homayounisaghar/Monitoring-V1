import { demoSessions, demoAthletes } from "./demo-library";
// Manually re-check: which same-position sub swaps could have happened
const posMap = new Map(demoAthletes.map(a => [a.id, a.position]));
console.log("hofmann pos:", posMap.get("hofmann"));
console.log("wagner pos:", posMap.get("wagner"));
