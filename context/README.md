# Tableau Public → DuckDB Pipeline Scaffold

A [dlt](https://dlthub.com) pipeline that loads a Tableau Public author profile and all their published workbook metadata into a local DuckDB database — no credentials required.

## What it loads

| Table | Description |
|---|---|
| `profile` | Author bio, location, follower count, social links |
| `workbooks` | All published workbooks with view/favourite counts |
| `workbook_details` | Rich per-workbook metadata: dates, size, revision, luid |
| `workbook_views` | Individual sheets/dashboards within each workbook |

## Quick start

```bash
# 1. Install dependencies (requires uv)
uv sync

# 2. Run the pipeline (loads carole6045 profile by default)
uv run python tableau_public_pipeline.py

# 3. Query the result
uv run python -c "
import dlt
pipe = dlt.attach('tableau_public')
with pipe.sql_client() as c:
    for row in c.execute_sql('SELECT workbook_repo_url, total_views FROM tableau_public_data.workbooks ORDER BY total_views DESC LIMIT 5'):
        print(row)
"
```

## Change the profile

Edit `tableau_public_pipeline.py` and update the `profile_name` argument:

```python
load_info = pipeline.run(tableau_public_source(profile_name="your_tableau_username"))
```

Or pass it via dlt config in `.dlt/config.toml`:

```toml
[sources.tableau_public]
profile_name = "your_tableau_username"
```

## API reference

Uses the undocumented but stable Tableau Public REST API documented by the community:
<https://github.com/wjsutton/tableau_public_api>

No API key or authentication is needed — all endpoints are public.

## Extending

- **Add incremental loading**: the `workbooks` resource can be filtered by `updatedAt` once you have a baseline load.
- **Add more profiles**: wrap `tableau_public_source()` calls in a list and pass to `pipeline.run()`.
- **Change destination**: swap `destination="duckdb"` for `"motherduck"`, `"bigquery"`, `"snowflake"`, etc.

## Dependencies

- `dlt[duckdb]>=1.27.0`
- `requests` (bundled with dlt)
- Python ≥ 3.12
