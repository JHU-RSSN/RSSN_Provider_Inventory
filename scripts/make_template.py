#!/usr/bin/env python3
"""Rebuild _includes/provider-template.md, the blank listing on the "Add your service" page.

    pip install pyyaml
    python scripts/make_template.py

Run it after changing a question or its answer choices in _data/fields.yml or
_data/taxonomy.yml (and run scripts/refresh_listings.py so existing listings show the
new choices too). The template uses the same format as every listing; see
scripts/listing_format.py.
"""
from listing_format import ROOT, Config, render

BODY = """Q21 (optional). A short paragraph shown beneath the summary RSSN builds from your answers:
your team's size, what sets you apart, unique tools or resources, or the projects you're best
suited for. About 500 characters. Delete this text if you don't want a paragraph."""


def main():
    cfg = Config()
    blank = {
        "title": "Your Team or Service Name",
        "unit": "Department of Example Studies",
        "contact": {"name": "First Last", "email": "name@jhu.edu"},
        "updated": "2026-01-01",
        "services": {s["name"]: "not offered" for s in cfg.services},
    }
    intro = ["# RSSN provider listing. Each field matches a question on the RSSN Research IT Provider",
             "# Questionnaire (Draft 3). Nothing is selected yet: select your answers as described below."]
    out = ROOT / "_includes/provider-template.md"
    out.write_text(render(blank, BODY, cfg, intro=intro), encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
