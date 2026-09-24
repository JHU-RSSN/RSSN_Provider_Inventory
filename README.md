# RSSN Provider Inventory (prototype)

A prototype GitHub Pages site for the Research Software Support Network (RSSN) service provider inventory. It lists Johns Hopkins teams that support research software, data, and computing, with search, filters, and a profile page for each team.

**Live site:** https://meganforbes.github.io/RSSN_Provider_Inventory_Prototpye/

> The listings in `_providers/` are sample data for review. They don't describe real teams or contacts.

## How it works

The site is built with [Jekyll](https://jekyllrb.com/), which GitHub Pages runs automatically. There's no server or database. Every push to `main` rebuilds the site in a minute or two.

- Each team is one Markdown file in `_providers/`. Jekyll turns each file into a profile page at `/providers/<file-name>/` and a card on the home page.
- The home page's search and filters run in the browser (`assets/js/directory.js`) using data Jekyll writes into the page at build time.
- Allowed values for institutions, schools, services, and eligibility live in `_data/taxonomy.yml`. They mirror the RSSN Research IT Provider Questionnaire.

## Adding or updating a listing

Contributors don't need to clone anything. The site's [Add your service](https://meganforbes.github.io/RSSN_Provider_Inventory_Prototpye/add-your-service/) page walks them through proposing a change on github.com. Every provider profile also has a "Suggest an edit on GitHub" link.

To add a listing by hand:

1. Copy `_includes/provider-template.md` into `_providers/` and give it a lowercase, hyphenated name, like `imaging-software-team.md`. The file name becomes the page's URL.
2. Fill in the fields. List values must match `_data/taxonomy.yml` exactly, or the listing won't show up under that filter.
3. Replace the placeholder paragraph at the bottom with a 2–3 sentence description (300–500 characters).
4. Open a pull request. A reviewer merges it, and the listing goes live.

### Listing fields

| Field | Questionnaire question | Notes |
| --- | --- | --- |
| `title` | Team or service name | |
| `institution` | Institution | `JHU`, `JHHS`, or `Joint JHU/JHHS` |
| `school` | School, division, department, or organizational unit | Schools in `taxonomy.yml` get a colored card accent |
| `unit` | (same question) | Department or unit within the school |
| `website` | Website or service information URL | Optional. Use `""` for none |
| `contact.name`, `contact.email` | Primary contact name and email | |
| `availability` | Available to researchers outside your unit? | Short labels listed in `taxonomy.yml` |
| `eligible` | Which researchers or organizations can engage your team? | List |
| `services` | What services does your team provide? | List |
| (body text) | Briefly describe your team | 300–500 characters |

JHED IDs from the questionnaire are intentionally left out, since this repository and site are public.

## Adding a filter or field

1. Add the field to each provider file (and to `_includes/provider-template.md`).
2. If it has a fixed set of values, add them to `_data/taxonomy.yml`.
3. Show it on the profile in `_layouts/provider.html`, and on cards in `_includes/card.html` if needed.
4. To filter on it, add it to the provider data in `index.html` and to the `GROUPS` list at the top of `assets/js/directory.js`.

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
