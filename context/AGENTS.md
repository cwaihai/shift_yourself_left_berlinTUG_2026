# Tableau Public → DuckDB — Agent Context

## What this scaffold does

Loads Tableau Public author profiles and workbook metadata into DuckDB using [dlt](https://dlthub.com).
No authentication required — all Tableau Public API endpoints are open.

## Source API

- **Base URL**: `https://public.tableau.com`
- **Auth**: None (public endpoints, `User-Agent` header only)
- **Community API reference**: <https://github.com/wjsutton/tableau_public_api>

### Endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /profile/api/{profile_name}` | Author profile (bio, follower count, social links) |
| `GET /public/apis/workbooks?profileName=…&start=…&count=…` | Paginated workbook list with view/favourite counts |
| `GET /profile/api/single_workbook/{workbookRepoUrl}` | Rich metadata for one workbook |
| `GET /profile/api/workbook/{workbookRepoUrl}` | Sheets/views within one workbook |

Pagination: `workbooks` uses cursor-style `nextIndex` (-1 signals last page).

## dlt resources

```
tableau_public_source(profile_name)
  ├── profile           (write_disposition=replace)
  ├── workbooks         (write_disposition=replace, primary_key=workbook_repo_url)
  ├── workbook_details  (transformer from workbooks)
  └── workbook_views    (transformer from workbooks, primary_key=sheet_repo_url)
```

`workbook_details` and `workbook_views` are **transformers** — they receive each workbook item and fetch additional detail. This produces one HTTP request per workbook, so large profiles will have many requests.

## Key implementation notes

- Drop the `workbooks` key from the profile response — it duplicates data already in the `workbooks` resource.
- `workbookRepoUrl` is the stable join key between `workbooks`, `workbook_details`, and `workbook_views`.
- All resources use `write_disposition="replace"` — full refresh on every run.

## Destination

Default: `duckdb` (local file `tableau_public.duckdb` in cwd).
Dataset: `tableau_public_data`.

Swap destination to `motherduck`, `bigquery`, etc. without changing source code.

## Tasks an agent can do with this scaffold

1. **Run the pipeline** — `uv run python tableau_public_pipeline.py`
2. **Change the profile** — update `profile_name` in `.dlt/config.toml` or pass as argument
3. **Add incremental loading** — filter workbooks by `updatedAt`, add `dlt.sources.incremental`
4. **Explore loaded data** — use `explore-data` skill after a successful run
5. **Add a new endpoint** — use `new-endpoint` or `add-table` skill (e.g. favourites, followers)
6. **Deploy** — use `dlthub-platform-workflow` skill to schedule on dltHub

## Common failure modes

| Error | Likely cause | Fix |
|---|---|---|
| 429 Too Many Requests | Large profile, too many transformer calls | Add `time.sleep(0.2)` between transformer requests |
| 404 on workbook detail | Workbook was deleted after listing | Skip with `try/except` in transformer |
| Empty `contents` list | Wrong `profile_name` or profile is private | Verify name at `https://public.tableau.com/app/profile/{name}` |

## Security

No credentials needed. Never store or request Tableau credentials — the public API requires none.
