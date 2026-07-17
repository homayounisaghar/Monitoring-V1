/**
 * ST2 — Athlete portrait chip.
 * Circular avatar with initials fallback. Neutral chrome, no data hue.
 * Sizes align to the type scale row heights (sm=24 for table, md=28 for
 * denser chart rows if needed). Border uses the standard border token so
 * the disc reads on both card and inset surfaces.
 */
import { avatarFor, initialsFor } from "@/lib/avatars";

type Props = {
  id: string;
  name: string;
  size?: number;
  dimmed?: boolean;
};

export function AthleteAvatar({ id, name, size = 24, dimmed = false }: Props) {
  const url = avatarFor(id);
  const dim = dimmed ? 0.55 : 1;
  return (
    <span
      aria-hidden
      className="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full"
      style={{
        width: size,
        height: size,
        backgroundColor: "var(--color-slate-100)",
        border: "1px solid var(--color-border)",
        opacity: dim,
      }}
    >
      {url ? (
        <img
          src={url}
          alt=""
          width={size}
          height={size}
          loading="lazy"
          decoding="async"
          className="h-full w-full object-cover"
        />
      ) : (
        <span
          className="type-num"
          style={{
            fontSize: Math.round(size * 0.42),
            color: "var(--color-text-secondary)",
            fontWeight: 600,
            letterSpacing: 0,
          }}
        >
          {initialsFor(name)}
        </span>
      )}
    </span>
  );
}
