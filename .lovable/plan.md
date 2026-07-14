## Problem

The active anchor in `AnchorRow` can lag behind the section actually on screen. In the screenshot, "Squad" is filling the viewport but "Summary" is still bold.

Root cause is in `src/components/session/AnchorRow.tsx`:

- It uses `IntersectionObserver` with `rootMargin: "-120px 0px -60% 0px"`, which only fires when a section edge crosses a narrow band near the top of the viewport.
- Long sections (Summary, Squad) can fully span that band, so **no** entry is intersecting at a given scroll position — the observer callback isn't invoked and `active` stays on whatever it was last set to (Summary).
- It also only considers `isIntersecting` entries and picks the topmost; a section that is fully covering the viewport but whose top scrolled past the band is ignored.

## Fix

Rewrite the scroll-spy in `AnchorRow.tsx` to be position-based instead of intersection-band-based:

1. Track scroll via a `scroll` listener on `window` (passive) plus a `resize` listener, throttled with `requestAnimationFrame`.
2. Compute an anchor line at `sticky offset + small buffer` (≈ top 12 rem, matching `top-24` + AnchorRow height, roughly 140px).
3. For each section element, read `getBoundingClientRect().top`. The active section is the **last** one whose `top <= anchorLine` (i.e. the deepest section whose header has crossed the sticky strip). Fallback to the first section when none has crossed yet, and force the last section when the page is scrolled to the bottom (so short trailing sections still activate).
4. Run once on mount and after layout settles.
5. Keep existing keyboard, `aria-current`, smooth-scroll, and reduced-motion behavior unchanged.

No changes to markup, styling, copy deck, section IDs, `scroll-mt-36` offsets, or any other file.

## Acceptance

- Scrolling from top through Attention → Summary → Periods → Squad flips the bold label to match the section whose header just passed under the sticky strip, one at a time.
- Standing anywhere inside the Squad table shows "Squad" as active (fixes the screenshot).
- Scrolled fully to the page bottom, "Squad" remains active.
- Clicking a label still smooth-scrolls (respects `prefers-reduced-motion`) and activates that section.
- Keyboard focus ring, `aria-current`, and the neutral visual treatment are unchanged.

## Files touched

- `src/components/session/AnchorRow.tsx` (scroll-spy logic only)
