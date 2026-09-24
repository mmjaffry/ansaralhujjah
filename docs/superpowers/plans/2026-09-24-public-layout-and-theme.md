# Public Layout and Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the homepage read well on a laptop by turning program cards into horizontal rows above 820px, and refine the shared warm palette for contrast and depth across every page.

**Architecture:** This is a CSS-only change to a static site. The homepage `<style>` block lives outside the `AAH-ALL-CARDS-START/END` markers, so card layout can change without touching the card markup the admin panel generates — the publish pipeline, its validators, and its DOM parsers are untouched. Design tokens are duplicated in four files; a single shared token block is pasted into all four and the two Python page builders are re-run so generated pages pick it up.

**Tech Stack:** Static HTML, inline CSS custom properties, Python 3 build scripts (`markdown`, `pyyaml`), Playwright MCP for browser verification.

**Spec:** `docs/superpowers/specs/2026-09-24-site-and-admin-refresh-design.md`

## Global Constraints

- No backend. Static HTML on GitHub Pages only.
- Do not edit `publishToGitHub`, `runPublishTransaction`, `validateCardsHtml`, `validateQuranPageHtml`, `spliceMarkerRegion`, `syncFromLiveSite`, `parseLiveSite`, `readCardFromAnchor`, `findExistingFlyer`, or the undo functions in `admin/index.html`.
- Do not change the card DOM produced by `buildCardHtml()` / `buildPinnedCardHtml()`. CSS only.
- `<!-- AAH-ALL-CARDS-START -->` / `<!-- AAH-ALL-CARDS-END -->` in `index.html` must each appear exactly once, with every `<!-- pinned:* -->` and `<!-- admin:* -->` comment intact and in the same order.
- `SESSIONS-START/END` and `QURAN-DESC-START/END` in `quran-reflections/index.html` must stay siblings, never nested.
- `--text-muted` must be `#6b3410` (contrast 6.27:1 against `#d9ccbc`, clears WCAG AA).
- Every change to the codebase updates `PROJECT.md` and `CLAUDE.md` in the same commit. Stale text is deleted, not appended to.
- Mobile rendering (below 820px) must be visually identical to the current site apart from the palette refinement.

---

### Task 1: Shared design token block

**Files:**
- Modify: `index.html:23-33` (`:root` block)
- Modify: `quran-reflections/index.html:23-31` (`:root` block)
- Modify: `build_notes.py:305-312` (`:root` block inside the page template — note doubled `{{ }}` braces, the `:root {{` / `}}` lines are f-string escapes and must stay doubled)
- Modify: `build_quran.py:156-164` (`:root` block inside the page template — single braces here, this template is not an f-string)
- Modify: `PROJECT.md` (design token table, lines ~224-232)
- Modify: `CLAUDE.md` (Design System section)

**Interfaces:**
- Consumes: nothing.
- Produces: the custom properties `--accent-light`, `--accent-mid`, `--accent-dark`, `--accent-glow`, `--bg`, `--bg-card`, `--bg-card-hover`, `--border`, `--border-strong`, `--text`, `--text-muted`, `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--sp-1`…`--sp-6`, `--fs-xs`…`--fs-2xl`, `--radius-sm`, `--radius-md`, `--radius-lg`. Task 2 and all later sub-projects consume these names.

- [ ] **Step 1: Record the current rendering as a baseline**

Start a local server from the repo root and screenshot the homepage so the palette change can be compared against something.

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
python3 -m http.server 8765 &
```

Then with the Playwright MCP browser: navigate to `http://localhost:8765/`, resize to 1440x900, screenshot. Keep the screenshot for comparison in Step 7.

- [ ] **Step 2: Replace the `:root` block in `index.html`**

The homepage `:root` currently reads:

```css
    :root {
      --accent-light: rgb(195,95,38);
      --accent-mid: rgb(148,62,12);
      --accent-dark: rgb(98,28,0);
      --accent-glow: rgb(210,112,50);
      --bg: #d9ccbc;
      --bg-card: rgba(255,255,255,0.48);
      --bg-card-hover: rgba(255,255,255,0.70);
      --text: #1a0d05;
      --text-muted: rgba(110,55,12,0.72);
    }
```

Replace it with:

```css
    :root {
      --accent-light: rgb(195,95,38);
      --accent-mid: rgb(148,62,12);
      --accent-dark: rgb(98,28,0);
      --accent-glow: rgb(210,112,50);
      --bg: #d9ccbc;
      --bg-card: rgba(255,255,255,0.55);
      --bg-card-hover: rgba(255,255,255,0.74);
      --border: rgba(148,62,12,0.18);
      --border-strong: rgba(148,62,12,0.42);
      --text: #1a0d05;
      --text-muted: #6b3410;
      --shadow-sm: 0 1px 2px rgba(74,32,6,0.08), 0 1px 3px rgba(74,32,6,0.06);
      --shadow-md: 0 4px 12px rgba(74,32,6,0.10), 0 2px 4px rgba(74,32,6,0.06);
      --shadow-lg: 0 12px 32px rgba(74,32,6,0.16), 0 4px 8px rgba(74,32,6,0.08);
      --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px;
      --sp-4: 16px; --sp-5: 24px; --sp-6: 40px;
      --fs-xs: 0.75rem; --fs-sm: 0.85rem; --fs-md: 0.95rem;
      --fs-lg: 1.1rem;  --fs-xl: 1.4rem;  --fs-2xl: 1.9rem;
      --radius-sm: 8px; --radius-md: 12px; --radius-lg: 18px;
    }
```

- [ ] **Step 3: Replace the `:root` block in `quran-reflections/index.html`**

Its current block is the aligned-colon variant:

```css
    :root {
      --accent-light: rgb(195,95,38);
      --accent-mid:   rgb(148,62,12);
      --accent-dark:  rgb(98,28,0);
      --bg:           #d9ccbc;
      --bg-card:      rgba(255,255,255,0.48);
      --text:         #1a0d05;
      --text-muted:   rgba(110,55,12,0.72);
    }
```

Replace with the same token set as Step 2 (aligned formatting is fine, values must match exactly):

```css
    :root {
      --accent-light: rgb(195,95,38);
      --accent-mid:   rgb(148,62,12);
      --accent-dark:  rgb(98,28,0);
      --accent-glow:  rgb(210,112,50);
      --bg:           #d9ccbc;
      --bg-card:      rgba(255,255,255,0.55);
      --bg-card-hover: rgba(255,255,255,0.74);
      --border:       rgba(148,62,12,0.18);
      --border-strong: rgba(148,62,12,0.42);
      --text:         #1a0d05;
      --text-muted:   #6b3410;
      --shadow-sm: 0 1px 2px rgba(74,32,6,0.08), 0 1px 3px rgba(74,32,6,0.06);
      --shadow-md: 0 4px 12px rgba(74,32,6,0.10), 0 2px 4px rgba(74,32,6,0.06);
      --shadow-lg: 0 12px 32px rgba(74,32,6,0.16), 0 4px 8px rgba(74,32,6,0.08);
      --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px;
      --sp-4: 16px; --sp-5: 24px; --sp-6: 40px;
      --fs-xs: 0.75rem; --fs-sm: 0.85rem; --fs-md: 0.95rem;
      --fs-lg: 1.1rem;  --fs-xl: 1.4rem;  --fs-2xl: 1.9rem;
      --radius-sm: 8px; --radius-md: 12px; --radius-lg: 18px;
    }
```

- [ ] **Step 4: Replace the `:root` block in `build_notes.py`**

This template is an f-string: literal braces are doubled. Use exactly the Step 3 block but with `:root {{` opening and `}}` closing:

```python
    :root {{
      --accent-light: rgb(195,95,38);
      --accent-mid:   rgb(148,62,12);
      --accent-dark:  rgb(98,28,0);
      --accent-glow:  rgb(210,112,50);
      --bg:           #d9ccbc;
      --bg-card:      rgba(255,255,255,0.55);
      --bg-card-hover: rgba(255,255,255,0.74);
      --border:       rgba(148,62,12,0.18);
      --border-strong: rgba(148,62,12,0.42);
      --text:         #1a0d05;
      --text-muted:   #6b3410;
      --shadow-sm: 0 1px 2px rgba(74,32,6,0.08), 0 1px 3px rgba(74,32,6,0.06);
      --shadow-md: 0 4px 12px rgba(74,32,6,0.10), 0 2px 4px rgba(74,32,6,0.06);
      --shadow-lg: 0 12px 32px rgba(74,32,6,0.16), 0 4px 8px rgba(74,32,6,0.08);
      --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px;
      --sp-4: 16px; --sp-5: 24px; --sp-6: 40px;
      --fs-xs: 0.75rem; --fs-sm: 0.85rem; --fs-md: 0.95rem;
      --fs-lg: 1.1rem;  --fs-xl: 1.4rem;  --fs-2xl: 1.9rem;
      --radius-sm: 8px; --radius-md: 12px; --radius-lg: 18px;
    }}
```

- [ ] **Step 5: Replace the `:root` block in `build_quran.py`**

Same values, single braces (this template is not an f-string) — identical text to Step 3.

- [ ] **Step 6: Rebuild generated pages and verify the token reached them**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
python3 build_notes.py && python3 build_quran.py
```

Expected: both scripts exit 0. If `build_notes.py` raises `KeyError` or `ValueError: Single '}' encountered`, a brace in Step 4 was not doubled — fix it before continuing.

Then assert the new token is present everywhere and the old one is gone:

```bash
grep -rl "text-muted:   #6b3410\|text-muted: #6b3410" index.html quran-reflections/index.html build_notes.py build_quran.py | wc -l
grep -rn "rgba(110,55,12,0.72)" . --include=*.html --include=*.py | wc -l
```

Expected: first command prints `4`, second prints `0`.

- [ ] **Step 7: Verify the marker contract survived and the page still renders**

```bash
grep -c "AAH-ALL-CARDS-START" index.html
grep -c "AAH-ALL-CARDS-END" index.html
grep -c "SESSIONS-START" quran-reflections/index.html
grep -c "QURAN-DESC-START" quran-reflections/index.html
```

Expected: `1` from each.

Confirm the two regions in `quran-reflections/index.html` are still siblings, not nested:

```bash
grep -n "SESSIONS-START\|SESSIONS-END\|QURAN-DESC-START\|QURAN-DESC-END" quran-reflections/index.html
```

Expected: the START/END pair of one region must both appear before or both after the pair of the other — never interleaved.

With the Playwright MCP browser, reload `http://localhost:8765/` at 1440x900 and screenshot. Compare against Step 1: colors slightly deeper, subtitles more readable, layout otherwise identical. Also load `http://localhost:8765/quran-reflections/` and one session page and confirm they render with no unstyled or broken sections.

- [ ] **Step 8: Update documentation**

In `PROJECT.md`, replace the design token table with one listing every token from Step 2, including the shadow, spacing, type, and radius scales. Delete the stale `--text-muted | rgba(110,55,12,0.72)` row rather than leaving it alongside the new value.

In `CLAUDE.md`, update the Design System section so it names the shared token block and states that it is duplicated in four files (`index.html`, `quran-reflections/index.html`, `build_notes.py`, `build_quran.py`) and that a change to one requires the same change to all four plus a re-run of both build scripts.

- [ ] **Step 9: Commit**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git add index.html quran-reflections/index.html build_notes.py build_quran.py PROJECT.md CLAUDE.md quran-reflections quran
git status
git commit -m "$(cat <<'EOF'
Refine shared design tokens for contrast and depth

Subtitle text failed contrast against the beige background, and elevation
and spacing were one-off values repeated across four files. Adds an opaque
muted text color plus shadow, spacing, type, and radius scales, applied to
every template that carries the token block.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

Review `git status` output before committing — the build scripts regenerate many pages under `quran-reflections/` and `quran/`, and all of them belong in this commit.

---

### Task 2: Horizontal program cards on desktop

**Files:**
- Modify: `index.html:42` (`.container` max-width)
- Modify: `index.html:95-127` (program card CSS block)
- Modify: `PROJECT.md` (Card Rendering section)
- Modify: `CLAUDE.md` (Card System section)

**Interfaces:**
- Consumes: the token names produced by Task 1 (`--border`, `--shadow-md`, `--sp-*`, `--radius-lg`).
- Produces: a `.program-card` that is a vertical stack below 820px and a flex row at or above it. The card DOM is unchanged, so `readCardFromAnchor()` keeps finding `.btn-label`, `.btn-sub`, `[href]`, and `.icon path[d]`.

- [ ] **Step 1: Capture the current mobile rendering as the regression baseline**

With the Playwright MCP browser against `http://localhost:8765/`, resize to 390x844 and screenshot. Mobile must look the same at the end of this task.

- [ ] **Step 2: Widen the container**

`index.html:42` currently reads:

```css
    .container { width: 100%; max-width: 520px; display: flex; flex-direction: column; align-items: center; }
```

Replace with:

```css
    .container { width: 100%; max-width: 520px; display: flex; flex-direction: column; align-items: center; }
    @media (min-width: 820px) { .container { max-width: 960px; } }
```

- [ ] **Step 3: Move the existing card rules onto the token scale**

In the `/* ── Program cards (admin-managed) ── */` block, replace the hardcoded values with tokens. `.program-card` becomes:

```css
    .program-card {
      display: block; width: 100%; text-decoration: none; color: var(--text);
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius-lg); overflow: hidden;
      box-shadow: var(--shadow-sm);
      transition: border-color 0.2s, transform 0.2s, box-shadow 0.25s, background 0.25s;
      animation: fadeUp 0.6s ease both;
    }
    .program-card:hover {
      border-color: var(--border-strong); background: var(--bg-card-hover);
      transform: translateY(-2px); box-shadow: var(--shadow-md);
    }
```

and `.program-card-info` becomes:

```css
    .program-card-info {
      display: flex; align-items: center; gap: var(--sp-4); padding: var(--sp-4) var(--sp-5);
      border-top: 1px solid var(--border);
    }
```

Leave `.program-card-flyer`, `.program-card-flyer img`, the `:not(:has(img))` rule, and the `.icon` / `.arrow` rules as they are — the desktop overrides in Step 4 handle them.

- [ ] **Step 4: Add the desktop horizontal layout**

Append this media query immediately after the program card block, before the `/* ── Social float icons ── */` comment:

```css
    @media (min-width: 820px) {
      .program-card { display: flex; align-items: stretch; }
      .program-card-flyer {
        flex: 0 0 38%; max-width: 320px;
        display: flex; align-items: center; justify-content: center;
        padding: var(--sp-3);
      }
      .program-card-flyer img { width: 100%; height: 100%; max-height: 260px; object-fit: contain; }
      .program-card-flyer:not(:has(img)) { min-height: 160px; }
      .program-card-info {
        flex: 1; border-top: none; border-left: 1px solid var(--border);
        padding: var(--sp-5) var(--sp-6);
      }
      .program-card-info .btn-label { font-size: var(--fs-lg); }
      .program-card-info .btn-sub { font-size: var(--fs-sm); }
    }
```

`object-fit: contain` is deliberate — flyers are text-heavy posters and must never be cropped.

- [ ] **Step 5: Verify desktop layout**

With the Playwright MCP browser: reload `http://localhost:8765/`, resize to 1440x900, screenshot.

Expected: each card is a single horizontal row — flyer on the left at roughly a third of the card width, icon + title + subtitle vertically centered to its right, arrow at the far right. The Quran Reflections flyer is fully visible, not cropped. Cards span a noticeably wider column than before.

Also check 1024x768 (just above the breakpoint) and 800x900 (just below) to confirm the switch happens cleanly with no overlap at either side.

- [ ] **Step 6: Verify mobile is unregressed**

Resize to 390x844, reload, screenshot. Compare against the Step 1 baseline: the layout must be the same stacked flyer-above-info card, with only the Task 1 palette difference visible.

- [ ] **Step 7: Verify the publish contract is untouched**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git diff --stat
grep -c "AAH-ALL-CARDS-START\|AAH-ALL-CARDS-END" index.html
grep -c "program-card" index.html
```

Expected: `git diff --stat` shows `index.html`, `PROJECT.md`, and `CLAUDE.md` only. The marker grep prints `2`. The `program-card` count is unchanged from before this task — run `git stash` / `git stash pop` around the count if a before-value is needed.

Confirm no card markup moved: `git diff index.html` must show changes only inside the `<style>` block, with zero lines changed between `AAH-ALL-CARDS-START` and `AAH-ALL-CARDS-END`.

- [ ] **Step 8: Update documentation**

In `PROJECT.md`, rewrite the Card Rendering section: cards are a stacked flyer-above-info block below 820px and a horizontal flyer-left row at or above it; flyers use `object-fit: contain` and are never cropped; the homepage container widens to 960px on desktop. Delete the current wording that describes only the stacked form.

In `CLAUDE.md`, add to the Card System section that the desktop horizontal form is pure CSS in the homepage `<style>` block, that the card DOM generated by `buildCardHtml()` / `buildPinnedCardHtml()` is identical at every width, and that this is why the change required no admin-panel edits.

- [ ] **Step 9: Commit**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git add index.html PROJECT.md CLAUDE.md
git commit -m "$(cat <<'EOF'
Lay program cards out horizontally on desktop

The single 520px column left most of a laptop screen empty and shrank
flyers unnecessarily. Widens the container and flips cards to a
flyer-left row above 820px. Card markup is unchanged, so the admin
publish pipeline and its parsers are unaffected.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 10: Stop the local server**

```bash
pkill -f "http.server 8765"
```

---

## Deferred to their own plans

Sub-project 2 (admin panel visual overhaul) and sub-project 3 (booking page) are separate plans, written after this one lands — both consume the token block Task 1 produces, so their code is written against the final values rather than predicted ones.
