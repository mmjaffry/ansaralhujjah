# Session Notes

Drop your Obsidian `.md` files here, then run the build script to generate the HTML session pages.

## Workflow

1. Write or export your session note in Obsidian
2. Copy the `.md` file into this folder
3. From the repo root, run:
   ```
   python3 build_notes.py
   python3 build_quran.py
   ```
4. Commit and push:
   ```
   git add -A && git commit -m "Add session notes" && git push
   ```

## File naming

The filename (without `.md`) becomes the URL slug.

| Filename | URL |
|---|---|
| `Session 1 - Introduction.md` | `/quran-reflections/session-1-introduction/` |
| `Session 2 - Ayat 3.md` | `/quran-reflections/session-2-ayat-3/` |

Keep filenames consistent so wikilinks resolve correctly.

## Titles vs URLs

- URL slug comes from filename
- Display title comes from the first markdown H1 (`# ...`)
- You can update note titles without renaming files/URLs

## Wikilinks

Obsidian `[[wikilinks]]` are converted as follows:

```
[[Session 1 - Introduction]]          → /quran-reflections/session-1-introduction/
[[Session 2 - Ayat 3|see session 2]]  → /quran-reflections/session-2-ayat-3/
[[Quran 29-2]]                        → /quran/verses/29-2/
![[Quran 29-2]]                       → inline Arabic + translation verse card (linked to /quran/verses/29-2/)
[[29 - Surah al-'Ankabut]]            → /quran/surahs/29/
![[29 - Surah al-'Ankabut]]           → /quran/surahs/29/
```

For verse cards to render clearly, place `![[Quran S-V]]` embeds directly in the body (paragraphs/bullets), not inside markdown table cells or heading text.

If a non-Quran wikilink does not match a note in this folder, it is rendered as plain text (no broken link).

## Frontmatter

YAML frontmatter is allowed for authoring (e.g. `speaker`, `date`, `series`, `surahs`), but it is stripped before page rendering, so metadata fields are not shown on the published page body.

## First-time setup

Install the markdown dependency once:

```
pip3 install markdown
pip3 install pyyaml
```
