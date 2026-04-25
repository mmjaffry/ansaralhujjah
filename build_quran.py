#!/usr/bin/env python3
"""
build_quran.py — Generate Quran verse and surah pages from the Obsidian vault.

Scans session notes in quran-reflections/notes/ for [[Quran S-V]] and
[[N - Surah ...]] wikilinks, then generates a page for each referenced
verse and surah using data read directly from the Obsidian vault.

Usage:
    python3 build_quran.py

Requirements:
    pip3 install pyyaml

Vault path (edit if your vault moves):
    VAULT_PATH below
"""

import os
import re
import sys
import glob

# ── Config ────────────────────────────────────────────────────────────────────

VAULT_PATH  = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/الدفتر"
)
NOTES_DIR   = "quran-reflections/notes"
VERSE_OUT   = "quran/verses"
SURAH_OUT   = "quran/surahs"

# ── Dependency check ──────────────────────────────────────────────────────────

try:
    import yaml
except ImportError:
    print("Error: 'pyyaml' package not found.")
    print("Install it with:  pip3 install pyyaml")
    sys.exit(1)

# ── Patterns ──────────────────────────────────────────────────────────────────

_VERSE_RE = re.compile(r'!?\[\[Quran (\d+)-(\d+)\]\]')
_SURAH_RE = re.compile(r'!?\[\[(\d+) - Surah .+?\]\]')

# ── Vault readers ─────────────────────────────────────────────────────────────

def parse_frontmatter(text):
    """Return (yaml_dict, body_text) from a file with --- frontmatter."""
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            fm = yaml.safe_load(text[3:end]) or {}
            return fm, text[end + 4:]
    return {}, text


def read_verse(surah_num, verse_num):
    """
    Read a verse file from the vault.
    Returns dict: arabic, translator, translation, surah_num, verse_num
    or None if not found.
    """
    verse_dir = os.path.join(VAULT_PATH, "Quran", "Verses", f"Surah {surah_num}")
    fpath = os.path.join(verse_dir, f"Quran {surah_num}-{verse_num}.md")
    if not os.path.exists(fpath):
        return None

    with open(fpath, encoding='utf-8') as f:
        text = f.read()

    fm, body = parse_frontmatter(text)

    # Arabic: inside <big><big><big>…</big></big></big>
    arabic = ''
    arabic_m = re.search(r'<big><big><big>(.*?)</big></big></big>', body, re.DOTALL)
    if arabic_m:
        arabic = arabic_m.group(1).strip()

    # Translator name: ##### heading
    translator = ''
    translation = ''
    trans_m = re.search(r'#{5}\s+(.+?)\n([\s\S]*?)(?=\n#|\n```|\Z)', body)
    if trans_m:
        translator = trans_m.group(1).strip()
        # Next non-empty line after the heading
        lines = trans_m.group(2).strip().splitlines()
        for line in lines:
            line = line.strip().strip('"').strip('\u201c\u201d')
            if line:
                translation = line
                break

    return {
        'surah_num': int(fm.get('surah_num', surah_num)),
        'verse_num': int(fm.get('verse', verse_num)),
        'arabic': arabic,
        'translator': translator,
        'translation': translation,
    }


def read_surah(surah_num):
    """
    Read a surah file from the vault.
    Returns dict: arabic_name, translation, total_verses, surah_type
    or None if not found.
    """
    pattern = os.path.join(VAULT_PATH, "Quran", "Surahs", f"{surah_num} - *.md")
    matches = glob.glob(pattern)
    if not matches:
        return None

    with open(matches[0], encoding='utf-8') as f:
        text = f.read()

    fm, _ = parse_frontmatter(text)
    return {
        'surah_num': int(fm.get('surah_num', surah_num)),
        'arabic_name': fm.get('name', ''),
        'translation': fm.get('translation', ''),
        'total_verses': int(fm.get('total_verses', 0)),
        'surah_type': str(fm.get('type', '')).capitalize(),
    }

# ── HTML templates ────────────────────────────────────────────────────────────

_HEAD = """\
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;1,300&family=Playfair+Display:wght@400;600&family=Alegreya+SC:wght@400;500&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --accent-light: rgb(195,95,38);
      --accent-mid:   rgb(148,62,12);
      --accent-dark:  rgb(98,28,0);
      --bg:           #d9ccbc;
      --bg-card:      rgba(255,255,255,0.48);
      --text:         #1a0d05;
      --text-muted:   rgba(110,55,12,0.72);
    }
    html, body {
      min-height: 100vh; background: var(--bg);
      color: var(--text); font-family: "Spectral", Georgia, serif; font-weight: 300;
    }
    body {
      background:
        radial-gradient(ellipse 80% 60% at 50% -10%, rgba(148,62,12,0.10) 0%, transparent 70%),
        radial-gradient(ellipse 40% 40% at 80% 80%, rgba(120,50,8,0.07) 0%, transparent 60%),
        #d9ccbc;
      display: flex; flex-direction: column; align-items: center;
      padding: 48px 20px 80px;
    }
    .container { width: 100%; max-width: 680px; }

    /* Breadcrumb */
    .breadcrumb {
      display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
      font-family: "Alegreya SC", serif; font-size: 0.78rem; letter-spacing: 0.05em;
      color: var(--text-muted); margin-bottom: 36px;
    }
    .breadcrumb a { color: var(--text-muted); text-decoration: none; transition: color 0.2s; }
    .breadcrumb a:hover { color: var(--accent-mid); }
    .breadcrumb svg { width: 12px; height: 12px; fill: currentColor; opacity: 0.5; }

    /* Card */
    .card {
      background: var(--bg-card); border: 1px solid rgba(180,90,45,0.18);
      border-radius: 20px; padding: 36px 40px; margin-bottom: 24px;
    }
    @media (max-width: 520px) { .card { padding: 24px 20px; } }

    h1 { font-family: "Playfair Display", serif; font-size: 1.55rem; font-weight: 600;
         color: var(--accent-dark); margin-bottom: 6px; line-height: 1.3; }
    h2 { font-family: "Playfair Display", serif; font-size: 1.1rem; font-weight: 600;
         color: var(--accent-mid); margin: 28px 0 10px; }
    .surah-ref { font-family: "Alegreya SC", serif; font-size: 0.88rem;
                 color: var(--text-muted); margin-bottom: 28px; }
    .surah-meta { font-family: "Alegreya SC", serif; font-size: 0.85rem;
                  color: var(--text-muted); margin-bottom: 28px; letter-spacing: 0.03em; }

    /* Arabic */
    .arabic {
      font-family: "Amiri", serif; direction: rtl; text-align: right;
      font-size: 1.85rem; line-height: 2.1; color: var(--text);
      margin-bottom: 28px; padding: 20px 0 16px;
      border-bottom: 1px solid rgba(148,62,12,0.15);
    }

    /* Translation blockquote */
    blockquote.translation {
      border-left: 3px solid var(--accent-mid);
      margin: 0 0 0 0; padding: 12px 20px;
      background: rgba(148,62,12,0.05); border-radius: 0 8px 8px 0;
    }
    blockquote.translation p {
      font-style: italic; font-size: 1rem; line-height: 1.8;
      color: var(--text); margin-bottom: 8px;
    }
    blockquote.translation cite {
      font-family: "Alegreya SC", serif; font-size: 0.78rem;
      color: var(--text-muted); font-style: normal;
    }

    /* Backlinks */
    .backlinks-list { list-style: none; padding: 0; }
    .backlinks-list li { margin-bottom: 8px; }
    .backlinks-list a {
      font-family: "Alegreya SC", serif; font-size: 0.9rem;
      color: var(--accent-light); text-decoration: underline;
      text-underline-offset: 3px; transition: color 0.2s;
    }
    .backlinks-list a:hover { color: var(--accent-mid); }

    /* Verse nav */
    .verse-nav {
      display: flex; justify-content: space-between; gap: 12px;
      margin-bottom: 40px;
    }
    .verse-nav a {
      display: flex; align-items: center; gap: 6px;
      padding: 12px 18px; border-radius: 10px; text-decoration: none;
      background: var(--bg-card); border: 1px solid rgba(180,90,45,0.18);
      font-family: "Alegreya SC", serif; font-size: 0.82rem;
      color: var(--text-muted); letter-spacing: 0.03em;
      transition: border-color 0.2s, color 0.2s, transform 0.15s;
    }
    .verse-nav a:hover {
      border-color: rgba(148,62,12,0.4); color: var(--accent-mid);
      transform: translateY(-1px);
    }
    .verse-nav .nav-next { margin-left: auto; text-align: right; }

    /* Verse list on surah page */
    .verse-list { list-style: none; padding: 0; }
    .verse-list li { margin-bottom: 6px; }
    .verse-list a {
      font-family: "Alegreya SC", serif; font-size: 0.88rem;
      color: var(--accent-light); text-decoration: underline;
      text-underline-offset: 3px; transition: color 0.2s;
    }
    .verse-list a:hover { color: var(--accent-mid); }

    footer {
      margin-top: 20px; font-size: 0.8rem; color: rgba(70,28,4,0.65);
      letter-spacing: 0.1em; text-transform: uppercase; text-align: center;
    }
  </style>
</head>"""

_CHEVRON = '<svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>'


def render_verse_page(verse, surah_info, backlinks, prev_v, next_v):
    s = verse['surah_num']
    v = verse['verse_num']
    title = f"Quran {s}:{v}"
    surah_name = surah_info['arabic_name'] if surah_info else ''
    surah_en   = surah_info['translation']  if surah_info else ''

    surah_ref = ''
    if surah_name or surah_en:
        surah_link = f'/quran/surahs/{s}/'
        parts = []
        if surah_name:
            parts.append(f'<span style="font-family:Amiri,serif;direction:rtl">{surah_name}</span>')
        if surah_en:
            parts.append(surah_en)
        surah_ref = (
            f'<p class="surah-ref">'
            f'<a href="{surah_link}" style="color:var(--text-muted);text-decoration:none">'
            f'Surah {s} — {" · ".join(parts)}</a></p>'
        )

    arabic_block = (
        f'<div class="arabic">{verse["arabic"]}</div>'
        if verse['arabic'] else ''
    )

    translation_block = ''
    if verse['translation']:
        cite = f'<cite>— {verse["translator"]}</cite>' if verse['translator'] else ''
        translation_block = (
            f'<blockquote class="translation">'
            f'<p>{verse["translation"]}</p>'
            f'{cite}</blockquote>'
        )

    backlinks_section = ''
    if backlinks:
        items = '\n'.join(
            f'        <li><a href="/quran-reflections/{slug}/">{label}</a></li>'
            for label, slug in backlinks
        )
        backlinks_section = f"""
    <div class="card">
      <h2>Mentioned In</h2>
      <ul class="backlinks-list">
{items}
      </ul>
    </div>"""

    prev_link = (
        f'<a class="nav-prev" href="/quran/verses/{s}-{prev_v}/">← {s}:{prev_v}</a>'
        if prev_v else '<span></span>'
    )
    next_link = (
        f'<a class="nav-next" href="/quran/verses/{s}-{next_v}/">{s}:{next_v} →</a>'
        if next_v else '<span></span>'
    )

    return f"""{_HEAD}
<body>
  <div class="container">

    <nav class="breadcrumb">
      <a href="/">Ansar Al-Hujjah</a>
      {_CHEVRON}
      <a href="/quran-reflections/">Quran Reflections</a>
      {_CHEVRON}
      <a href="/quran/surahs/{s}/">Surah {s}</a>
      {_CHEVRON}
      <span>Verse {v}</span>
    </nav>

    <div class="card">
      <h1>{title}</h1>
      {surah_ref}
      {arabic_block}
      {translation_block}
    </div>
{backlinks_section}
    <nav class="verse-nav">
      {prev_link}
      {next_link}
    </nav>

  </div>
  <footer>Ansar Al-Hujjah · Houston, TX</footer>
</body>
</html>
"""


def render_surah_page(surah, referenced_verses, backlinks):
    n             = surah['surah_num']
    arabic_name   = surah['arabic_name']
    translation   = surah['translation']
    total_verses  = surah['total_verses']
    surah_type    = surah['surah_type']

    meta_parts = []
    if total_verses:
        meta_parts.append(f'{total_verses} verses')
    if surah_type:
        meta_parts.append(surah_type)
    meta = ' · '.join(meta_parts)

    verse_list_html = ''
    if referenced_verses:
        items = '\n'.join(
            f'        <li><a href="/quran/verses/{n}-{v}/">Verse {v}</a></li>'
            for v in sorted(referenced_verses)
        )
        verse_list_html = f"""
      <h2>Referenced Verses</h2>
      <ul class="verse-list">
{items}
      </ul>"""

    backlinks_section = ''
    if backlinks:
        items = '\n'.join(
            f'        <li><a href="/quran-reflections/{slug}/">{label}</a></li>'
            for label, slug in backlinks
        )
        backlinks_section = f"""
    <div class="card">
      <h2>Mentioned In</h2>
      <ul class="backlinks-list">
{items}
      </ul>
    </div>"""

    return f"""{_HEAD}
<body>
  <div class="container">

    <nav class="breadcrumb">
      <a href="/">Ansar Al-Hujjah</a>
      {_CHEVRON}
      <a href="/quran-reflections/">Quran Reflections</a>
      {_CHEVRON}
      <span>Surah {n}</span>
    </nav>

    <div class="card">
      <h1 style="font-family:Amiri,serif;direction:rtl;text-align:right;font-size:2rem">{arabic_name}</h1>
      <p class="surah-meta">Surah {n} — {translation} &nbsp;·&nbsp; {meta}</p>
      {verse_list_html}
    </div>
{backlinks_section}
  </div>
  <footer>Ansar Al-Hujjah · Houston, TX</footer>
</body>
</html>
"""

# ── Scanner ───────────────────────────────────────────────────────────────────

def scan_notes(notes_dir):
    """
    Scan all session notes and return:
      verse_backlinks: { "S-V": [(title, slug), ...] }
      surah_backlinks:  { "N":   [(title, slug), ...] }
    """
    from build_notes import slugify  # reuse the same slugify function

    verse_backlinks = {}  # "29-2" → [(title, slug)]
    surah_backlinks = {}  # "29"   → [(title, slug)]

    if not os.path.isdir(notes_dir):
        return verse_backlinks, surah_backlinks

    for fname in sorted(os.listdir(notes_dir)):
        if not fname.endswith('.md') or fname.lower() == 'readme.md':
            continue
        note_title = fname[:-3]
        note_slug  = slugify(note_title)
        fpath      = os.path.join(notes_dir, fname)
        with open(fpath, encoding='utf-8') as f:
            content = f.read()

        for m in _VERSE_RE.finditer(content):
            key = f"{m.group(1)}-{m.group(2)}"
            verse_backlinks.setdefault(key, [])
            entry = (note_title, note_slug)
            if entry not in verse_backlinks[key]:
                verse_backlinks[key].append(entry)

        for m in _SURAH_RE.finditer(content):
            key = m.group(1)
            surah_backlinks.setdefault(key, [])
            entry = (note_title, note_slug)
            if entry not in surah_backlinks[key]:
                surah_backlinks[key].append(entry)

    return verse_backlinks, surah_backlinks

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(VAULT_PATH):
        print(f"Error: Vault not found at:\n  {VAULT_PATH}")
        print("Update VAULT_PATH in build_quran.py.")
        sys.exit(1)

    print("Scanning session notes for Quran wikilinks…")
    verse_backlinks, surah_backlinks = scan_notes(NOTES_DIR)
    print(f"  Found {len(verse_backlinks)} referenced verse(s), "
          f"{len(surah_backlinks)} referenced surah(s)")

    # Build surah info cache (needed by verse pages)
    surah_cache = {}
    for s_str in set(k.split('-')[0] for k in verse_backlinks) | set(surah_backlinks):
        s = int(s_str)
        info = read_surah(s)
        if info:
            surah_cache[s] = info

    # ── Verse pages ──────────────────────────────────────────────────────────
    verse_count = 0
    # Track which verses exist per surah for prev/next nav
    verses_by_surah = {}
    for key in verse_backlinks:
        s, v = map(int, key.split('-'))
        verses_by_surah.setdefault(s, set()).add(v)

    for key, backlinks in sorted(verse_backlinks.items()):
        s, v = map(int, key.split('-'))
        verse = read_verse(s, v)
        if verse is None:
            print(f"  Warning: verse file not found for {key} — skipping")
            continue

        surah_info = surah_cache.get(s)

        # Determine prev/next among referenced verses in this surah
        sibling_verses = sorted(verses_by_surah[s])
        idx = sibling_verses.index(v)
        prev_v = sibling_verses[idx - 1] if idx > 0 else None
        next_v = sibling_verses[idx + 1] if idx < len(sibling_verses) - 1 else None

        html = render_verse_page(verse, surah_info, backlinks, prev_v, next_v)
        out_dir = os.path.join(VERSE_OUT, key)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        verse_count += 1

    print(f"  Generated {verse_count} verse page(s) → {VERSE_OUT}/")

    # ── Surah pages ──────────────────────────────────────────────────────────
    surah_count = 0
    for s_str, backlinks in sorted(surah_backlinks.items(), key=lambda x: int(x[0])):
        s = int(s_str)
        surah = surah_cache.get(s) or read_surah(s)
        if surah is None:
            print(f"  Warning: surah file not found for surah {s} — skipping")
            continue

        # Verses in this surah that were also individually referenced
        referenced_verses = {int(k.split('-')[1]) for k in verse_backlinks
                             if k.split('-')[0] == s_str}

        html = render_surah_page(surah, referenced_verses, backlinks)
        out_dir = os.path.join(SURAH_OUT, s_str)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        surah_count += 1

    print(f"  Generated {surah_count} surah page(s) → {SURAH_OUT}/")
    print(f"\nDone. Run 'python3 build_notes.py' then 'git push origin main' to publish.")


if __name__ == '__main__':
    main()
