/**
 * ST2 — ScopeTag (C4 scope expression, single source).
 *
 * Right-aligned tag that declares a section's scope while any filter is
 * active. Two forms in the existing chip dress (type-num 11px, tertiary):
 *
 *   filter active, full=false  →  "{showingCount} of {total}"
 *   filter active, full=true   →  copy("scope.unscopedTag")
 *   filterIsDefault            →  render nothing
 *
 * Attention does NOT consume this — its triage is squad-wide always.
 */
import { useSessionScope } from "@/lib/session-scope";
import { participants } from "@/lib/session-data";
import { copy } from "@/lib/copy-deck";

export function ScopeTag({ full = false }: { full?: boolean }) {
  const { filterIsDefault, showingCount } = useSessionScope();
  if (filterIsDefault) return null;
  const total = participants.length; // "of 18" invariant
  return (
    <span
      className="type-num text-[11px]"
      style={{ color: "var(--color-text-tertiary)" }}
    >
      {full ? copy("scope.unscopedTag") : `${showingCount} of ${total}`}
    </span>
  );
}
