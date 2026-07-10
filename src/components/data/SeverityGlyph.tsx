import { copy } from "@/lib/copy-deck";
/**
 * SeverityGlyph — two named tiers, always glyph + word.
 * Exists only inside the Attention card.
 */
export type SeverityTier = "escalate" | "notice";

export function SeverityGlyph({
  tier,
  size = "default",
}: {
  tier: SeverityTier;
  size?: "default" | "compact";
}) {
  const compact = size === "compact";
  const dim = compact ? 9 : 10;
  const pad = compact ? "gap-1 px-1.5 py-0.5" : "gap-1.5 px-1.5 py-0.5";
  if (tier === "escalate") {
    return (
      <span
        className={`inline-flex items-center ${pad} rounded type-micro`}
        style={{
          backgroundColor: "var(--color-escalate-surface)",
          color: "var(--color-escalate-ink)",
        }}
      >
        <svg width={dim} height={dim} viewBox="0 0 10 10" aria-hidden>
          <polygon points="5,1 9.5,9 0.5,9" fill="currentColor" />
        </svg>
        escalate
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center ${pad} rounded type-micro`}
      style={{
        backgroundColor: "var(--color-notice-surface)",
        color: "var(--color-notice-ink)",
      }}
    >
      <svg width={dim} height={dim} viewBox="0 0 10 10" aria-hidden>
        <polygon points="5,1 9,5 5,9 1,5" fill="currentColor" />
      </svg>
      notice
    </span>
  );
}
