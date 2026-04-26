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

Wikilink behavior:
- [[Quran S-V]]                       -> /quran/verses/S-V/
- ![[Quran S-V]]                      -> inline Arabic + translation card (linked to /quran/verses/S-V/)
- [[N - Surah ...]] / ![[N - Surah ...]] -> /quran/surahs/N/
- [[Note Name]] / [[Note|Display]]   -> /quran-reflections/{slug}/ (if known note)
- Unresolved non-Quran wikilinks are rendered as plain text.
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
OVERVIEW_NOTE_NAME = "Quran Reflections - Overview"
VAULT_PATH     = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/الدفتر"
)

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

def strip_yaml_frontmatter(text):
    """Remove leading YAML frontmatter block if present."""
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1:
            return text[end + 5:]
    return text

def extract_markdown_h1(text, fallback):
    """Return first markdown H1 text (without leading #), else fallback."""
    m = re.search(r'(?m)^\s*#\s+(.+?)\s*$', text)
    return m.group(1).strip() if m else fallback

def extract_overview_session_index_html(content_html):
    """
    Extract the overview block from H1 through Session Index tables.
    Stops before "Core Framework" section when present.
    """
    start = content_html.find('<h1')
    if start == -1:
        start = 0

    end_candidates = []
    for marker in (
        '<h2 id="core-framework"',
        '<h2 id="surahs-covered"',
        '<h2 id="central-themes"',
        '<h2 id="key-verses"',
    ):
        pos = content_html.find(marker, start)
        if pos != -1:
            end_candidates.append(pos)

    end = min(end_candidates) if end_candidates else len(content_html)
    return content_html[start:end].strip()

# ── Wikilink resolution ───────────────────────────────────────────────────────

_VERSE_PATTERN = re.compile(r'^Quran (\d+)-(\d+)$')
_SURAH_PATTERN = re.compile(r'^(\d+) - Surah .+$')
_VERSE_EMBED_PATTERN = re.compile(r'!?\[\[Quran (\d+)-(\d+)(?:\|[^\]]+)?\]\]')

_NAS_ARABIC_FALLBACK = {
    1: "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
    2: "مَلِكِ النَّاسِ",
    3: "إِلَٰهِ النَّاسِ",
    4: "مِنْ شَرِّ الْوَسْوَاسِ الْخَنَّاسِ",
    5: "الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ",
    6: "مِنَ الْجِنَّةِ وَالنَّاسِ",
}

_VERSE_CACHE = {}

def load_verse_data(surah_num, verse_num):
    """
    Read verse Arabic + translation from the local Obsidian vault.
    Returns dict or None if file is missing/unreadable.
    """
    key = (int(surah_num), int(verse_num))
    if key in _VERSE_CACHE:
        return _VERSE_CACHE[key]

    verse_path = os.path.join(
        VAULT_PATH, "Quran", "Verses", f"Surah {surah_num}", f"Quran {surah_num}-{verse_num}.md"
    )
    if not os.path.exists(verse_path):
        _VERSE_CACHE[key] = None
        return None

    with open(verse_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    body = strip_yaml_frontmatter(raw)

    arabic = ''
    arabic_m = re.search(r'<big><big><big>(.*?)</big></big></big>', body, re.DOTALL)
    if arabic_m:
        arabic = arabic_m.group(1).strip()
    if not arabic and int(surah_num) == 114:
        arabic = _NAS_ARABIC_FALLBACK.get(int(verse_num), '')

    translator = ''
    translation = ''
    trans_m = re.search(r'#{5}\s+(.+?)\n([\s\S]*?)(?=\n#|\n```|\Z)', body)
    if trans_m:
        translator = trans_m.group(1).strip()
        lines = trans_m.group(2).strip().splitlines()
        for line in lines:
            line = line.strip().strip('"').strip('\u201c\u201d')
            if line:
                translation = line
                break

    data = {
        'surah': int(surah_num),
        'verse': int(verse_num),
        'arabic': arabic,
        'translation': translation,
        'translator': translator,
    }
    _VERSE_CACHE[key] = data
    return data

def render_verse_embed_card(surah_num, verse_num):
    """
    Render ![[Quran S-V]] as an inline verse card in session notes.
    """
    data = load_verse_data(surah_num, verse_num)
    verse_url = f"/quran/verses/{surah_num}-{verse_num}/"

    if not data:
        return f'<a href="{verse_url}">Quran {surah_num}-{verse_num}</a>'

    arabic_html = (
        f'<div class="verse-embed-arabic">{data["arabic"]}</div>'
        if data['arabic'] else ''
    )
    translation_html = ''
    if data['translation']:
        cite = f'<cite>— {data["translator"]}</cite>' if data['translator'] else ''
        translation_html = (
            f'<blockquote class="verse-embed-translation">'
            f'<p>{data["translation"]}</p>{cite}</blockquote>'
        )

    return (
        f'<div class="verse-embed-card">'
        f'<a class="verse-embed-ref" href="{verse_url}">Quran {surah_num}:{verse_num}</a>'
        f'{arabic_html}'
        f'{translation_html}'
        f'</div>'
    )

def replace_verse_embeds(text):
    """Convert [[Quran S-V]] and ![[Quran S-V]] to inline verse cards, except in heading/table lines."""
    def repl(m):
        return render_verse_embed_card(m.group(1), m.group(2))
    out = []
    for line in text.split('\n'):
        stripped = line.lstrip()
        if stripped.startswith('#') or stripped.startswith('|') or stripped.startswith('>'):
            out.append(line)
        else:
            out.append(_VERSE_EMBED_PATTERN.sub(repl, line))
    return '\n'.join(out)

def resolve_wikilinks(text, slug_map):
    """
    Convert Obsidian [[wikilinks]] to standard Markdown links before parsing.
      [[Quran S-V]]              → [Quran S-V](/quran/verses/S-V/)
      [[N - Surah name]]         → [N - Surah name](/quran/surahs/N/)
      [[Note Name]]              → [Note Name](/quran-reflections/note-name/)
      [[Note Name|Display Text]] → [Display Text](...) with the same routing
    Wikilinks that match none of the above are rendered as plain text.
    Handles both [[...]] and ![[...]] (Obsidian embed syntax).
    """
    def replace(m):
        inner = m.group(1)
        if '|' in inner:
            note_name, display = inner.split('|', 1)
        else:
            note_name = display = inner
        note_name = note_name.strip()
        display   = display.strip()

        vm = _VERSE_PATTERN.match(note_name)
        if vm:
            return f'[{display}](/quran/verses/{vm.group(1)}-{vm.group(2)}/)'

        sm = _SURAH_PATTERN.match(note_name)
        if sm:
            return f'[{display}](/quran/surahs/{sm.group(1)}/)'

        if note_name == OVERVIEW_NOTE_NAME:
            return f'[{display}]({PROGRAM_URL}/)'

        if note_name in slug_map:
            return f'[{display}]({PROGRAM_URL}/{slug_map[note_name]}/)'

        return display

    text = replace_verse_embeds(text)
    text = re.sub(r'!\[\[([^\]]+)\]\]', replace, text)
    text = re.sub(r'\[\[([^\]]+)\]\]', replace, text)
    return text

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

    prev_box = (
        f'<a class="header-nav-btn" href="{PROGRAM_URL}/{prev_session[1]}/">← Previous</a>'
        if prev_session else
        '<span class="header-nav-btn disabled">← Previous</span>'
    )
    overview_box = f'<a class="header-nav-btn" href="{PROGRAM_URL}/">Overview</a>'
    next_box = (
        f'<a class="header-nav-btn" href="{PROGRAM_URL}/{next_session[1]}/">Next →</a>'
        if next_session else
        '<span class="header-nav-btn disabled">Next →</span>'
    )
    header_nav = f'<div class="article-header-nav">{prev_box}{overview_box}{next_box}</div>'
    content_for_page = content_html.replace('<hr />', header_nav + '\n<hr />', 1)
    if content_for_page == content_html:
        content_for_page = header_nav + '\n' + content_html

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
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&family=Playfair+Display:wght@400;600&family=Alegreya+SC:wght@400;500&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
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
      color: var(--text); font-family: "EB Garamond", Georgia, serif;
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
      font-family: "Alegreya SC", serif; font-size: 0.78rem; letter-spacing: 0.05em;
      color: var(--text-muted); margin-bottom: 36px;
    }}
    .breadcrumb a {{ color: var(--text-muted); text-decoration: none; transition: color 0.2s; }}
    .breadcrumb a:hover {{ color: var(--accent-mid); }}
    .breadcrumb svg {{ width: 12px; height: 12px; fill: currentColor; opacity: 0.5; }}

    /* ── Article ── */
    .article {{
      border-top: 2px solid var(--accent-mid);
      padding-top: 32px; margin-bottom: 40px;
    }}
    .article h1 {{
      font-family: "Playfair Display", serif; font-size: 1.8rem; font-weight: 600;
      color: var(--accent-dark);
      margin-bottom: 10px; line-height: 1.25;
    }}
    .article h1 + p {{
      font-size: 1.05rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 14px;
    }}
    .article-header-nav {{
      display: flex; gap: 8px; margin-bottom: 32px;
    }}
    .header-nav-btn {{
      flex: 1; text-align: center; padding: 7px 10px;
      font-family: "Alegreya SC", serif; font-size: 0.8rem; letter-spacing: 0.04em;
      border: 1px solid rgba(148,62,12,0.22); border-radius: 6px;
      text-decoration: none; color: var(--text-muted); background: rgba(148,62,12,0.03);
      transition: border-color 0.2s, color 0.2s;
    }}
    .header-nav-btn:hover {{ border-color: rgba(148,62,12,0.45); color: var(--accent-mid); }}
    .header-nav-btn.disabled {{ opacity: 0.35; cursor: default; }}
    .article h2 {{
      font-family: "Playfair Display", serif; font-size: 1.2rem; font-weight: 600;
      color: var(--accent-mid);
      margin: 32px 0 12px;
    }}
    .article h3 {{
      font-family: "Playfair Display", serif; font-size: 1.05rem; font-weight: 600;
      color: var(--text);
      margin: 22px 0 8px;
    }}
    .article p {{
      font-size: 1.05rem; line-height: 1.85; color: var(--text);
      margin-bottom: 16px;
    }}
    .article ul, .article ol {{
      padding-left: 24px; margin-bottom: 16px;
    }}
    .article li {{
      font-size: 1.05rem; line-height: 1.8; color: var(--text);
      margin-bottom: 6px;
    }}
    .article a {{
      color: var(--accent-light); text-decoration: underline;
      text-underline-offset: 3px;
      transition: color 0.2s;
    }}
    .article a:hover {{ color: var(--accent-mid); }}
    .article blockquote {{
      border-left: 3px solid var(--accent-mid);
      margin: 18px 0; padding: 10px 20px;
      background: rgba(148,62,12,0.04);
      font-style: italic;
    }}
    .article blockquote p {{ margin-bottom: 0; color: var(--text-muted); }}
    .article hr {{
      border: none; border-top: 1px solid rgba(148,62,12,0.18);
      margin: 32px 0;
    }}
    .article code {{
      background: rgba(148,62,12,0.08); border-radius: 4px;
      padding: 2px 6px; font-size: 0.9em;
    }}
    .article pre {{
      background: rgba(148,62,12,0.06); border-radius: 8px;
      padding: 16px; overflow-x: auto; margin-bottom: 16px;
    }}
    .article pre code {{ background: none; padding: 0; }}
    .article table {{
      border-collapse: collapse; margin: 0 auto 16px;
      font-size: 1rem;
    }}
    .article th, .article td {{
      padding: 8px 14px; text-align: left;
      border-bottom: 1px solid rgba(148,62,12,0.15);
    }}
    .article th {{ font-weight: 700; color: var(--accent-mid); }}
    .article table th:first-child, .article table td:first-child {{ min-width: 5.5em; }}
    .article table th:nth-child(2), .article table td:nth-child(2) {{ min-width: 6.5em; white-space: nowrap; }}

    /* ── Inline Quran verse embeds ── */
    .verse-embed-card {{
      border-left: 3px solid var(--accent-mid);
      padding: 12px 0 12px 20px;
      margin: 22px 0;
    }}
    .verse-embed-ref {{
      display: inline-block;
      font-family: "Alegreya SC", serif;
      font-size: 0.82rem;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      text-decoration: none;
      margin-bottom: 28px;
    }}
    .verse-embed-ref:hover {{ color: var(--accent-mid); }}
    .verse-embed-arabic {{
      font-family: "Amiri", serif;
      direction: rtl; text-align: right;
      font-size: 1.8rem; line-height: 2.0;
      color: var(--text);
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(148,62,12,0.12);
    }}
    .verse-embed-translation {{
      margin: 0;
    }}
    .verse-embed-translation p {{
      margin: 0 0 6px; font-size: 1.0rem; font-style: italic; color: var(--text); line-height: 1.75;
    }}
    .verse-embed-translation cite {{
      font-family: "Alegreya SC", serif; font-size: 0.78rem; color: var(--text-muted); font-style: normal;
    }}
    /* Snap verse cards to article left edge when inside list items */
    .article li .verse-embed-card {{
      margin-left: -24px;
      width: calc(100% + 24px);
    }}

    /* ── Trials reference list (numbered, compact verses) ── */
    .article .trials-list {{ padding-left: 24px; margin: 0 0 16px; }}
    .article .trials-list li {{ margin-bottom: 8px; }}
    .article .trials-list li p {{
      margin-bottom: 4px; font-family: "Playfair Display", serif;
      font-size: 1.05rem; font-weight: 600; color: var(--text); line-height: 1.55;
    }}
    .article .trials-list .verse-embed-card {{
      margin-left: -24px; width: calc(100% + 24px);
      margin-top: 6px; margin-bottom: 8px;
      padding: 8px 0 8px 14px;
    }}
    .article .trials-list .verse-embed-ref {{ font-size: 0.75rem; margin-bottom: 6px; }}
    .article .trials-list .verse-embed-arabic {{
      font-size: 1.2rem; line-height: 1.7; margin-bottom: 6px; padding-bottom: 6px;
    }}
    .article .trials-list .verse-embed-translation p {{ font-size: 0.82rem; line-height: 1.55; }}
    .article .trials-list .verse-embed-translation cite {{ font-size: 0.7rem; }}

    /* ── Session nav ── */
    .session-nav {{
      display: flex; justify-content: space-between; gap: 12px;
      margin-bottom: 40px;
    }}
    .session-nav a {{
      display: flex; align-items: center; gap: 6px;
      padding: 12px 18px; border-radius: 10px; text-decoration: none;
      background: var(--bg-card); border: 1px solid rgba(180,90,45,0.18);
      font-family: "Alegreya SC", serif; font-size: 0.82rem;
      color: var(--text-muted); letter-spacing: 0.03em;
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

    <article class="article">
      {content_for_page}
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

def inject_sessions(sessions, overview_index_html=None):
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

    if overview_index_html:
        inner = f'\n        {overview_index_html}\n        '
    elif sessions:
        links = '\n'.join(
            f'        <a class="session-link" href="{PROGRAM_URL}/{slug}/">{title}</a>'
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

    # Build ordered session list with display titles from markdown H1.
    session_entries = []
    for fname in md_files:
        note_name = fname[:-3]
        slug = slug_map[note_name]
        fpath = os.path.join(NOTES_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            raw = f.read()
        body = strip_yaml_frontmatter(raw)
        display_title = extract_markdown_h1(body, note_name)
        session_entries.append({
            'note_name': note_name,
            'slug': slug,
            'body': body,
            'display_title': display_title,
        })

    # Notes shown in the main session index / prev-next sequence.
    navigable_entries = [e for e in session_entries if e['note_name'] != OVERVIEW_NOTE_NAME]
    nav_idx_by_name = {e['note_name']: i for i, e in enumerate(navigable_entries)}

    overview_index_html = None

    # Generate each session page
    for i, entry in enumerate(session_entries):
        title = entry['note_name']
        slug = entry['slug']
        raw = entry['body']

        # Pre-process: resolve [[wikilinks]] to standard markdown links
        processed = resolve_wikilinks(raw, slug_map)

        # Parse markdown → HTML (extra adds tables, footnotes; toc adds heading ids)
        content_html = md_lib.markdown(processed, extensions=['extra', 'toc'])

        if title == OVERVIEW_NOTE_NAME:
            overview_index_html = extract_overview_session_index_html(content_html)

        display_title = entry['display_title']

        if title in nav_idx_by_name:
            nav_i = nav_idx_by_name[title]
            prev_session = (
                (navigable_entries[nav_i - 1]['display_title'], navigable_entries[nav_i - 1]['slug'])
                if nav_i > 0 else None
            )
            next_session = (
                (navigable_entries[nav_i + 1]['display_title'], navigable_entries[nav_i + 1]['slug'])
                if nav_i < len(navigable_entries) - 1 else None
            )
        else:
            prev_session = None
            next_session = None

        page_html = render_page(display_title, content_html, prev_session, next_session)

        out_dir = os.path.join(OUTPUT_BASE, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

        print(f"  Built: {out_path}")

    # Update session list in quran-reflections/index.html
    inject_sessions(
        [(e['display_title'], e['slug']) for e in navigable_entries],
        overview_index_html=overview_index_html
    )

    print(f"\nDone. {len(session_entries)} session page(s) generated.")
    print("Run 'git push origin main' to publish.")

if __name__ == '__main__':
    main()
