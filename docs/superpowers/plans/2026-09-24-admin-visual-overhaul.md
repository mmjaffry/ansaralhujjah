# Admin Panel Visual Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `admin/index.html` pleasant and legible to work in — proper contrast, a real spacing and type scale, scannable card rows, and a preview that shows the card as it will actually publish.

**Architecture:** Everything happens inside `admin/index.html`. The `<style>` block is rewritten against the same token scales the public site now uses. Two JavaScript functions change, both of which only draw admin UI: `renderSidebar()` (adds a state badge to each row) and `updatePreview()` (renders real `.program-card` markup instead of the stale `demo-card` shape). No publish, validation, sync, or undo function is touched.

**Tech Stack:** Static HTML, inline CSS custom properties, vanilla JS, Playwright (Node CLI + a small script) for browser verification.

**Spec:** `docs/superpowers/specs/2026-09-24-site-and-admin-refresh-design.md`

## Global Constraints

- Do not edit `publishToGitHub`, `runPublishTransaction`, `validateCardsHtml`, `validateQuranPageHtml`, `spliceMarkerRegion`, `softValidateLivePublish`, `syncFromLiveSite`, `parseLiveSite`, `readCardFromAnchor`, `findExistingFlyer`, `saveUndoSnapshot`, `getUndoSnapshot`, `undoLastPublish`, `buildCardHtml`, or `buildPinnedCardHtml`.
- Never click Save, Delete, Restore, or a move arrow while testing. Those publish to the live site immediately. Verification is limited to signing in, selecting cards, and typing in fields.
- `ADMIN_PASSWORD` and `GH_TOKEN` stay exactly as they are. Do not print the token into any screenshot, log, or commit.
- Admin tokens mirror the public ones where they overlap: `--text-muted: #6b3410`, `--bg-card: rgba(255,255,255,0.55)`, plus `--shadow-sm/md/lg`, `--sp-1`…`--sp-6`, `--fs-xs`…`--fs-2xl`, `--radius-sm/md/lg` with the same values as `index.html`.
- The panel must be usable at 390px wide.
- `PROJECT.md` and `CLAUDE.md` are updated in the same commit as the change they describe; stale wording is deleted, not appended to.

---

### Task 1: Token scales and base chrome

**Files:**
- Modify: `admin/index.html:15-25` (`:root`), `:27-33` (body), `:35-52` (login), `:54-84` (shared inputs/buttons), `:89-119` (topbar and status pill)
- Modify: `PROJECT.md` (Admin Panel section)

**Interfaces:**
- Consumes: nothing.
- Produces: the admin token set — `--bg`, `--bg-card`, `--bg-panel`, `--accent`, `--accent-light`, `--accent-dim`, `--accent-border`, `--accent-border-strong`, `--text`, `--text-muted`, `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--sp-1`…`--sp-6`, `--fs-xs`…`--fs-2xl`, `--radius-sm`, `--radius-md`, `--radius-lg`, `--focus-ring`. Tasks 2 and 3 consume these names.

- [ ] **Step 1: Write the sign-in screenshot script**

The admin panel needs a password before anything renders, so screenshots need a driver script rather than the `playwright screenshot` CLI. Create it in the scratchpad directory (not the repo):

```javascript
// shot-admin.js — usage: node shot-admin.js <width> <height> <outfile> [cardIndex]
const { chromium } = require('playwright');

(async () => {
  const [width, height, out, cardIndex] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +width, height: +height } });
  await page.goto('http://localhost:8765/admin/', { waitUntil: 'networkidle' });
  await page.fill('#passwordInput', process.env.AAH_ADMIN_PASSWORD);
  await page.click('#loginForm button[type="submit"]');
  await page.waitForSelector('#dashboard', { state: 'visible' });
  await page.waitForTimeout(1500); // let syncFromLiveSite finish
  if (cardIndex !== undefined) {
    await page.locator('.event-item').nth(+cardIndex).click();
    await page.waitForTimeout(400);
  }
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
})();
```

Run it with `NODE_PATH` pointed at the npx-installed Playwright, or from a scratchpad directory where `npm i playwright` has been run. The script must never click a save, delete, restore, or move control.

- [ ] **Step 2: Capture the baseline**

```bash
node shot-admin.js 1440 900 admin-baseline-desktop.png
node shot-admin.js 390 844 admin-baseline-mobile.png
node shot-admin.js 1440 900 admin-baseline-editor.png 0
```

Keep these for comparison at the end of Task 3.

- [ ] **Step 3: Replace the admin `:root` block**

`admin/index.html:15-25` currently reads:

```css
    :root {
      --bg:            #d9ccbc;
      --bg-card:       rgba(255,255,255,0.55);
      --bg-panel:      rgba(255,255,255,0.38);
      --accent:        rgb(148,62,12);
      --accent-light:  rgb(195,95,38);
      --accent-dim:    rgba(148,62,12,0.10);
      --accent-border: rgba(148,62,12,0.22);
      --text:          #1a0d05;
      --text-muted:    rgba(110,55,12,0.72);
    }
```

Replace with:

```css
    :root {
      --bg:            #d9ccbc;
      --bg-card:       rgba(255,255,255,0.55);
      --bg-panel:      rgba(255,255,255,0.38);
      --bg-field:      rgba(255,255,255,0.72);
      --accent:        rgb(148,62,12);
      --accent-light:  rgb(195,95,38);
      --accent-dim:    rgba(148,62,12,0.10);
      --accent-border: rgba(148,62,12,0.22);
      --accent-border-strong: rgba(148,62,12,0.45);
      --text:          #1a0d05;
      --text-muted:    #6b3410;
      --danger:        #8a1a1a;
      --success:       #1a5a1a;
      --shadow-sm: 0 1px 2px rgba(74,32,6,0.08), 0 1px 3px rgba(74,32,6,0.06);
      --shadow-md: 0 4px 12px rgba(74,32,6,0.10), 0 2px 4px rgba(74,32,6,0.06);
      --shadow-lg: 0 12px 32px rgba(74,32,6,0.16), 0 4px 8px rgba(74,32,6,0.08);
      --focus-ring: 0 0 0 3px rgba(148,62,12,0.22);
      --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px;
      --sp-4: 16px; --sp-5: 24px; --sp-6: 40px;
      --fs-xs: 0.75rem; --fs-sm: 0.85rem; --fs-md: 0.95rem;
      --fs-lg: 1.1rem;  --fs-xl: 1.4rem;  --fs-2xl: 1.9rem;
      --radius-sm: 8px; --radius-md: 12px; --radius-lg: 18px;
    }
```

- [ ] **Step 4: Give every interactive control a visible focus state**

The panel currently shows focus only as a border color change on `.field` and form inputs, and nothing at all on buttons — unusable from the keyboard. Add, immediately after the `:root` block:

```css
    :focus-visible { outline: none; box-shadow: var(--focus-ring); border-radius: var(--radius-sm); }
```

and change the two existing focus rules to include the ring:

```css
    .field:focus { border-color: var(--accent); box-shadow: var(--focus-ring); }
    .form-row input:focus, .form-row textarea:focus { border-color: var(--accent); box-shadow: var(--focus-ring); }
```

- [ ] **Step 5: Move the login card, buttons, and fields onto the scales**

Replace the hardcoded pixel and rem values in `.login-card`, `.field`, `.btn-primary`, `.btn-ghost`, and `.btn-secondary` with the token equivalents. Specifically:

```css
    .login-card {
      width: 100%; max-width: 380px; background: var(--bg-card);
      border: 1px solid var(--accent-border); border-radius: var(--radius-lg);
      padding: var(--sp-6) var(--sp-6) var(--sp-5); text-align: center;
      box-shadow: var(--shadow-lg);
    }
    .login-card h1 { font-family: 'Cinzel', serif; font-size: var(--fs-xl); font-weight: 400; color: var(--accent); margin-bottom: var(--sp-1); }
    .login-sub { font-size: var(--fs-xs); color: var(--text-muted); margin-bottom: var(--sp-5); }
    .login-error { margin-top: var(--sp-3); font-size: var(--fs-sm); color: var(--danger); display: none; }

    .field {
      width: 100%; background: var(--bg-field); border: 1px solid var(--accent-border);
      border-radius: var(--radius-md); padding: var(--sp-3) var(--sp-4); color: var(--text);
      font-family: 'Lato', sans-serif; font-size: var(--fs-md); outline: none;
      transition: border-color 0.2s, box-shadow 0.2s; margin-bottom: var(--sp-3);
    }

    .btn-primary {
      width: 100%; background: var(--accent); color: #fff; border: none;
      border-radius: var(--radius-md); padding: var(--sp-3) var(--sp-4);
      font-family: 'Cinzel', serif; font-size: var(--fs-sm); letter-spacing: 0.05em;
      cursor: pointer; box-shadow: var(--shadow-sm);
      transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
    }
    .btn-primary:hover  { background: var(--accent-light); transform: translateY(-1px); box-shadow: var(--shadow-md); }
    .btn-primary:active { transform: translateY(0); box-shadow: var(--shadow-sm); }
    .btn-primary:disabled { opacity: 0.5; cursor: default; transform: none; box-shadow: none; }

    .btn-ghost {
      background: var(--accent-dim); border: 1px solid var(--accent-border); color: var(--accent);
      border-radius: var(--radius-sm); padding: var(--sp-2) var(--sp-4); font-size: var(--fs-sm);
      cursor: pointer; transition: background 0.2s, border-color 0.2s; font-family: 'Lato', sans-serif;
    }
    .btn-ghost:hover { background: rgba(180,90,45,0.22); border-color: var(--accent-border-strong); }

    .btn-secondary {
      background: transparent; border: 1px solid var(--accent-border); color: var(--text-muted);
      border-radius: var(--radius-md); padding: var(--sp-3) var(--sp-5); font-family: 'Lato', sans-serif;
      font-size: var(--fs-sm); cursor: pointer; transition: border-color 0.2s, color 0.2s, background 0.2s;
    }
    .btn-secondary:hover { border-color: var(--accent-light); color: var(--text); background: rgba(255,255,255,0.35); }
```

`.btn-ghost`'s color changes from `--accent-light` to `--accent` because the lighter orange on the translucent panel was the weakest text on the page.

- [ ] **Step 6: Fix the topbar badge**

`.topbar-badge` uses `rgba(255,255,255,0.05)` background and `rgba(255,255,255,0.08)` border — values carried over from a dark theme, effectively invisible on beige. Replace:

```css
    .topbar-badge {
      font-size: var(--fs-xs); color: var(--accent); background: var(--accent-dim);
      border: 1px solid var(--accent-border); border-radius: var(--radius-sm);
      padding: 2px var(--sp-2); letter-spacing: 0.08em; text-transform: uppercase;
    }
```

Also give the topbar depth so it separates from the scrolling body:

```css
    .topbar {
      position: sticky; top: 0; z-index: 200; background: var(--bg-card);
      border-bottom: 1px solid var(--accent-border); padding: 0 var(--sp-5); height: 60px;
      display: flex; align-items: center; justify-content: space-between; gap: var(--sp-3);
      backdrop-filter: blur(8px); box-shadow: var(--shadow-sm);
    }
```

The `.admin-body` `min-height` calc must change from `calc(100vh - 56px)` to `calc(100vh - 60px)` to match the new topbar height.

- [ ] **Step 7: Verify**

```bash
node shot-admin.js 1440 900 admin-task1-desktop.png
```

Expected: the login screen and topbar read cleanly; the "Admin" badge is now visible; nothing overlaps; the sign-in still works (the script fails at `waitForSelector('#dashboard')` if it does not).

Confirm no protected function was touched:

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git diff admin/index.html | grep -E "^[-+].*(publishToGitHub|runPublishTransaction|validateCardsHtml|spliceMarkerRegion|syncFromLiveSite|parseLiveSite|readCardFromAnchor|findExistingFlyer|undoLastPublish|buildCardHtml|buildPinnedCardHtml)" | wc -l
```

Expected: `0`.

Also confirm no credential is in the diff:

```bash
git diff admin/index.html | grep -cE "^[-+].*(GH_TOKEN|ADMIN_PASSWORD)"
```

Expected: `0`.

- [ ] **Step 8: Update documentation and commit**

In `PROJECT.md`'s Admin Panel section, note that the panel carries its own token set mirroring the public scales, and that every control has a visible focus ring.

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git add admin/index.html PROJECT.md
git commit -m "$(cat <<'EOF'
Put the admin panel on the shared design scales

Spacing, type, and elevation were one-off values, the topbar badge used
leftover dark-theme colors that were invisible on beige, and buttons had
no focus state at all. Adopts the same token scales as the public site
and gives every control a visible focus ring.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Scannable card rows

**Files:**
- Modify: `admin/index.html:125-196` (sidebar CSS)
- Modify: `admin/index.html:855-915` (`renderSidebar()` — markup only)
- Modify: `PROJECT.md` (Admin Panel card management description)

**Interfaces:**
- Consumes: the token names from Task 1.
- Produces: an `.event-item` row containing `.event-thumb`, `.event-info` (with `.event-name`, `.event-sub`), a `.card-badge` element whose class is one of `card-badge--pinned` / `card-badge--event` / `card-badge--hidden`, and the existing `.move-btns` / `.btn-del` / `.btn-restore` controls. Task 3 does not depend on these.

- [ ] **Step 1: Add badge styles**

Append after the `.event-sub` rule:

```css
    .card-badge {
      font-size: 0.62rem; letter-spacing: 0.08em; text-transform: uppercase;
      padding: 2px var(--sp-2); border-radius: 999px; flex-shrink: 0;
      border: 1px solid transparent; white-space: nowrap;
    }
    .card-badge--pinned { background: var(--accent-dim); border-color: var(--accent-border); color: var(--accent); }
    .card-badge--event  { background: rgba(255,255,255,0.5); border-color: var(--accent-border); color: var(--text-muted); }
    .card-badge--hidden { background: rgba(138,26,26,0.10); border-color: rgba(138,26,26,0.30); color: var(--danger); }
```

- [ ] **Step 2: Loosen the rows**

Replace the `.event-item` and `.event-thumb` rules:

```css
    .event-item {
      display: flex; align-items: center; gap: var(--sp-3); background: var(--bg-card);
      border: 1px solid var(--accent-border); border-radius: var(--radius-md);
      padding: var(--sp-3); margin-bottom: var(--sp-2); cursor: pointer;
      transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
    }
    .event-item:hover  { border-color: var(--accent-border-strong); box-shadow: var(--shadow-sm); }
    .event-item.active { border-color: var(--accent); background: rgba(180,90,45,0.09); box-shadow: var(--shadow-sm); }
    .event-item.pinned-removed { opacity: 0.55; }

    .event-thumb {
      width: 40px; height: 40px; border-radius: var(--radius-sm); flex-shrink: 0;
      background: var(--accent-dim); display: flex; align-items: center; justify-content: center;
      font-size: var(--fs-md); overflow: hidden; border: 1px solid var(--accent-border);
    }
    .event-thumb svg { width: 18px; height: 18px; fill: var(--accent-light); }
    .event-name { font-size: var(--fs-sm); font-weight: 400; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .event-sub  { font-size: var(--fs-xs); color: var(--text-muted); margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
```

- [ ] **Step 3: Render the badges**

In `renderSidebar()`, each of the three returned templates gains a badge between `.event-info` and the trailing button. For the removed-pinned branch, replace the inline-styled sub line:

```html
          <div class="event-sub" style="color:#e07070;">Removed from site</div>
```

with a plain sub line plus a badge — the removed branch becomes:

```javascript
      if (pc.removed) {
        return `
      <div class="event-item pinned-removed" id="pinned-${id}">${moveBtns}
        <div class="event-thumb"><svg viewBox="0 0 24 24"><path d="${iconPath}"/></svg></div>
        <div class="event-info">
          <div class="event-name">${esc(pc.title)}</div>
          <div class="event-sub">Not shown on the site</div>
        </div>
        <span class="card-badge card-badge--hidden">Hidden</span>
        <button class="btn-restore" onclick="event.stopPropagation();restorePinned('${id}')" title="Restore">↺</button>
      </div>`;
      }
```

The visible pinned branch gains `<span class="card-badge card-badge--pinned">Pinned</span>` in the same position, and the event branch gains `<span class="card-badge card-badge--event">Event</span>`. Nothing else in the function changes — the `onclick` handlers, ids, and `applySyncingUI()` call stay exactly as they are.

- [ ] **Step 4: Verify**

```bash
node shot-admin.js 1440 900 admin-task2-desktop.png
```

Expected: each sidebar row shows thumbnail, title, subtitle, and a badge reading Pinned or Event; rows are taller and easier to hit; hidden pinned cards read "Hidden" in red rather than a red subtitle.

Confirm the handlers survived:

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
grep -c "openPinnedEditor\|openEditor\|removePinned\|restorePinned\|deleteCard\|moveCard" admin/index.html
git diff admin/index.html | grep -E "^[-+].*(publishToGitHub|runPublishTransaction|validateCardsHtml|syncFromLiveSite|parseLiveSite)" | wc -l
```

Expected: the second command prints `0`.

- [ ] **Step 5: Update documentation and commit**

In `PROJECT.md`, update the card management bullets to say each sidebar row shows a flyer thumbnail, title, subtitle, and a state badge (Pinned / Event / Hidden).

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git add admin/index.html PROJECT.md
git commit -m "$(cat <<'EOF'
Make admin card rows scannable

Rows were cramped and a hidden pinned card was signalled only by a red
subtitle. Loosens row spacing and adds an explicit Pinned / Event / Hidden
badge so card state is readable at a glance.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: A preview that matches what publishes

**Files:**
- Modify: `admin/index.html:275-291` (preview CSS)
- Modify: `admin/index.html:435-454` (preview markup)
- Modify: `admin/index.html:1120-1132` (`updatePreview()`)
- Modify: `admin/index.html:319-324` (responsive block)
- Modify: `PROJECT.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: tokens from Task 1.
- Produces: preview markup with ids `previewCard`, `previewFlyer`, `previewFlyerImg`, `previewFlyerIcon`, `previewIconPath`, `previewTitle`, `previewSub`. `updatePreview()` writes to exactly these.

- [ ] **Step 1: Replace the preview markup**

The current `demo-card` block renders a header row, a hidden body, and a "Register" button — a shape the site stopped publishing when cards became `.program-card`. Replace the `<div class="demo-card">…</div>` block at `admin/index.html:438-453` with markup mirroring the published card:

```html
          <div class="demo-card" id="previewCard">
            <div class="demo-flyer" id="previewFlyer">
              <img id="previewFlyerImg" src="" alt="">
              <svg id="previewFlyerIcon" viewBox="0 0 24 24"><path id="previewFlyerIconPath" d=""/></svg>
            </div>
            <div class="demo-info">
              <div class="demo-icon">
                <svg viewBox="0 0 24 24"><path id="previewIconPath" d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>
              </div>
              <div class="demo-text">
                <div class="demo-label" id="previewTitle">Event Title</div>
                <div class="demo-sub"   id="previewSub">Subtitle</div>
              </div>
              <div class="demo-arrow">→</div>
            </div>
          </div>
```

Note `previewIconPath` keeps its id and its default `d` so the existing `updatePreview()` line that sets it keeps working.

- [ ] **Step 2: Replace the preview CSS**

Replace the `.demo-*` rules with ones mirroring the published card, including its desktop row form:

```css
    .demo-card {
      background: var(--bg-card); border: 1px solid var(--accent-border);
      border-radius: var(--radius-lg); overflow: hidden; max-width: 560px;
      box-shadow: var(--shadow-sm);
    }
    .demo-flyer {
      background: rgba(148,62,12,0.06); min-height: 96px;
      display: flex; align-items: center; justify-content: center; padding: var(--sp-3);
    }
    .demo-flyer img { display: block; width: 75%; height: auto; }
    .demo-flyer svg { width: 40px; height: 40px; fill: var(--accent); opacity: 0.35; }
    .demo-info {
      display: flex; align-items: center; gap: var(--sp-4);
      padding: var(--sp-4) var(--sp-5); border-top: 1px solid var(--accent-border);
    }
    .demo-icon {
      width: 36px; height: 36px; border-radius: var(--radius-sm); background: var(--accent-dim);
      border: 1px solid var(--accent-border);
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .demo-icon svg { fill: var(--accent-light); width: 18px; height: 18px; }
    .demo-text { flex: 1; min-width: 0; }
    .demo-label { font-size: var(--fs-md); color: var(--text); }
    .demo-sub   { font-size: var(--fs-xs); color: var(--text-muted); margin-top: 2px; }
    .demo-arrow { color: var(--accent); font-size: var(--fs-md); flex-shrink: 0; }

    /* mirrors the homepage's 820px rule so the preview shows the desktop form */
    @media (min-width: 900px) {
      .demo-card { display: flex; align-items: stretch; }
      .demo-flyer { flex: 0 0 38%; max-width: 220px; }
      .demo-flyer img { width: 100%; height: 100%; max-height: 190px; object-fit: contain; }
      .demo-info { border-top: none; border-left: 1px solid var(--accent-border); }
    }
```

- [ ] **Step 3: Rewrite `updatePreview()`**

```javascript
function updatePreview() {
  document.getElementById('previewTitle').textContent = document.getElementById('fTitle').value || 'Event Title';
  const subEl = document.getElementById('previewSub');
  const subVal = document.getElementById('fSub').value;
  subEl.textContent = subVal;
  subEl.style.display = subVal ? 'block' : 'none';
  document.getElementById('previewIconPath').setAttribute('d', getIconPath(selectedIconId));
  document.getElementById('previewFlyerIconPath').setAttribute('d', getIconPath(selectedIconId));
  const img  = document.getElementById('previewFlyerImg');
  const icon = document.getElementById('previewFlyerIcon');
  if (flyerB64) {
    img.src = `data:${flyerMime};base64,${flyerB64}`;
    img.style.display = 'block';
    icon.style.display = 'none';
  } else {
    img.removeAttribute('src');
    img.style.display = 'none';
    icon.style.display = 'block';
  }
}
```

This mirrors the real card exactly: a card with no flyer publishes with the icon centered in the flyer area, and a card with no subtitle publishes with the `.btn-sub` span omitted.

- [ ] **Step 4: Update the responsive block**

Replace the `@media (max-width: 580px)` block so the panel works on a phone:

```css
    @media (max-width: 760px) {
      .admin-body { grid-template-columns: 1fr; }
      .sidebar { border-right: none; border-bottom: 1px solid var(--accent-border); max-height: 42vh; }
      .editor-wrap { padding: var(--sp-5) var(--sp-4); }
      .icon-picker { grid-template-columns: repeat(6, 1fr); }
      .topbar { padding: 0 var(--sp-4); }
      .topbar-brand { font-size: var(--fs-sm); }
      .form-actions { flex-direction: column-reverse; }
      .form-actions .btn-secondary, .form-actions .btn-primary { width: 100%; }
    }
```

`.form-actions` reverses on a phone so Save sits above Cancel, under the thumb.

- [ ] **Step 5: Verify against a real card**

```bash
node shot-admin.js 1440 900 admin-task3-editor.png 0
node shot-admin.js 390 844 admin-task3-mobile.png 0
```

Expected: selecting the first card (Quran Reflections, which has a flyer) shows a preview whose flyer, icon, title, subtitle, and arrow match the published homepage card. On the phone-width shot the sidebar sits above the editor, fields are full width, and Save is the lower, wider button.

Then compare the preview against the real thing: open `http://localhost:8765/` at 1440 and confirm the Quran Reflections card and the admin preview show the same composition.

- [ ] **Step 6: Confirm nothing protected changed across all three tasks**

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git diff main -- admin/index.html | grep -E "^[-+].*(publishToGitHub|runPublishTransaction|validateCardsHtml|validateQuranPageHtml|spliceMarkerRegion|softValidateLivePublish|syncFromLiveSite|parseLiveSite|readCardFromAnchor|findExistingFlyer|saveUndoSnapshot|undoLastPublish|buildCardHtml|buildPinnedCardHtml|GH_TOKEN|ADMIN_PASSWORD)" | wc -l
```

Expected: `0`.

- [ ] **Step 7: Update documentation and commit**

In `PROJECT.md`, replace the claim that each card "shows a live preview while editing" with a description of what the preview now is: the real published card markup, including the desktop row form, so what the editor sees is what the homepage renders.

In `CLAUDE.md`, add to the admin panel notes that `updatePreview()` renders the `.program-card` composition and must be updated whenever `buildCardHtml()` / `buildPinnedCardHtml()` change shape — the preview is a deliberate mirror of them, and the two drifting apart is what made the old `demo-card` misleading.

```bash
cd /Users/murtazajaffry/Desktop/Projects/ansaralhujjah
git add admin/index.html PROJECT.md CLAUDE.md
git commit -m "$(cat <<'EOF'
Show the real published card in the admin preview

The preview rendered a header/body/register shape the site stopped
publishing when cards became .program-card, so the editor showed
something the homepage would never produce. Rebuilds it from the real
card composition, including the desktop row form, and makes the panel
usable at phone width.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```
