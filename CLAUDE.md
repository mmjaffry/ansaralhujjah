# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static site for Ansar Al-Hujjah Islamic community center in Houston, TX. Hosted on GitHub Pages at ansaralhujjah.org. Zero build tools — pure HTML/CSS/vanilla JS.

## Deployment

There is no build step. Changes go live by pushing to `main`:

```bash
git push origin main
```

GitHub Pages auto-deploys on push. No CI/CD pipeline.

## Architecture

Two HTML files form the entire application:

**`index.html`** — Public site. Contains all CSS and JS inline. Event cards are injected between HTML comment markers:
- `<!-- AAH-ALL-CARDS-START -->` / `<!-- AAH-ALL-CARDS-END -->` — surrounds all cards
- `<!-- admin:{cardId} -->` — per-card markers used during sync

**`admin/index.html`** — Admin panel SPA. Manages event cards and publishes to GitHub directly from the browser using the Git Data API. Auth is SHA-256 password (client-side). GitHub token is hardcoded as a split string to avoid accidental scanning.

### Publishing Flow

Admin edits cards → clicks Publish → JS fetches `index.html` from GitHub, injects new card HTML between the comment markers, creates a new blob/tree/commit via GitHub Git Data API, and force-pushes. Uses Git Data API (not Contents API) because `index.html` exceeds GitHub's 1 MB limit for the Contents API.

### Card System

Cards come in two types:
- **Pinned cards** (`PINNED_DEFAULTS`): Sisters Social and Quran Reflections — always expandable, stored under `aah_pinned` in localStorage
- **Event cards**: Created via admin, stored under `aah_events` in localStorage with IDs like `Date.now().toString(36)`

Card ordering is stored in `aah_card_order` (localStorage). Auth session is in `sessionStorage` under `aah_authed`.

### Icons

26 SVG Material Design icons defined in the `ICONS` array in `admin/index.html`. Each has `id`, `label`, and `path` (SVG path data). Selectable per card.

### Design System

CSS custom properties throughout. Key values:
- Accent: `rgb(148,62,12)` (warm brown)
- Background: `#d9ccbc` (beige)
- Cards: glassmorphism (semi-transparent white)
- Fonts: Cinzel (headings), Lato (body) — loaded from Google Fonts

### Flyer Images

Card flyers are base64-encoded directly in the HTML. No external image hosting. Large images increase `index.html` size, which is why the Git Data API switch was necessary.
