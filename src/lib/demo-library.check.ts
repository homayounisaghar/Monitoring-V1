/**
 * ST2 — Demo library self-checks (Workstream 01 · prompt 1/4, corrections 1b).
 * Not imported by the app. Run in the sandbox to verify §-level invariants.
 */
import {
  demoSessions, demoRecords, demoAthletes, demoDays,
  recordsForAthlete, recordsForSession, DEMO_TODAY,
  buildSessions, buildDays, buildRecords,
  DAY_TD_DOMAIN_MAX, contractRowFor,
  type DemoRecord, type DemoSession,
} from "./demo-library";
import {
  TYPICAL_METRICS,
  typicalFor, comparableSessionCount,
  bucketKeyFor, allBucketKeys,
  expectedSumForSession,
  _samplesFor,
} from "./demo-typicals";



type Check = { name: string; pass: boolean; detail: string };

function inWindow(s: { dateISO: string }): boolean {
  return s.dateISO >= "2026-06-22" && s.dateISO <= "2026-07-19";
}

export function runDemoLibraryChecks(): Check[] {
  const out: Check[] = [];
  const push = (name: string, pass: boolean, detail: string) => out.push({ name, pass, detail });

  const win = demoSessions.filter(inWindow);
  const matches = win.filter((s) => s.type === "match");
  const nonMatch = win.filter((s) => s.type !== "match");
  push("28-day sessions total = 24", win.length === 24, `got ${win.length}`);
  push("28-day matches = 5", matches.length === 5, `got ${matches.length}`);
  push("28-day non-match = 19", nonMatch.length === 19, `got ${nonMatch.length}`);

  // demoDays checks (§2).
  const day714 = demoDays.find((d) => d.dateISO === "2026-07-14");
  push("demoDays has no entry for 14 Jul", !day714, day714 ? "present" : "absent");
  const restDates = ["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"];
  const restsAsDays = restDates.every((d) => demoDays.find((x) => x.dateISO === d)?.kind === "rest");
  push("Four rest dates present as demoDays kind=rest", restsAsDays, restDates.join(","));

  const missingSession = demoSessions.find((s) => s.dateISO === "2026-07-14");
  push("Tue 14 Jul missing (no session)", !missingSession, missingSession ? `found ${missingSession.id}` : "absent");

  const restRecordsZero = demoRecords
    .filter((r) => restDates.includes(r.dateISO))
    .every((r) => r.totalDistance === 0 && r.hsr === 0 && r.minutes === 0 && r.sessionId === null);
  push("Rest-day records zero and sessionId null", restRecordsZero, "");

  const doubleDay = demoSessions.filter((s) => s.dateISO === "2026-07-13");
  push("Mon 13 Jul double-session",
    doubleDay.length === 2 && doubleDay.some((s) => s.type === "gym") && doubleDay.some((s) => s.type === "training"),
    doubleDay.map((s) => s.name).join(" + "));

  // §1 — every non-match session's name day-code must equal dayCodeFor(dateISO).
  const codeRe = /^(MD[-+]\d)/;
  const badCode = demoSessions
    .filter((s) => s.type !== "match")
    .map((s) => {
      const m = s.name.match(codeRe);
      if (!m) return null;
      return m[1] === s.dayCode ? null : `${s.dateISO}: name=${m[1]} dayCode=${s.dayCode}`;
    })
    .filter((x): x is string => x !== null);
  push("Non-match session name day-code matches dayCode (§1)", badCode.length === 0, badCode.join(" | "));

  const koehler = recordsForAthlete("koehler").filter((r) => r.inSquad);
  const koehlerDays = new Set(koehler.map((r) => r.dateISO));
  const koehlerFirst = [...koehlerDays].sort()[0];
  push("Köhler first record ≥ 2026-07-07", (koehlerFirst ?? "") >= "2026-07-07", `first=${koehlerFirst}`);
  const koehlerWindow = koehler.filter(inWindow).length;
  push("Köhler 13 records in 28-day window", koehlerWindow === 13, `got ${koehlerWindow}`);

  const voss = recordsForAthlete("voss").filter((r) => inWindow(r) && r.participation !== null);
  const vossAlwaysInjury = voss.every((r) => r.participation === "Injury");
  push("Voss = Injury throughout window", vossAlwaysInjury && voss.length > 0, `count=${voss.length}`);
  const vossZeroMinutes = recordsForAthlete("voss")
    .filter((r) => inWindow(r) && r.sessionId !== null && r.sessionId !== "s-2026-07-04-dortmund")
    .every((r) => r.minutes === 0);
  push("Voss zero minutes on all pre-pinned window sessions (§3)", vossZeroMinutes, "");

  const langeArc = recordsForAthlete("lange").filter((r) => inWindow(r) && r.sessionId !== null)
    .sort((a, b) => a.dateISO.localeCompare(b.dateISO));
  const seen: string[] = [];
  for (const r of langeArc) {
    if (r.participation && seen[seen.length - 1] !== r.participation) seen.push(r.participation);
  }
  push("Lange arc Full→Part→Rehab→Injury", seen.join(">") === "Full>Part>Rehab>Injury", seen.join(">"));

  const jul02Session = demoSessions.find((s) => s.dateISO === "2026-07-02");
  const jul02 = jul02Session ? recordsForSession(jul02Session.id) : [];
  const brandt = jul02.find((r) => r.athleteId === "brandt");
  const kuhn = jul02.find((r) => r.athleteId === "kuhn");
  push(
    "2 Jul session is MD-2 · Intensive (training)",
    !!jul02Session && jul02Session.type === "training" && jul02Session.name.startsWith("MD-2"),
    `type=${jul02Session?.type} name=${jul02Session?.name}`,
  );
  push("Brandt <80 % HR on 2 Jul (MD-2)", !!brandt && (brandt.hrCoveragePct ?? 100) < 80, `hr=${brandt?.hrCoveragePct}`);
  push("Kuhn <80 % HR on 2 Jul (MD-2)", !!kuhn && (kuhn.hrCoveragePct ?? 100) < 80, `hr=${kuhn?.hrCoveragePct}`);

  // Missing day (§3, prompt 1d) — a gap must be between things, not the edge.
  const jul14Session = demoSessions.find((s) => s.dateISO === "2026-07-14");
  const jul14Day = demoDays.find((d) => d.dateISO === "2026-07-14");
  const jul13Day = demoDays.find((d) => d.dateISO === "2026-07-13");
  const jul15Day = demoDays.find((d) => d.dateISO === "2026-07-15");
  push(
    "14 Jul missing (no session, no demoDays entry) and 13/15 Jul present",
    !jul14Session && !jul14Day && !!jul13Day && !!jul15Day,
    `session=${!!jul14Session} day=${!!jul14Day} 13=${!!jul13Day} 15=${!!jul15Day}`,
  );

  // Beyond-range day — cause travels with effect.
  const jul08Session = demoSessions.find((s) => s.dateISO === "2026-07-08");
  push(
    "8 Jul session is a match with note='AET'",
    !!jul08Session && jul08Session.type === "match" && jul08Session.note === "AET",
    `type=${jul08Session?.type} note=${jul08Session?.note}`,
  );

  // sRPE-not-collected days must resolve to real recovery sessions.
  const noCollectRecovery = ["2026-07-12", "2026-07-19"].every((d) => {
    const s = demoSessions.find((x) => x.dateISO === d);
    return s?.type === "recovery" && s?.srpeCollected === false;
  });
  push("12/19 Jul are recovery sessions with srpeCollected=false", noCollectRecovery, "");

  const unconfirmed = demoSessions.filter((s) => s.unconfirmed);
  push("Exactly one unconfirmed session", unconfirmed.length === 1 && unconfirmed[0].dateISO === "2026-07-19", unconfirmed.map((s) => s.dateISO).join(","));

  // Beyond-range: verified against a fixed drawn domain, not a %-vs-peer trick.
  // (a) Exactly one calendar day in the full library exceeds DAY_TD_DOMAIN_MAX,
  // and that day is 2026-07-08. (b) No athlete-session exceeds 15,000 m — the
  // plausibility floor the retired multiplier was breaching.
  const dayTotals = new Map<string, number>();
  for (const r of demoRecords) {
    dayTotals.set(r.dateISO, (dayTotals.get(r.dateISO) ?? 0) + r.totalDistance);
  }
  const overCap = [...dayTotals.entries()].filter(([, td]) => td > DAY_TD_DOMAIN_MAX);
  push(
    `Exactly one day exceeds DAY_TD_DOMAIN_MAX=${DAY_TD_DOMAIN_MAX} and it is 8 Jul`,
    overCap.length === 1 && overCap[0][0] === "2026-07-08",
    overCap.map(([d, td]) => `${d}=${td}`).join(", ") || "none",
  );
  const maxAthleteTd = demoRecords.reduce((m, r) => Math.max(m, r.totalDistance), 0);
  const maxRec = demoRecords.find((r) => r.totalDistance === maxAthleteTd);
  push(
    "No athlete-session exceeds 15,000 m total distance",
    maxAthleteTd <= 15000,
    `max=${maxAthleteTd} m (${maxRec?.athleteId} on ${maxRec?.dateISO})`,
  );

  const frei = recordsForAthlete("frei").filter((r) => r.srpeAU != null);
  push("Frei has zero sRPE records", frei.length === 0, `count=${frei.length}`);

  /* ─── §1 (prompt 1d) — participation contract invariant ─── */
  const PINNED_SESSION_ID = "s-2026-07-04-dortmund";
  type Violation = { athleteId: string; dateISO: string; tag: string; field: string; got: string };
  const violations: Violation[] = [];
  const exemptions: { athleteId: string; tag: string; minutes: number }[] = [];
  for (const r of demoRecords) {
    // Rest-day records are the one legitimate zero — outside the tag contract.
    if (r.sessionId === null) continue;
    const row = contractRowFor(r.participation);
    const tag = r.participation ?? "unselected";
    // Declared exception: pinned session may carry Injury with minutes>0.
    if (r.sessionId === PINNED_SESSION_ID && r.participation === "Injury" && r.minutes > 0) {
      exemptions.push({ athleteId: r.athleteId, tag, minutes: r.minutes });
      continue;
    }
    const v = (field: string, got: unknown) =>
      violations.push({ athleteId: r.athleteId, dateISO: r.dateISO, tag, field, got: String(got) });
    if (row.hasMinutes) {
      if (r.minutes <= 0) v("minutes", r.minutes);
    } else {
      if (r.minutes !== 0) v("minutes", r.minutes);
    }
    if (row.hasLoad) {
      if (r.totalDistance <= 0) v("totalDistance", r.totalDistance);
      if (r.cardioLoad === null && r.hrCoveragePct !== null) {
        // cardioLoad may be null when coverage is absent even for hasLoad tags;
        // but hasLoad tags must at least produce non-zero external load.
      }
    } else {
      if (r.totalDistance !== 0) v("totalDistance", r.totalDistance);
      if (r.hsr !== 0) v("hsr", r.hsr);
      if (r.sprintDist !== 0) v("sprintDist", r.sprintDist);
      if (r.accDec !== 0) v("accDec", r.accDec);
      if (r.mMin !== 0) v("mMin", r.mMin);
      if (r.topSpeedKmh !== 0) v("topSpeedKmh", r.topSpeedKmh);
      if (r.cardioLoad !== null) v("cardioLoad", r.cardioLoad ?? "null");
    }
    if (row.hasCoverage) {
      if (r.hrCoveragePct === null) v("hrCoveragePct", "null");
    } else {
      if (r.hrCoveragePct !== null) v("hrCoveragePct", r.hrCoveragePct);
    }
    if (!row.srpeEligible) {
      if (r.srpeRating !== null) v("srpeRating", r.srpeRating);
      if (r.srpeAU !== null) v("srpeAU", r.srpeAU);
    }
  }
  const exemptDetail = exemptions
    .map((e) => `${e.athleteId} ${e.tag}@${e.minutes}′`).join(", ") || "none";
  push(
    `Contract invariant holds for every record (exempt: ${exemptDetail})`,
    violations.length === 0,
    violations.slice(0, 12).map((x) => `${x.athleteId}/${x.dateISO}/${x.tag}: ${x.field}=${x.got}`).join(" | "),
  );

  // §4 — match squad shape: exactly 11 rows with minutes ≥ 85; 3–5 Part rows.
  // Pinned Dortmund exempt.
  const shapeIssues: string[] = [];
  const starterCounts = new Map<string, number>();
  const nonPinnedMatches = matches.filter((m) => m.id !== "s-2026-07-04-dortmund");
  for (const m of nonPinnedMatches) {
    const rs = recordsForSession(m.id);
    const starters = rs.filter((r) => r.participation === "Full" && r.minutes >= 85);
    const parts = rs.filter((r) => r.participation === "Part");
    if (starters.length !== 11) shapeIssues.push(`${m.dateISO} starters=${starters.length}`);
    if (parts.length < 3 || parts.length > 5) shapeIssues.push(`${m.dateISO} parts=${parts.length}`);
    for (const r of starters) starterCounts.set(r.athleteId, (starterCounts.get(r.athleteId) ?? 0) + 1);
  }
  push("Each non-pinned match: 11 starters ≥85′ and 3–5 Part (§4)", shapeIssues.length === 0, shapeIssues.join(" | "));

  // Keller is the roster's only GK, so he is always the starting keeper — exempt.
  const alwaysStarter = Array.from(starterCounts.entries())
    .filter(([id, c]) => id !== "keller" && c === nonPinnedMatches.length);
  push("No outfield athlete is starter in every match (§4)", alwaysStarter.length === 0, alwaysStarter.map(([id]) => id).join(","));

  // §4 — all six participation tags occur at least once in the 28-day window.
  const tagsSeen = new Set<string>();
  for (const r of demoRecords) if (inWindow(r) && r.participation) tagsSeen.add(r.participation);
  const wantedTags = ["Full", "Part", "Modified", "Other", "Rehab", "Injury"];
  const missingTags = wantedTags.filter((t) => !tagsSeen.has(t));
  push("All six participation tags occur in window (§4)", missingTags.length === 0, missingTags.length ? `missing: ${missingTags.join(",")}` : Array.from(tagsSeen).sort().join(","));

  // §5 — real determinism: re-run builders and deep-compare.
  const s2 = buildSessions();
  const d2 = buildDays();
  const r2 = buildRecords();
  const firstDiff = <T,>(a: readonly T[], b: readonly T[], label: string): string | null => {
    if (a.length !== b.length) return `${label}: length ${a.length} vs ${b.length}`;
    for (let i = 0; i < a.length; i++) {
      const A = JSON.stringify(a[i]);
      const B = JSON.stringify(b[i]);
      if (A !== B) return `${label}[${i}]: ${A} !== ${B}`;
    }
    return null;
  };
  const detSess = firstDiff(demoSessions, s2, "sessions");
  const detDays = firstDiff(demoDays, d2, "days");
  const detRecs = firstDiff(demoRecords, r2, "records");
  const detFail = [detSess, detDays, detRecs].filter(Boolean).join(" | ");
  push("Builders deterministic (deep-equal on re-run) (§5)", detFail === "", detFail);

  push("DEMO_TODAY = 2026-07-19", DEMO_TODAY === "2026-07-19", DEMO_TODAY);
  push("Roster size = 19", demoAthletes.length === 19, `n=${demoAthletes.length}`);

  /* ═════════════════ typicals layer (Workstream 01 · prompt 2/4) ═════════════════ */





  // (a) Every typical carries its bucket key; no code path returns a pooled mean.
  //     Enforced structurally: `typicalFor` requires a BucketKey and there is no
  //     pooled/positional builder to call. Assert here by inspecting every
  //     reachable typical result and confirming its bucketKey matches the input.
  const bkAll = allBucketKeys();
  let bkMismatch = 0;
  for (const a of demoAthletes) for (const bk of bkAll) {
    const t = typicalFor(a.id, bk);
    if (t.bucketKey !== bk) bkMismatch++;
  }
  push("Every typical carries its bucket key (§6.a)", bkMismatch === 0, `mismatched=${bkMismatch}`);

  // (b) Sample count per (athlete, bucket) = count of that athlete's
  //     minutes-bearing records in that bucket. Proves Injury/Rehab/Other/
  //     unselected contribute nothing.
  const sessionById = new Map(demoSessions.map((s) => [s.id, s]));
  let sampleMismatch = 0;
  const MINB = new Set(["Full", "Part", "Modified"]);
  for (const a of demoAthletes) {
    // Group this athlete's minutes-bearing, non-unconfirmed, non-rest records by bucket.
    const expectedByBucket = new Map<string, number>();
    for (const r of demoRecords) {
      if (r.athleteId !== a.id) continue;
      if (r.sessionId == null) continue;
      const s = sessionById.get(r.sessionId)!;
      if (s.unconfirmed) continue;
      if (r.participation == null || !MINB.has(r.participation)) continue;
      if (r.minutes <= 0) continue;
      const bk = bucketKeyFor(s);
      expectedByBucket.set(bk, (expectedByBucket.get(bk) ?? 0) + 1);
    }
    for (const bk of bkAll) {
      const expected = expectedByBucket.get(bk) ?? 0;
      const got = comparableSessionCount(a.id, bk);
      if (got !== expected) sampleMismatch++;
    }
  }
  push("Sample count = minutes-bearing records per bucket (§6.b)", sampleMismatch === 0, `mismatched=${sampleMismatch}`);

  // (c) Neither the 19 Jul unconfirmed session nor any rest day appears in any
  //     sample set.
  const restDatesSet = new Set(["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"]);
  let banned = 0;
  const bannedDetails: string[] = [];
  for (const a of demoAthletes) for (const bk of bkAll) {
    for (const r of _samplesFor(a.id, bk)) {
      if (r.dateISO === "2026-07-19") { banned++; bannedDetails.push(`unconf ${a.id}`); }
      if (restDatesSet.has(r.dateISO)) { banned++; bannedDetails.push(`rest ${a.id}/${r.dateISO}`); }
    }
  }
  push("No unconfirmed / rest-day rows enter samples (§6.c)", banned === 0, bannedDetails.slice(0, 6).join(" | "));

  // (d) Every typical at or above the minimum has non-zero SD on every metric.
  //     Report the smallest SD found and which metric+bucket it came from.
  let smallest: { athleteId: string; bucketKey: string; metric: string; sd: number; fs: number } | null = null;
  let zeroSd = 0;
  const zeroDetails: string[] = [];
  for (const a of demoAthletes) for (const bk of bkAll) {
    const t = typicalFor(a.id, bk);
    if (t.state !== "computed") continue;
    for (const m of TYPICAL_METRICS) {
      const pm = t.metrics[m];
      if (!pm) continue;
      if (pm.sd === 0) { zeroSd++; if (zeroDetails.length < 4) zeroDetails.push(`${a.id}/${bk}/${m}`); }
      const rel = pm.fullSession !== 0 ? pm.sd / Math.abs(pm.fullSession) : pm.sd;
      if (!smallest || rel < (smallest.fs !== 0 ? smallest.sd / Math.abs(smallest.fs) : smallest.sd)) {
        smallest = { athleteId: a.id, bucketKey: bk, metric: m, sd: pm.sd, fs: pm.fullSession };
      }
    }
  }
  const smallestDetail = smallest
    ? `smallest sd/|mean|=${(smallest.fs !== 0 ? smallest.sd / Math.abs(smallest.fs) : smallest.sd).toFixed(4)} @ ${smallest.athleteId}/${smallest.bucketKey}/${smallest.metric} (sd=${smallest.sd.toFixed(2)}, mean=${smallest.fs.toFixed(2)})`
    : "no samples";
  push("Every computed typical has non-zero SD on every metric (§6.d)",
    zeroSd === 0,
    zeroSd === 0 ? smallestDetail : `zeroSd=${zeroSd} [${zeroDetails.join(", ")}] | ${smallestDetail}`);

  // (e) Köhler withholds in every bucket, and print his per-bucket count.
  const koehlerCounts = bkAll.map((bk) => `${bk}:${comparableSessionCount("koehler", bk)}`);
  const koehlerAllWithheld = bkAll.every((bk) => typicalFor("koehler", bk).state === "withheld");
  push("Köhler withholds in every bucket (§6.e)", koehlerAllWithheld, koehlerCounts.join(" "));

  // (f) At least one athlete has a computable typical in each of the four
  //     load-bearing buckets.
  const needed: Array<[string, DemoSession["type"]]> = [
    ["MD", "match"],
    ["MD-1", "training"],
    ["MD-2", "training"],
    ["MD+1", "recovery"],
  ];
  const bucketMisses: string[] = [];
  for (const [dc, st] of needed) {
    const bk = `${dc}::${st}`;
    const anyone = demoAthletes.some((a) => typicalFor(a.id, bk).state === "computed");
    if (!anyone) bucketMisses.push(bk);
  }
  push("Load-bearing buckets each have ≥1 computable typical (§6.f)", bucketMisses.length === 0, bucketMisses.join(","));

  // (g) Expected sum for pinned 18 July computes, states its coverage, and
  //     names any withheld participants.
  const es = expectedSumForSession("s-2026-07-04-dortmund");
  const esOk = es.state === "computed" && es.participatedCount > 0;
  const esDetail = es.state === "computed"
    ? `contributed=${es.contributedCount}/${es.participatedCount} coverage=${(es.coverage * 100).toFixed(0)}% withheld=[${es.withheldAthletes.join(",") || "none"}]`
    : `withheld reason=${es.reason} contrib=${es.contributedCount}/${es.participatedCount}`;
  push("Expected sum for pinned 18 Jul computes with coverage stated (§6.g)", esOk, esDetail);

  // (h) Determinism: read every typical twice, deep-compare. Because
  //     `typicalFor` is a pure function of frozen module state and cached, a
  //     second call must return identical serialised output for every key.
  let typDiffs = 0;
  for (const a of demoAthletes) for (const bk of bkAll) {
    const A = JSON.stringify(typicalFor(a.id, bk));
    const B = JSON.stringify(typicalFor(a.id, bk));
    if (A !== B) typDiffs++;
  }
  const esA = JSON.stringify(expectedSumForSession("s-2026-07-04-dortmund"));
  const esB = JSON.stringify(expectedSumForSession("s-2026-07-04-dortmund"));
  const esSame = esA === esB;
  push("Typicals layer deterministic (§6.h)", typDiffs === 0 && esSame, `typicalDiffs=${typDiffs} expectedSameSum=${esSame}`);

  /* ═════════════════ prompt 1e — day-code census ═════════════════ */

  // Census: prints every (dayCode, sessionType) bucket and its session count,
  // sorted descending. Always passes; exists to report the number the
  // Longitudinal build needs before designing around withheld baselines.
  const censusCounts = new Map<string, number>();
  for (const s of demoSessions) {
    const key = `${s.dayCode}::${s.type}`;
    censusCounts.set(key, (censusCounts.get(key) ?? 0) + 1);
  }
  const censusSorted = [...censusCounts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const censusDetail = censusSorted.map(([k, n]) => `${k}=${n}`).join(" ");
  push("Day-code census (report-only, prompt 1e §4)", true, censusDetail);

  // Assert MD-2, MD-3, MD-4 and MD-5 (all sessionType=training) each have ≥5
  // sessions. If any is short, report the counts — do not adjust the assertion.
  const targetCodes = ["MD-2", "MD-3", "MD-4", "MD-5"];
  const shortCodes: string[] = [];
  for (const dc of targetCodes) {
    const n = censusCounts.get(`${dc}::training`) ?? 0;
    if (n < 5) shortCodes.push(`${dc}=${n}`);
  }
  push(
    "MD-2, MD-3, MD-4, MD-5 buckets each have ≥5 sessions (prompt 1e §4)",
    shortCodes.length === 0,
    shortCodes.length === 0
      ? targetCodes.map((dc) => `${dc}=${censusCounts.get(`${dc}::training`) ?? 0}`).join(" ")
      : `SHORT: ${shortCodes.join(" ")}`,
  );

  // Second-highest day total — reported so DAY_TD_DOMAIN_MAX can be re-examined
  // as new matches enter the history. Only actionable if a day other than
  // 2026-07-08 now exceeds the cap; §3 asserts that separately above.
  const dayTotalsAll = new Map<string, number>();
  for (const r of demoRecords) dayTotalsAll.set(r.dateISO, (dayTotalsAll.get(r.dateISO) ?? 0) + r.totalDistance);
  const sortedDays = [...dayTotalsAll.entries()].sort((a, b) => b[1] - a[1]);
  const secondHighest = sortedDays[1];
  push(
    "Second-highest day total sits below DAY_TD_DOMAIN_MAX (report)",
    !!secondHighest && secondHighest[1] < DAY_TD_DOMAIN_MAX,
    `top=${sortedDays[0]?.[0]}=${sortedDays[0]?.[1]}  second=${secondHighest?.[0]}=${secondHighest?.[1]}`,
  );

  // Extended-stretch rest rule (prompt 1e §2) — the Monday after each
  // pre-31-May match is a rest day, and the four fixed rest dates inside the
  // 28-day window are unchanged.
  const fixedRest = new Set(["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"]);
  const fixedRestOk = [...fixedRest].every((d) => demoDays.find((x) => x.dateISO === d)?.kind === "rest");
  const winRestCount = demoDays.filter((d) => d.kind === "rest" && d.dateISO >= "2026-06-22" && d.dateISO <= "2026-07-19").length;
  push(
    "28-day window still contains exactly four rest days on the original dates",
    fixedRestOk && winRestCount === 4,
    `fixed=${fixedRestOk} winRest=${winRestCount}`,
  );
  const expectedExtRest = ["2026-04-20", "2026-04-27", "2026-05-04", "2026-05-11", "2026-05-18", "2026-05-25"];
  const extRestOk = expectedExtRest.every((d) => demoDays.find((x) => x.dateISO === d)?.kind === "rest");
  push(
    "Extended stretch: Monday-after-match is rest (six new dates)",
    extRestOk,
    expectedExtRest.map((d) => `${d}:${demoDays.find((x) => x.dateISO === d)?.kind ?? "-"}`).join(" "),
  );

  return out;
}


declare const process: { argv: string[]; exit(n: number): never } | undefined;
if (typeof process !== "undefined" && process.argv[1] && process.argv[1].endsWith("demo-library.check.ts")) {
  const results = runDemoLibraryChecks();
  const pad = (s: string, n: number) => (s + " ".repeat(n)).slice(0, n);
  for (const r of results) {
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${pad(r.name, 62)}  ${r.detail}`);
  }
  const fails = results.filter((r) => !r.pass).length;
  console.log(`\n${results.length - fails}/${results.length} passed`);
  process.exit(fails === 0 ? 0 : 1);
}
// Silence unused-import warning if types get tree-shaken.
export type _DemoRecord = DemoRecord;
