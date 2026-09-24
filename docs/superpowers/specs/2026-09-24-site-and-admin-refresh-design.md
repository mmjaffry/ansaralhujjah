# Site and Admin Refresh — Design

Date: 2026-09-24

## Goal

Three independent improvements to the Ansar Al-Hujjah site:

1. Public homepage reads well on a laptop (cards become horizontal rows) and the warm palette is refined for contrast and depth.
2. The admin panel looks and reads better — a visual pass only, no changes to publishing logic.
3. Visitors can book time with a scholar through a new `/book` page backed by Calendly.

Each sub-project ships as its own commit with its own documentation update.

## Constraints

- The site is static HTML on GitHub Pages. There is no backend and none will be added.
- `admin/index.html` generates the card markup published into `index.html`. Any change to card *markup* forces a coordinated change in both files; a change to card *CSS* does not, because the homepage `<style>` block lives outside the `AAH-ALL-CARDS-START/END` markers.
- The publish pipeline (`publishToGitHub`, `runPublishTransaction`, `validateCardsHtml`, `syncFromLiveSite`, undo) has broken production twice in the past. It is out of scope for this work and must not be edited.
- `SESSIONS-START/END` and `QURAN-DESC-START/END` in `quran-reflections/index.html` must remain sibling, non-overlapping regions.
- Design tokens are duplicated across four places: `index.html`, `quran-reflections/index.html`, the page template in `build_notes.py`, and the page template in `build_quran.py`. A palette change must be applied to all four or pages will visibly diverge.

---

## Sub-project 1 — Public layout and theme

### Horizontal cards on desktop

`index.html` only. Two changes:

- `.container` grows from a fixed `max-width: 520px` to `max-width: 960px`, keeping the existing full-width behavior below that.
- A `@media (min-width: 820px)` block restyles `.program-card` as a flex row: the `.program-card-flyer` becomes the left column (flex-basis ~38%, max 320px, image scaled to fit), `.program-card-info` becomes the right column, vertically centered, with the arrow pushed to the far right.

Below 820px every card renders exactly as it does today — stacked flyer above an info row. The card DOM is untouched, so `readCardFromAnchor()`, `findExistingFlyer()`, and `parseLiveSite()` keep working against the same selectors.

The `.program-card-flyer img { width: 75% }` rule is replaced with `width: 100%` inside the desktop media query so the flyer fills its column; the mobile rule stays as-is.

### Palette refinement

Keep the terracotta-on-beige identity. Correct the specific weaknesses:

- `--text-muted: rgba(110,55,12,0.72)` fails contrast against `#d9ccbc` at small sizes. It becomes the opaque `#6b3410`, verified at 4.5:1 or better against the page background before the change is kept.
- Introduce a three-step elevation scale (`--shadow-sm`, `--shadow-md`, `--shadow-lg`) replacing the one-off `box-shadow` values currently scattered through the CSS.
- Introduce a spacing scale (`--sp-1` through `--sp-6`, 4px-based) and a type scale (`--fs-xs` through `--fs-2xl`) as custom properties so future edits are consistent.
- Refine the glassmorphism card background so borders read at both card sizes.

The updated token block is applied identically to `index.html`, `quran-reflections/index.html`, `build_notes.py`, and `build_quran.py`. Both Python scripts are re-run so the generated pages carry the new tokens.

### Verification

Serve locally with `python3 -m http.server`, then view the homepage at 390px and 1440px widths. Confirm: mobile layout unchanged; desktop cards are horizontal; flyers are not distorted; the `AAH-ALL-CARDS-START/END` markers and every `pinned:`/`admin:` comment are still present and in order.

---

## Sub-project 2 — Admin panel visual overhaul

Scope is the `<style>` block in `admin/index.html`, plus the preview markup. No JavaScript behavior changes.

- Rebuild the panel's CSS on an explicit spacing and type scale. Improve form field affordance, focus states, label hierarchy, and sidebar row density.
- Sidebar card rows show a flyer thumbnail alongside the title and state (pinned / hidden / event), so the list is scannable.
- The panel becomes usable at phone width — the sidebar collapses above the editor rather than sitting beside it.
- Replace the `demo-card` preview markup. It currently renders a shape (`demo-card-header`, `demo-body`, `demo-register`) that no longer matches the published `.program-card` format, so the preview misleads. It is rewritten to render the real card markup with the real card CSS, including the horizontal desktop form from sub-project 1.

`updatePreview()` is the one function that changes, and only because the element ids it writes into change. Every other function is untouched.

### Verification

Open `admin/index.html` locally, sign in, and confirm: card list renders, selecting a card populates the editor, the preview matches what the homepage shows, and the panel is usable at 390px. Do not trigger a publish during visual testing.

---

## Sub-project 3 — Booking page

New file `book/index.html`, using the homepage font stack from `_head.html` and the refreshed tokens.

- A `SCHOLARS` array at the top of the page's script holds `{ name, title, calendlyUrl }` entries. Until real Calendly accounts exist, entries carry placeholder URLs and the page shows a clearly worded "booking opens soon" state rather than a broken widget.
- With one scholar configured, the page renders that scholar's Calendly inline embed directly. With more than one, it renders a scholar picker above the embed.
- The Calendly inline embed script is loaded from `assets.calendly.com`. This is the only third-party dependency the page adds.
- `book` is added to `PINNED_KEYS` and `PINNED_DEFAULTS` in `admin/index.html` so "Book time with a scholar" becomes a permanent, admin-editable homepage card pointing at `/book`. Per the existing design, every other reference to pinned cards reads from `PINNED_KEYS`, so no other code changes.

Swapping a placeholder for a real Calendly link is a one-line edit per scholar in `book/index.html`.

### Verification

Serve locally and load `/book/` at both widths. Confirm the placeholder state renders when no real URL is set, and that adding a real URL renders the embed. Confirm the new pinned card appears in the admin sidebar without disturbing existing cards.

---

## Documentation

`PROJECT.md` and `CLAUDE.md` are updated with each sub-project's commit, not batched at the end. Stale content is deleted rather than appended to — specifically, any description of card rendering, the design token table, the admin preview, and the pinned card list must describe only the post-change state.

## Out of scope

- Any change to the publish transaction, validation, sync, or undo logic.
- A backend, serverless function, or database of any kind.
- Restructuring the session note build scripts beyond their token blocks.
- A dark theme.
