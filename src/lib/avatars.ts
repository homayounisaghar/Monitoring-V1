/**
 * ST2 — Athlete portrait mapping.
 * Portraits live in /public/portraits/ and are served at /portraits/pNN.jpg.
 * Mapping is fixed per athlete id so the same face follows the same player
 * across sessions and views.
 */

const AVATAR_BY_ID: Record<string, string> = {
  keller:   "/portraits/p01.jpg",
  hofmann:  "/portraits/p02.jpg",
  koehler:  "/portraits/p03.jpg",
  hoffmann: "/portraits/p04.jpg",
  roth:     "/portraits/p05.jpg",
  frei:     "/portraits/p06.jpg",
  schaefer: "/portraits/p07.jpg",
  wagner:   "/portraits/p08.jpg",
  albrecht: "/portraits/p09.jpg",
  meier:    "/portraits/p10.jpg",
  brandt:   "/portraits/p11.jpg",
  fischer:  "/portraits/p12.jpg",
  werner:   "/portraits/p13.jpg",
  brunner:  "/portraits/p14.jpg",
  ebel:     "/portraits/p15.jpg",
  kuhn:     "/portraits/p16.jpg",
  voss:     "/portraits/p17.jpg",
  lange:    "/portraits/p18.jpg",
  sturm:    "/portraits/p02.jpg",
};

export function avatarFor(id: string): string | undefined {
  return AVATAR_BY_ID[id];
}

/** Initials fallback from a "Last, First" or "F. Last" display name. */
export function initialsFor(name: string): string {
  const cleaned = name.replace(/[.,]/g, "").trim();
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
