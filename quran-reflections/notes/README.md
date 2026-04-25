# Session Notes

Drop your Obsidian `.md` files here, then run the build script to generate the HTML session pages.

## Workflow

1. Write or export your session note in Obsidian
2. Copy the `.md` file into this folder
3. From the repo root, run:
   ```
   python3 build_notes.py
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

## Wikilinks

Obsidian `[[wikilinks]]` to other notes in this folder are automatically converted to hyperlinks:

```
[[Session 1 - Introduction]]          → links to /quran-reflections/session-1-introduction/
[[Session 2 - Ayat 3|see session 2]]  → links to /quran-reflections/session-2-ayat-3/
```

Links to notes that do not exist in this folder will still be generated (pointing to the expected slug URL), so you can create notes in any order.

## First-time setup

Install the markdown dependency once:

```
pip3 install markdown
```
