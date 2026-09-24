# Scholar Booking Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let visitors book time with a scholar from `/book`, backed by Calendly, with a clear "not open yet" state until real Calendly links exist.

**Architecture:** A new static page, `book/index.html`, in the homepage font stack and design tokens. A `SCHOLARS` array at the top of its script drives everything: entries with an empty `calendlyUrl` render an explanatory placeholder, entries with a real URL render Calendly's inline embed. One scholar renders the embed directly; more than one renders a picker above it. The homepage gains a permanent `book` pinned card, seeded directly into `index.html` so it is live immediately and the admin panel picks it up on its next sync.

**Tech Stack:** Static HTML, inline CSS custom properties, vanilla JS, Calendly inline embed widget (`assets.calendly.com`).

**Spec:** `docs/superpowers/specs/2026-09-24-site-and-admin-refresh-design.md`

## Global Constraints

- No backend. Calendly is the only third-party dependency this page may add.
- The page must render a usable, non-broken state when no scholar has a real Calendly URL — that is the state it ships in.
- The seeded homepage card must match `buildPinnedCardHtml()`'s output shape exactly, or the admin's `readCardFromAnchor()` will read it back wrong.
- Do not edit any publish, validation, sync, or undo function in `admin/index.html`. The only admin change is adding `book` to `PINNED_KEYS` and `PINNED_DEFAULTS`.
- `<!-- AAH-ALL-CARDS-START -->` / `<!-- AAH-ALL-CARDS-END -->` must each still appear exactly once, with one `<!-- pinned:* -->` comment per card.
- `PROJECT.md` and `CLAUDE.md` are updated in the same commit.

---

### Task 1: The booking page

**Files:**
- Create: `book/index.html`

**Interfaces:**
- Produces: `SCHOLARS`, an array of `{ id: string, name: string, role: string, calendlyUrl: string }`. An entry whose `calendlyUrl` is `''` is treated as not yet bookable. Task 2 does not consume this.

- [ ] **Step 1: Write the page**

Create `book/index.html` with the homepage `<head>` (Cinzel + Lato, favicons, manifest) and the shared token block, then this body structure: page heading, a scholar list, and an embed region.

```javascript
const SCHOLARS = [
  {
    id: 'farhat-abbas',
    name: 'Molana Farhat Abbas',
    role: 'Resident scholar · Quran Reflections',
    // Paste the Calendly event link here, e.g. 'https://calendly.com/your-name/30min'
    calendlyUrl: ''
  }
];
```

Rendering rules:

- If no scholar has a `calendlyUrl`, render a single panel: a short line saying scheduling is not open yet, and a WhatsApp link to reach the community in the meantime. No Calendly script is loaded.
- If exactly one scholar has a `calendlyUrl`, render that scholar's name and role above a Calendly inline embed.
- If more than one does, render a row of scholar buttons; clicking one swaps the embed.
- Scholars with an empty `calendlyUrl` still appear in the list, marked "Booking opens soon" and not clickable.

Load the widget only when at least one real URL exists:

```javascript
function loadCalendly(cb) {
  if (window.Calendly) return cb();
  const s = document.createElement('script');
  s.src = 'https://assets.calendly.com/assets/external/widget.js';
  s.onload = cb;
  document.head.appendChild(s);
}
```

and mount with `Calendly.initInlineWidget({ url, parentElement, prefill: {}, utm: {} })`.

- [ ] **Step 2: Verify both states**

Serve locally and load `http://localhost:8765/book/`. With `calendlyUrl: ''` (the shipping state) confirm the placeholder panel renders, no request to `assets.calendly.com` is attempted, and there is no console error. Then temporarily set a real-looking URL, reload, and confirm the embed container mounts — revert to `''` before committing.

Screenshot at 1440x900 and 390x844 and confirm both read well.

- [ ] **Step 3: Commit**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git add book/index.html
git commit -m "$(cat <<'EOF'
Add a scholar booking page

Visitors had no way to request time with a scholar. Adds /book, driven by
a SCHOLARS array: entries without a Calendly link render an explanatory
panel and load no third-party script, so the page ships usable before any
scholar has an account.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Homepage card and admin pinned key

**Files:**
- Modify: `index.html` (one new card inside the `AAH-ALL-CARDS` region)
- Modify: `admin/index.html` (`PINNED_KEYS`, `PINNED_DEFAULTS`)
- Modify: `PROJECT.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: `/book/` from Task 1.
- Produces: the pinned key `book`, readable by `parseLiveSite()` through its `<!-- pinned:book -->` marker.

- [ ] **Step 1: Add the key to the admin panel**

`PINNED_KEYS` becomes:

```javascript
const PINNED_KEYS = ['sisters', 'quran', 'book', 'whatsapp', 'instagram'];
```

and `PINNED_DEFAULTS` gains:

```javascript
  book: {
    title: 'Book Time with a Scholar',
    sub:   'Schedule a one-on-one conversation',
    link:  '/book',
    iconId: 'calendar',
    removed: false,
  },
```

Use an `iconId` that exists in the `ICONS` array — check with `grep -o "id: '[a-z-]*'" admin/index.html` before choosing.

- [ ] **Step 2: Seed the card into the homepage**

Without this, `syncFromLiveSite()` sets `removed: true` for `book` (it derives removed state from the live HTML), and the card would sit hidden in the admin until someone clicked Restore. Insert the card inside the `AAH-ALL-CARDS` region, after the quran card, matching `buildPinnedCardHtml()`'s output exactly: a `<!-- pinned:book -->` comment, then an `<a class="program-card" href="/book">` with a `.program-card-flyer` holding the icon SVG, and a `.program-card-info` holding `.icon`, `.btn-text` (with `.btn-label` and `.btn-sub`), and `.arrow`.

The card links internally, so it takes no `target="_blank"` — check what `buildPinnedCardHtml()` emits for `/quran-reflections` and match that exactly.

- [ ] **Step 3: Verify the markers and the round trip**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
grep -c "AAH-ALL-CARDS-START" index.html
grep -c "pinned:" index.html
```

Expected: `1` and `4`.

Then run the admin screenshot script from the previous plan and confirm the sidebar lists Book Time with a Scholar as **Pinned**, not Hidden — that proves `parseLiveSite()` read the seeded card correctly. Do not click Save.

Load `http://localhost:8765/` at 1440 and 390 and confirm the new card renders in both layouts.

- [ ] **Step 4: Update documentation and commit**

`PROJECT.md`: add `book` to the pinned card list, describe `/book` and the `SCHOLARS` array, and state plainly how to switch it on — paste the Calendly link into the entry's `calendlyUrl`.

`CLAUDE.md`: note `book` in `PINNED_KEYS`, the page's location, and that the card was seeded into `index.html` by hand because `syncFromLiveSite()` derives `removed` from the live HTML, so a new pinned key that is absent from the published page syncs as removed.

```bash
git add index.html admin/index.html PROJECT.md CLAUDE.md
git commit -m "$(cat <<'EOF'
Add a permanent Book a Scholar card to the homepage

Makes /book reachable from the homepage and editable from the admin panel
as a pinned card. The card is seeded into index.html directly because
syncFromLiveSite derives a pinned card's removed state from the published
HTML — a new key absent from the live page would sync as hidden.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```
