#!/usr/bin/env python3
"""Rewrite listing files in the current format, keeping every answer they already have.

    pip install pyyaml
    python scripts/refresh_listings.py                 # every file in _providers
    python scripts/refresh_listings.py _providers/jhpce.md

Run it after adding, renaming, or reordering an answer choice in _data/taxonomy.yml or a
question in _data/fields.yml, so every listing shows the new list of choices. It also
converts older listings (services and strengths as two lists) to the services grid format.

Answers that aren't listed choices are kept and marked "# not one of the listed choices",
and keys the questionnaire no longer has are kept at the bottom of the file, so nothing is
lost. If you renamed a choice, update the listings that use it (or add the old wording to
"aliases" in taxonomy.yml and re-import) before refreshing. Review the git diff before committing.
"""
import sys
from pathlib import Path

from listing_format import PROVIDERS, Config, EDIT_HELP, read_listing, render, split_front_matter


def intro_lines(path):
    """The file's own opening comment (e.g. "Pilot response..."), without the edit help."""
    front, _ = split_front_matter(Path(path).read_text(encoding="utf-8"))
    out = []
    for line in front.split("\n"):
        if not line.startswith("#") or line in EDIT_HELP or line.startswith("# HOW TO EDIT"):
            break
        out.append(line)
    while out and out[-1].strip() == "#":
        out.pop()
    return out or None


def main(argv):
    cfg = Config()
    paths = [Path(p) for p in argv] or sorted(PROVIDERS.glob("*.md"))
    changed = 0
    for path in paths:
        data, body, dups = read_listing(path)
        if dups:
            print(f"skip   {path.name}: {', '.join(k for k, _ in dups)} answered more than once; fix that first")
            continue
        text = render(data, body, cfg, intro=intro_lines(path))
        if text != path.read_text(encoding="utf-8"):
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
            print(f"wrote  {path.name}")
    print(f"{changed} of {len(paths)} listings rewritten.")


if __name__ == "__main__":
    main(sys.argv[1:])
