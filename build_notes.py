#!/usr/bin/env python3
"""
build_notes.py — Convert Obsidian .md session notes to styled HTML pages.

Usage:
    python3 build_notes.py

Requirements:
    pip3 install markdown

Workflow:
    1. Drop .md files from your Obsidian vault into quran-reflections/notes/
    2. Run this script
    3. git push

[[Wikilinks]] to other note files are resolved to /quran-reflections/{slug}/ URLs.
[[Note Name|Display Text]] aliased links are also supported.
"""

import os
import re
import sys

# ── Config ────────────────────────────────────────────────────────────────────

NOTES_DIR      = "quran-reflections/notes"
OUTPUT_BASE    = "quran-reflections"
PROGRAM_INDEX  = "quran-reflections/index.html"
SESSIONS_START = "<!-- SESSIONS-START -->"
SESSIONS_END   = "<!-- SESSIONS-END -->"
PROGRAM_TITLE  = "Quran Reflections"
PROGRAM_URL    = "/quran-reflections"

# ── Dependency check ──────────────────────────────────────────────────────────

try:
    import markdown as md_lib
except ImportError:
    print("Error: 'markdown' package not found.")
    print("Install it with:  pip3 install markdown")
    sys.exit(1)

# ── Slug helpers ──────────────────────────────────────────────────────────────

def slugify(name):
    """Convert a note filename (without .md) to a URL-safe slug."""
    s = name.lower()
    s = re.sub(r'[^\w\s-]', '', s)   # strip non-word, non-space, non-hyphen
    s = re.sub(r'[\s_]+', '-', s)    # spaces/underscores → hyphen
    s = re.sub(r'-+', '-', s)        # collapse multiple hyphens (e.g. " - " → "-")
    s = s.strip('-')
    return s

def build_slug_map(notes_dir):
    """Return {note_title: slug} for every .md file in notes_dir."""
    slug_map = {}
    for fname in os.listdir(notes_dir):
        if fname.endswith('.md') and fname.lower() != 'readme.md':
            title = fname[:-3]
            slug_map[title] = slugify(title)
    return slug_map

# ── Wikilink resolution ───────────────────────────────────────────────────────

def resolve_wikilinks(text, slug_map):
    """
    Convert Obsidian [[wikilinks]] to standard Markdown links before parsing.
      [[Note Name]]              → [Note Name](/quran-reflections/note-name/)
      [[Note Name|Display Text]] → [Display Text](/quran-reflections/note-name/)
    Links to notes not in the slug_map are slugified from the note name.
    """
    def replace(m):
        inner = m.group(1)
        if '|' in inner:
            note_name, display = inner.split('|', 1)
        else:
            note_name = display = inner
        note_name = note_name.strip()
        display   = display.strip()
        slug = slug_map.get(note_name, slugify(note_name))
        url  = f"{PROGRAM_URL}/{slug}/"
        return f'[{display}]({url})'

    return re.sub(r'\[\[([^\]]+)\]\]', replace, text)

# ── Page template ─────────────────────────────────────────────────────────────

def render_page(title, content_html, prev_session, next_session):
    """Wrap article HTML in the site-styled full page template."""

    prev_link = (
        f'<a class="nav-prev" href="{PROGRAM_URL}/{prev_session[1]}/">'
        f'← {prev_session[0]}</a>'
        if prev_session else '<span></span>'
    )
    next_link = (
        f'<a class="nav-next" href="{PROGRAM_URL}/{next_session[1]}/">'
        f'{next_session[0]} →</a>'
        if next_session else '<span></span>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} · {PROGRAM_TITLE} · Ansar Al-Hujjah</title>
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lato:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --accent-light: rgb(195,95,38);
      --accent-mid:   rgb(148,62,12);
      --accent-dark:  rgb(98,28,0);
      --bg:           #d9ccbc;
      --bg-card:      rgba(255,255,255,0.48);
      --text:         #1a0d05;
      --text-muted:   rgba(110,55,12,0.72);
    }}
    html, body {{
      min-height: 100vh; background: var(--bg);
      color: var(--text); font-family: "Lato", sans-serif; font-weight: 300;
    }}
    body {{
      background:
        radial-gradient(ellipse 80% 60% at 50% -10%, rgba(148,62,12,0.10) 0%, transparent 70%),
        radial-gradient(ellipse 40% 40% at 80% 80%, rgba(120,50,8,0.07) 0%, transparent 60%),
        #d9ccbc;
      display: flex; flex-direction: column; align-items: center;
      padding: 48px 20px 80px;
    }}
    .container {{ width: 100%; max-width: 680px; }}

    /* ── Nav ── */
    .breadcrumb {{
      display: flex; align-items: center; gap: 8px;
      font-size: 0.78rem; letter-spacing: 0.05em; text-transform: uppercase;
      color: var(--text-muted); margin-bottom: 36px;
    }}
    .breadcrumb a {{ color: var(--text-muted); text-decoration: none; transition: color 0.2s; }}
    .breadcrumb a:hover {{ color: var(--accent-mid); }}
    .breadcrumb svg {{ width: 12px; height: 12px; fill: currentColor; opacity: 0.5; }}

    /* ── Article ── */
    .article-card {{
      background: var(--bg-card); border: 1px solid rgba(180,90,45,0.18);
      border-radius: 20px; padding: 36px 40px; margin-bottom: 24px;
    }}
    .article-card h1 {{
      font-family: "Cinzel", serif; font-size: 1.55rem; font-weight: 600;
      letter-spacing: 0.05em; color: var(--accent-dark);
      margin-bottom: 8px; line-height: 1.3;
    }}
    .article-card h2 {{
      font-family: "Cinzel", serif; font-size: 1.1rem; font-weight: 600;
      letter-spacing: 0.04em; color: var(--accent-mid);
      margin: 28px 0 10px;
    }}
    .article-card h3 {{
      font-family: "Cinzel", serif; font-size: 0.95rem; font-weight: 600;
      letter-spacing: 0.04em; color: var(--text);
      margin: 20px 0 8px;
    }}
    .article-card p {{
      font-size: 0.95rem; line-height: 1.8; color: var(--text);
      margin-bottom: 14px;
    }}
    .article-card ul, .article-card ol {{
      padding-left: 22px; margin-bottom: 14px;
    }}
    .article-card li {{
      font-size: 0.95rem; line-height: 1.75; color: var(--text);
      margin-bottom: 4px;
    }}
    .article-card a {{
      color: var(--accent-light); text-decoration: underline;
      text-underline-offset: 3px;
      transition: color 0.2s;
    }}
    .article-card a:hover {{ color: var(--accent-mid); }}
    .article-card blockquote {{
      border-left: 3px solid var(--accent-mid);
      margin: 16px 0; padding: 10px 18px;
      background: rgba(148,62,12,0.05); border-radius: 0 8px 8px 0;
      font-style: italic;
    }}
    .article-card blockquote p {{ margin-bottom: 0; color: var(--text-muted); }}
    .article-card hr {{
      border: none; border-top: 1px solid rgba(148,62,12,0.18);
      margin: 28px 0;
    }}
    .article-card code {{
      background: rgba(148,62,12,0.08); border-radius: 4px;
      padding: 2px 6px; font-size: 0.85em;
    }}
    .article-card pre {{
      background: rgba(148,62,12,0.06); border-radius: 8px;
      padding: 16px; overflow-x: auto; margin-bottom: 14px;
    }}
    .article-card pre code {{ background: none; padding: 0; }}
    .article-card table {{
      width: 100%; border-collapse: collapse; margin-bottom: 14px;
      font-size: 0.9rem;
    }}
    .article-card th, .article-card td {{
      padding: 8px 14px; text-align: left;
      border-bottom: 1px solid rgba(148,62,12,0.15);
    }}
    .article-card th {{ font-weight: 600; color: var(--accent-mid); }}

    /* ── Session nav ── */
    .session-nav {{
      display: flex; justify-content: space-between; gap: 12px;
      margin-bottom: 40px;
    }}
    .session-nav a {{
      display: flex; align-items: center; gap: 6px;
      padding: 12px 18px; border-radius: 10px; text-decoration: none;
      background: var(--bg-card); border: 1px solid rgba(180,90,45,0.18);
      font-size: 0.82rem; color: var(--text-muted); letter-spacing: 0.03em;
      transition: border-color 0.2s, color 0.2s, transform 0.15s;
      max-width: 48%;
    }}
    .session-nav a:hover {{
      border-color: rgba(148,62,12,0.4); color: var(--accent-mid);
      transform: translateY(-1px);
    }}
    .session-nav .nav-next {{ margin-left: auto; text-align: right; }}

    footer {{
      margin-top: 20px; font-size: 0.8rem; color: rgba(70,28,4,0.65);
      letter-spacing: 0.1em; text-transform: uppercase; text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">

    <nav class="breadcrumb">
      <a href="/">Ansar Al-Hujjah</a>
      <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
      <a href="{PROGRAM_URL}/">{PROGRAM_TITLE}</a>
      <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
      <span>{title}</span>
    </nav>

    <article class="article-card">
      {content_html}
    </article>

    <nav class="session-nav">
      {prev_link}
      {next_link}
    </nav>

  </div>
  <footer>Ansar Al-Hujjah · Houston, TX</footer>
</body>
</html>
"""

# ── Session index injection ───────────────────────────────────────────────────

def inject_sessions(sessions):
    """Replace content between SESSIONS-START and SESSIONS-END in program index."""
    if not os.path.exists(PROGRAM_INDEX):
        print(f"  Warning: {PROGRAM_INDEX} not found — skipping session list injection.")
        return

    with open(PROGRAM_INDEX, 'r', encoding='utf-8') as f:
        html = f.read()

    start_i = html.find(SESSIONS_START)
    end_i   = html.find(SESSIONS_END)
    if start_i == -1 or end_i == -1:
        print(f"  Warning: SESSIONS-START/END markers not found in {PROGRAM_INDEX}.")
        return

    if sessions:
        links = '\n'.join(
            f'        <a class="session-link" href="{PROGRAM_URL}/{slug}/">'
            f'<span>{title}</span><span class="session-arrow">→</span></a>'
            for title, slug in sessions
        )
        inner = f'\n{links}\n        '
    else:
        inner = '\n        <p class="sessions-empty">Session notes coming soon.</p>\n        '

    new_html = html[:start_i + len(SESSIONS_START)] + inner + html[end_i:]
    with open(PROGRAM_INDEX, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"  Updated session list in {PROGRAM_INDEX} ({len(sessions)} sessions)")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.isdir(NOTES_DIR):
        print(f"Notes directory not found: {NOTES_DIR}")
        print("Create it and add your Obsidian .md files there.")
        sys.exit(1)

    md_files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith('.md') and f.lower() != 'readme.md')
    if not md_files:
        print(f"No .md files found in {NOTES_DIR}/ — resetting session list.")
        inject_sessions([])
        sys.exit(0)

    print(f"Found {len(md_files)} note(s) in {NOTES_DIR}/")

    slug_map = build_slug_map(NOTES_DIR)

    # Build ordered session list: (title, slug)
    sessions = []
    for fname in md_files:
        note_name = fname[:-3]
        sessions.append((note_name, slug_map[note_name]))

    # Generate each session page
    for i, (title, slug) in enumerate(sessions):
        fpath = os.path.join(NOTES_DIR, title + '.md')
        with open(fpath, 'r', encoding='utf-8') as f:
            raw = f.read()

        # Pre-process: resolve [[wikilinks]] to standard markdown links
        processed = resolve_wikilinks(raw, slug_map)

        # Parse markdown → HTML (extra adds tables, footnotes; toc adds heading ids)
        content_html = md_lib.markdown(processed, extensions=['extra', 'toc'])

        # Extract title from first H1, falling back to filename
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content_html, re.IGNORECASE | re.DOTALL)
        display_title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else title

        prev_session = sessions[i - 1] if i > 0 else None
        next_session = sessions[i + 1] if i < len(sessions) - 1 else None

        page_html = render_page(display_title, content_html, prev_session, next_session)

        out_dir = os.path.join(OUTPUT_BASE, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

        print(f"  Built: {out_path}")

    # Update session list in quran-reflections/index.html
    inject_sessions(sessions)

    print(f"\nDone. {len(sessions)} session page(s) generated.")
    print("Run 'git push origin main' to publish.")

if __name__ == '__main__':
    main()
