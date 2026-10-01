# RSSN Provider Inventory (prototype)

A prototype GitHub Pages site for the Research Software Support Network (RSSN) service provider inventory. It lists Johns Hopkins teams that support research software, data, and computing, with search, filters, and a profile page for each team.

**Live site:** https://meganforbes.github.io/RSSN_Provider_Inventory_Prototpye/

> Listings imported from the first questionnaire responses (September 2026) describe real teams and haven't been reviewed by those teams yet. Listings with `sample: true` are fictional examples kept to show how the directory works; delete them once real listings cover the same ground.

## How it works

The site is built with [Jekyll](https://jekyllrb.com/), which GitHub Pages runs automatically. There's no server or database. Every push to `main` rebuilds the site in a minute or two.

- Each team is one Markdown file in `_providers/`. Jekyll turns each file into a profile page at `/providers/<file-name>/` and a card on the home page.
- The home page's search and filters run in the browser (`assets/js/directory.js`) using data Jekyll writes into the page at build time.
- `_data/fields.yml` lists every listing field, grouped the way the questionnaire groups them. It drives the profile page, the search data, the filter panel, and the import script.
- Allowed values for every list field live in `_data/taxonomy.yml`. They mirror the RSSN Research IT Provider Questionnaire.

## Importing questionnaire responses

`scripts/import_responses.py` turns the Microsoft Forms Excel export into listings, one file per response:

```sh
pip install openpyxl pyyaml
python scripts/import_responses.py "Research Software Support Network ... .xlsx"
```

It skips listings that already exist (add `--overwrite` to replace them). Answers are matched to the values in `_data/taxonomy.yml`. Anything that doesn't match, like a write-in "Other" answer, is kept as text in that field's `_other` key, and the script lists which files have them. Review each new file before committing, especially `school` and `unit`, since the form collects those as one free-text answer.

If the questionnaire adds or renames an answer choice, add it to `_data/taxonomy.yml` first so it imports as a filterable value instead of a write-in.

## Adding or updating a listing by hand

Contributors don't need to clone anything. The site's [Add your service](https://meganforbes.github.io/RSSN_Provider_Inventory_Prototpye/add-your-service/) page walks them through proposing a change on github.com. Every provider profile also has a "Suggest an edit on GitHub" link.

1. Copy `_includes/provider-template.md` into `_providers/` and give it a lowercase, hyphenated name, like `imaging-software-team.md`. The file name becomes the page's URL.
2. Fill in the fields. List values must match `_data/taxonomy.yml` exactly, or the listing won't show up under that filter.
3. Replace the placeholder paragraph at the bottom with a 2–3 sentence description (300–500 characters).
4. Open a pull request. A reviewer merges it, and the listing goes live.

### Listing fields

Every field maps to a questionnaire question. The full list, with labels and question numbers, is in `_data/fields.yml`.

| Questionnaire section | Fields |
| --- | --- |
| Provider information (Q3–9) | `title`, `institution`, `school`, `unit`, `website`, `contact.name`, `contact.email`, and the description as the body text |
| Who you support (Q10–11) | `availability`, `eligible` |
| Services (Q13, Q42) | `services`, `strengths` (up to five, marked "Core strength" on the profile) |
| Technical capabilities (Q14–17) | `languages`, `databases`, `devops`, `hosting` |
| Research experience (Q18–22) | `research_frequency`, `research_areas`, `stages`, `grant_estimates`, `pre_award` |
| Data, security & compliance (Q23–25) | `data_types`, `compliance`, `security_approach` |
| Engagement model (Q26–30) | `engagement_types`, `project_sizes`, `durations`, `takeover`, `collaborate` |
| Cost & funding (Q31–33) | `funding`, `charges`, `minimum` |
| Availability & support (Q34–36) | `lead_time`, `production_support`, `support_coverage` |
| Sustainability (Q37–39) | `open_source`, `handoff_docs`, `maintenance` |
| Additional information (Q40–41) | `examples`, `notes` (Markdown allowed) |

Any list or single-answer field can also have a `<field>_other` text value for write-in answers. Listings also carry `updated` (date of the response or last review), `submitted_by` (who filled out the questionnaire, if different from the contact), and `sample: true` for fictional listings.

JHED IDs from the questionnaire are intentionally left out, since this repository and site are public.

## Adding a filter or field

1. Add the field to `_data/fields.yml` in the right section, and its allowed values to `_data/taxonomy.yml`. The profile page picks it up automatically.
2. Add it to each provider file and to `_includes/provider-template.md`.
3. To filter on it, add it to the `filters` list at the bottom of `_data/fields.yml`.

## Teams that only serve their own unit

Some teams are listed so RSSN knows the capability exists, even though they don't take outside requests. Availability answers marked `internal: true` in `_data/taxonomy.yml` ("No - our services are limited to our own department/unit" and "No - other") flag these teams. Their cards get a "Unit only" tag, and their profiles open with a "Not taking outside requests" banner.

On the home page they're hidden by default behind a pre-checked "Only show teams that take requests from outside their unit" box at the top of the filters. The result count says how many are hidden, with a link to show them. "Clear all" doesn't change this box.

## Design

Colors follow the [Johns Hopkins color guidelines](https://brand.jhu.edu/visual-identity/colors/). Heritage Blue leads, and the secondary palette only appears as the thin card accents that mark each school. Type uses Source Serif 4 and Work Sans, two of the university's [open-source typefaces](https://brand.jhu.edu/visual-identity/typography/), with Georgia and Tahoma as fallbacks. All styles are in `assets/css/site.css`.

## Previewing locally (optional)

You only need this to preview changes before pushing. With Ruby installed:

```sh
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000/RSSN_Provider_Inventory_Prototpye/.

## Moving the repository

If the repo is renamed or transferred (for example to an RSSN organization), update `repository`, `url`, and `baseurl` in `_config.yml`, then turn on Pages again under **Settings → Pages**.
