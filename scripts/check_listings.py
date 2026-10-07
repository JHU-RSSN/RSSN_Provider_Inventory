#!/usr/bin/env python3
"""Check provider listings for editing mistakes before merging a pull request.

    pip install pyyaml
    python scripts/check_listings.py                      # every file in _providers
    python scripts/check_listings.py _providers/jhpce.md  # just one

Finds the mistakes that are easy to make when selecting and unselecting lines on GitHub:
  - more than one answer left selected on a "choose one" question
  - an answer whose spelling no longer matches a listed choice (it would drop out of filters)
  - a service marked with a word other than "not offered", "offered", or "strength"
  - more than five areas of strength
  - lines whose spacing broke the file
Problems marked ERROR need fixing; WARNING ones are worth a look. Exits with status 1 if
there are any errors.
"""
import datetime as dt
import difflib
import sys
from pathlib import Path

import yaml

from listing_format import HEADER_KEYS, LEVELS, PRIVATE_KEYS, MAX_STRENGTHS, PROVIDERS, Config, as_list, read_listing


def suggest(value, options):
    same = [o for o in options if o.lower() == str(value).lower()]
    hit = same or difflib.get_close_matches(str(value), options, n=1, cutoff=0.6)
    return f' Did you mean "{hit[0]}"?' if hit else " See _data/taxonomy.yml for the listed choices."


def check(path, cfg):
    errors, warnings = [], []
    try:
        data, body, dups = read_listing(path)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f" near line {mark.line + 2}" if mark else ""
        return [f"the file can't be read{where}. Usually a line lost its leading spaces or a quotation mark. "
                f"({getattr(e, 'problem', e)})"], []
    except ValueError as e:
        return [str(e)], []

    for key, line in dups:
        f = cfg.by_key.get(key)
        what = f"Q{f['q']} ({key})" if f else key
        errors.append(f"{what} is answered more than once (again on line {line}). For a CHOOSE ONE question, "
                      f"put \"# \" back in front of every line but one.")

    for k in PRIVATE_KEYS:
        if k in data:
            errors.append(f"{k} is in the file. Who filled out the questionnaire and who approved the listing "
                          f"aren't published; delete those lines.")
    if not str(data.get("title") or "").strip():
        errors.append("title is blank")
    if not str((data.get("contact") or {}).get("email") or "").strip():
        warnings.append("contact email is blank")
    if data.get("updated") and not isinstance(data["updated"], (dt.date, dt.datetime)):
        warnings.append(f'updated should be a date like 2026-10-07, not "{data["updated"]}"')

    for f in cfg.stored_fields():
        k, t = f["key"], f["type"]
        v = data.get(k)
        label = f"Q{f['q']} ({k})"
        if t == "one":
            if isinstance(v, list):
                errors.append(f"{label} is a CHOOSE ONE question but has a list of answers")
            elif v not in (None, "") and str(v) not in cfg.options(k):
                if k == "school":
                    warnings.append(f'school "{v}" isn\'t one of the listed schools, so its card has no color accent')
                else:
                    errors.append(f'{label}: "{v}" is not one of the choices.{suggest(v, cfg.options(k))}')
        elif t == "many":
            if v is not None and not isinstance(v, list):
                errors.append(f"{label} should be a list (each answer on its own line starting with \"  - \")")
                continue
            vals = as_list(v)
            for x in vals:
                if str(x) not in cfg.options(k):
                    errors.append(f'{label}: "{x}" is not one of the choices.{suggest(x, cfg.options(k))}')
            if len(vals) != len(set(map(str, vals))):
                warnings.append(f"{label} lists the same answer twice")
            for lone in ("Not applicable", "None of the above"):
                if lone in vals and len(vals) > 1:
                    warnings.append(f'{label} has "{lone}" selected along with other answers')
        elif t == "grid":
            if not isinstance(v, dict):
                errors.append("services should list every service with not offered, offered, or strength after it")
                continue
            for name, level in v.items():
                word = str(level if level is not None else "").strip().lower()
                if name not in cfg.service_names:
                    errors.append(f'services: "{name}" is not one of the services.{suggest(name, cfg.service_names)}')
                if word not in LEVELS:
                    errors.append(f'services: "{name}" is marked "{level}"; use not offered, offered, or strength')
            missing = [n for n in cfg.service_names if n not in v]
            if missing:
                warnings.append("services is missing: " + "; ".join(missing) + " (they'll count as not offered)")
            n = sum(1 for x in v.values() if str(x).strip().lower() == "strength")
            if n > MAX_STRENGTHS:
                warnings.append(f"{n} services are marked strength; the limit is {MAX_STRENGTHS}")
        elif v is not None and not isinstance(v, str):
            warnings.append(f"{label} should be text in quotation marks")

    if data.get("hands_on") == "No":
        tech = [k for k in ("languages", "databases", "devops", "hosting") if as_list(data.get(k))]
        if tech:
            warnings.append(f'Q22 (hands_on) is "No" but {", ".join(tech)} has answers selected; the site shows them as N/A')

    known = set(HEADER_KEYS) | set(PRIVATE_KEYS) | {f["key"] for f in cfg.fields} | {f["key"] + "_other" for f in cfg.fields}
    unknown = [k for k in data if k not in known]
    if unknown:
        warnings.append("keys the questionnaire doesn't have (check the spelling): " + ", ".join(unknown))
    return errors, warnings


def main(argv):
    cfg = Config()
    paths = [Path(p) for p in argv] or sorted(PROVIDERS.glob("*.md"))
    n_err = n_warn = 0
    for path in paths:
        errors, warnings = check(path, cfg)
        n_err += len(errors)
        n_warn += len(warnings)
        if errors or warnings:
            print(path.name)
            for e in errors:
                print(f"  ERROR    {e}")
            for w in warnings:
                print(f"  WARNING  {w}")
    print(f"\nChecked {len(paths)} listing(s): {n_err} error(s), {n_warn} warning(s).")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
