// Deterministic date formatting from an ISO YYYY-MM-DD string.
// No Intl, no toLocale*, no timezone-sensitive Date parsing paths on the
// display side. Weekdays come from getUTCDay() applied to a UTC-midnight
// Date, which is stable across runtimes and locales.

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
] as const;

const MONTHS_LONG = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
] as const;

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] as const;

const WEEKDAYS_LONG = [
  "Sunday", "Monday", "Tuesday", "Wednesday",
  "Thursday", "Friday", "Saturday",
] as const;

type Parts = { y: number; m: number; d: number };

function parts(iso: string): Parts {
  // iso is "YYYY-MM-DD"
  const y = Number(iso.slice(0, 4));
  const m = Number(iso.slice(5, 7));
  const d = Number(iso.slice(8, 10));
  return { y, m, d };
}

function weekday(iso: string): string {
  const { y, m, d } = parts(iso);
  const t = Date.UTC(y, m - 1, d);
  return WEEKDAYS[new Date(t).getUTCDay()];
}

function pad2(n: number): string {
  return n < 10 ? `0${n}` : String(n);
}

/** "19 Jul", "08 Jul" — two-digit day, zero-padded. */
export function dayMonth2(iso: string): string {
  const { m, d } = parts(iso);
  return `${pad2(d)} ${MONTHS[m - 1]}`;
}

/** "Mon 22 Jun" — no leading zero on the day. */
export function weekdayDayMonth(iso: string): string {
  const { m, d } = parts(iso);
  return `${weekday(iso)} ${d} ${MONTHS[m - 1]}`;
}

/** "13 Apr" — no leading zero. */
export function dayMonth(iso: string): string {
  const { m, d } = parts(iso);
  return `${d} ${MONTHS[m - 1]}`;
}

/** "Sat 18 Jul 2026" — weekday, day (no leading zero), month, year. */
export function weekdayDayMonthYear(iso: string): string {
  const { y, m, d } = parts(iso);
  return `${weekday(iso)} ${d} ${MONTHS[m - 1]} ${y}`;
}

/**
 * "Mon 22 Jun – Sun 19 Jul 2026" — en dash, single space each side.
 * Same-year: year prints once at the end.
 * Cross-year: year prints on both ends.
 */
export function rangeLabel(startISO: string, endISO: string): string {
  const s = parts(startISO);
  const e = parts(endISO);
  const startCore = `${weekday(startISO)} ${s.d} ${MONTHS[s.m - 1]}`;
  const endCore = `${weekday(endISO)} ${e.d} ${MONTHS[e.m - 1]}`;
  if (s.y === e.y) {
    return `${startCore} – ${endCore} ${e.y}`;
  }
  return `${startCore} ${s.y} – ${endCore} ${e.y}`;
}

/** "13 April" — full month name, no leading zero on the day. */
export function dayMonthLong(iso: string): string {
  const { m, d } = parts(iso);
  return `${d} ${MONTHS_LONG[m - 1]}`;
}

/** "Tuesday" — full weekday, zone-independent. */
export function weekdayLong(iso: string): string {
  const { y, m, d } = parts(iso);
  const t = Date.UTC(y, m - 1, d);
  return WEEKDAYS_LONG[new Date(t).getUTCDay()];
}
