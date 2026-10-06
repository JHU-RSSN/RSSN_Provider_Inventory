# RSSN Provider Inventory (prototype)

A prototype GitHub Pages site for the Research Software Support Network (RSSN) service provider inventory. It lists Johns Hopkins teams that support research software, data, and computing, with search, filters, and a profile page for each team.

**Live site:** https://jhu-rssn.github.io/RSSN_Provider_Inventory/

> The site follows Draft 3 of the RSSN Research IT Provider Questionnaire. Listings without `sample: true` come from pilot responses to Draft 2 (September 2026), carried over to Draft 3's fields; questions Draft 2 didn't ask are left blank, and every team will resubmit on the final form. Listings with `sample: true` are fictional examples kept to show how the directory works; delete them once real listings cover the same ground.

## How it works

The site is built with [Jekyll](https://jekyllrb.com/), which GitHub Pages runs automatically. There's no server or database. Every push to `main` rebuilds the site in a minute or two.

- Each team is one Markdown file in `_providers/`. Jekyll turns each file into a profile page at `/providers/<file-name>/`, plus a card and a table row on the home page.
- The home page's search, filters, sorting, and Cards/Table switch run in the browser (`assets/js/directory.js`) using data Jekyll writes into the page at build time.
- `_data/fields.yml` lists every listing field, grouped the way the questionnaire groups them. It drives the profile page, the search data, the filter panel, and the import script.
- Allowed values for every list field live in `_data/taxonomy.yml`. They mirror the RSSN Research IT Provider Questionnaire.

## Importing questionnaire responses

`scripts/import_responses.py` turns the Microsoft Forms Excel export of the Draft 3 questionnaire into listings, one file per response:

```sh
pip install openpyxl pyyaml
python scripts/import_responses.py "Research Software Support Network ... .xlsx"
```

It skips listings that already exist (add `--overwrite` to replace them). Answers are matched to the values in `_data/taxonomy.yml`. Anything that doesn't match, like an "Other (please specify)" answer, is kept as text in that field's `_other` key. The service grids (Q12–15) are recognized by their answers (Not offered / Offered / Area of strength), so the exact column headings Forms uses don't matter. For each file, the script lists what to check: write-ins, more than five areas of strength, or "None of the above" chosen alongside other compliance answers. Review each new file before committing, especially `school` and `unit`, since the form collects those as one free-text answer.

The script was tested against a mock Draft 3 export. Run it on the first real export and check the "no column found" notes before trusting the output.

If the questionnaire adds or renames an answer choice, add it to `_data/taxonomy.yml` first so it imports as a filterable value instead of a write-in.

## Adding or updating a listing by hand

Contributors don't need to clone anything. The site's [Add your service](https://jhu-rssn.github.io/RSSN_Provider_Inventory/add-your-service/) page walks them through proposing a change on github.com. Every provider profile also has a "Suggest an edit on GitHub" link.

1. Copy `_includes/provider-template.md` into `_providers/` and give it a lowercase, hyphenated name, like `imaging-software-team.md`. The file name becomes the page's URL.
2. Fill in the fields. List values must match `_data/taxonomy.yml` exactly, or the listing won't show up under that filter.
3. Replace the placeholder text at the bottom with the team's optional paragraph (Q18, about 500 characters), or delete it.
4. Open a pull request. A reviewer merges it, and the listing goes live.

### Listing fields

Every field maps to a questionnaire question. The full list, with labels and question numbers, is in `_data/fields.yml`.

| Questionnaire section (Draft 3) | Fields |
| --- | --- |
| Provider information (Q1–8) | `contact.name`, `contact.email`, `submitted_by`, `institution`, `school`, `unit`, `title`, `website` |
| Who you support (Q9–11) | `team_type`, `availability`, `eligible` |
| Services & expertise (Q12–17) | `services` (everything marked Offered or Area of strength), `strengths` (Area of strength, up to five), `services_other` (Q16), `examples` (Q17) |
| Optional paragraph (Q18) | the body text below the front matter |
| Technical capabilities (Q19–23) | `hands_on`, `languages`, `databases`, `devops`, `hosting` |
| Research experience (Q24–28) | `research_areas`, `stages`, `grant_estimates`, `pre_award`, `consult_scope` |
| Data, security & compliance (Q29–31) | `data_types`, `compliance`, `security_approach` |
| Engagement model (Q32–36) | `engagement_types`, `project_sizes`, `durations`, `takeover`, `collaborate` |
| Cost & funding (Q37–41) | `cost`, `free_limit`, `charges`, `minimum`, `funding` |
| Availability & support (Q42–45) | `accepting`, `lead_time`, `production_support`, `support_coverage` |
| Open source & sustainability (Q46–48) | `open_source`, `handoff_docs`, `maintenance` |
| Additional information (Q49) | `notes` |

### The summary

Each card and profile opens with a summary built from the answers, as Q18 promises respondents: unit and team name, team type, availability, areas of strength, cost, lead time, and whether the team is accepting new work. The wording comes from the `phrase` values in `_data/taxonomy.yml`, and the template is `_includes/summary.html`. Cards use a shorter version (team type and cost), since they already show the rest.

### Pausing new requests

`accepting` (Q42) is its own field so a team can pause or resume requests with a one-line edit: set it to `"Not at this time"` and the card and table show it under "Taking new work," and the profile gets a banner.

Any list or single-answer field can also have a `<field>_other` text value for write-in answers. Listings also carry `updated` (date of the response or last review), `submitted_by` (who filled out the questionnaire, if different from the contact), and `sample: true` for fictional listings.

JHED IDs from the questionnaire are intentionally left out, since this repository and site are public.

## Adding a filter or field

1. Add the field to `_data/fields.yml` in the right section, and its allowed values to `_data/taxonomy.yml`. The profile page picks it up automatically.
2. Add it to each provider file, then run `python scripts/make_template.py` to rebuild `_includes/provider-template.md`.
3. To filter on it, add it to the `filters` list at the bottom of `_data/fields.yml`.

## Teams that only serve their own unit

Some teams are listed so RSSN knows the capability exists, even though they don't take outside requests. Availability answers marked `internal: true` in `_data/taxonomy.yml` ("No - our services are limited to our own department/unit") flag these teams. On cards and in the table their "Available to" value is shown in plum with a lock, and their profiles open with a "Not taking outside requests" banner.

On the home page they're hidden by default behind a pre-checked "Only show teams that take requests from outside their unit" box at the top of the filters. The result count says how many are hidden, with a link to show them. "Clear all" doesn't change this box.

## Cards and table views

The home page shows cards by default. The Table button switches to a table with one row per team: name and school, top three areas of strength, available to, lead time, and taking new work. Each row's arrow opens a details row (the team's description, all strengths, languages, and data types); "Expand all" opens every visible row. Table rows come from `_includes/table-row.html`, cards from `_includes/card.html`, and both use `_includes/availability.html` and `_includes/accepting.html` for those values.

- **Filters, search, view, and sort all live in the page address** (`?view=table&sort=lead_time&dir=desc`), so they survive switching views, refreshing, and sharing a link.
- **Sorting** works from the Sort menu above either view or from the table's column headers (click again to reverse). Team and School sort A–Z. Available to, Lead time, and Taking new work sort in the order their answers are listed in `_data/taxonomy.yml`, so reordering a list there changes the sort. "Varies based on project" and "It's complicated" sort after the real answers, and blank answers ("Not reported") sort last, in either direction. Ties sort by team name.
- **Default order** lists real listings A–Z, then sample listings. Once a sort is chosen, samples mix in with the real listings.
- **Phones** (720px wide or less) show cards only; the Table button is hidden there.
- **Teams that don't do hands-on technical work** (Q19 = "No") show N/A for languages in the table and for the whole Technical capabilities section on their profile, instead of leaving those questions blank.

## Design

Colors follow the [Johns Hopkins color guidelines](https://brand.jhu.edu/visual-identity/colors/). Heritage Blue leads, and the secondary palette only appears as the thin card accents that mark each school. Type uses Source Serif 4 and Work Sans, two of the university's [open-source typefaces](https://brand.jhu.edu/visual-identity/typography/), with Georgia and Tahoma as fallbacks. All styles are in `assets/css/site.css`.

## Previewing locally (optional)

You only need this to preview changes before pushing. With Ruby installed:

```sh
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000/RSSN_Provider_Inventory/.

## Moving the repository

If the repo is renamed or transferred (for example to an RSSN organization), update `repository`, `url`, and `baseurl` in `_config.yml`, then turn on Pages again under **Settings → Pages**.
