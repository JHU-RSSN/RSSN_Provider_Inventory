#!/usr/bin/env python3
"""Rebuild _includes/provider-template.md from _data/fields.yml and _data/taxonomy.yml.

    pip install pyyaml
    python scripts/make_template.py

Run it after changing a question or its answer choices, so the "Add your service"
page and the template people copy stay in step with the questionnaire.
"""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def label_of(o):
    return (o.get("label") or o.get("name")) if isinstance(o, dict) else str(o)


def q(s):
    return json.dumps(s, ensure_ascii=False)


def main():
    tax = yaml.safe_load((ROOT / "_data/taxonomy.yml").read_text(encoding="utf-8"))
    sections = yaml.safe_load((ROOT / "_data/fields.yml").read_text(encoding="utf-8"))["sections"]
    L = [
        "---",
        "# RSSN provider listing. Each field matches a question on the RSSN Research IT Provider Questionnaire.",
        "# For lists, delete the lines that don't apply and keep the spelling of the rest exactly as written.",
        "# For single answers, pick one of the values listed in the comment above the field.",
        "# Anything that doesn't fit a listed value goes in the matching \"_other\" field as plain text.",
        "# Leave a field empty (\"\" or []) if the questionnaire skipped it for your team.",
        "",
        "# Q7. Team or service name, as researchers should see it",
        'title: "Your Team or Service Name"',
        "",
        "# Q5. One of: " + ", ".join(label_of(o) for o in tax["institutions"]),
        'institution: "JHU"',
        "",
        "# Q6. School, division, or central office. These get a colored card accent:",
        "#   " + "; ".join(s["name"] for s in tax["schools"]),
        'school: "Whiting School of Engineering"',
        "",
        "# Q6. Department or organizational unit within that school",
        'unit: "Department of Example Studies"',
        "",
        "# Q8. Website or service information URL (optional; leave \"\" if none)",
        'website: ""',
        "",
        "# Q1-4. Primary point of contact",
        "contact:",
        '  name: "First Last"',
        '  email: "name@jhu.edu"',
        "",
        "# Date this listing was last reviewed (YYYY-MM-DD)",
        "updated: 2026-01-01",
    ]
    for s in sections:
        if all(f["key"] in ("institution", "school") for f in s["fields"]):
            continue
        L += ["", f"# ===== {s['title']} ====="]
        for f in s["fields"]:
            k = f["key"]
            if k in ("institution", "school"):
                continue
            opts = [label_of(o) for o in tax.get(f.get("options"), []) or []]
            L.append("")
            if k == "services":
                L.append("# Q12-15. Services you offer (Offered or Area of strength in the grids), by group")
                L.append(f"{k}:")
                for g in tax["service_groups"]:
                    L.append(f"  # {g}")
                    L += [f"  - {q(sv['name'])}" for sv in tax["services"] if sv["group"] == g]
            elif k == "strengths":
                L.append("# Q12-15. Areas of strength: up to five of the services above")
                L.append(f"{k}:")
                L += [f"  - {q(sv['name'])}" for sv in tax["services"]][:2]
                L.append("  # ...add up to three more")
            elif f["type"] == "many":
                L.append(f"# Q{f['q']}. {f['label']}")
                L.append(f"{k}:")
                L += [f"  - {q(o)}" for o in opts]
                L.append(f'{k}_other: ""')
            elif f["type"] == "one":
                L.append(f"# Q{f['q']}. {f['label']}. One of:")
                L.append("#   " + " | ".join(opts))
                L.append(f"{k}: {q(opts[0])}")
            elif f["type"] == "short":
                L.append(f"# Q{f['q']}. {f['label']} (one line; leave \"\" if it doesn't apply)")
                L.append(f'{k}: ""')
            else:
                L.append(f"# Q{f['q']}. {f['label']} (optional; Markdown is fine)")
                L.append(f'{k}: ""')
    L += [
        "---",
        "Q18 (optional). A short paragraph shown beneath the summary RSSN builds from your answers:",
        "your team's size, what sets you apart, unique tools or resources, or the projects you're best",
        "suited for. About 500 characters. Delete this text if you don't want a paragraph.",
        "",
    ]
    out = ROOT / "_includes/provider-template.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
