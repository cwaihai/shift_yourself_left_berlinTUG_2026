"""
Tableau Public pipeline – loads workbooks and metadata for a given profile into DuckDB.

API reference: https://github.com/wjsutton/tableau_public_api

Tables produced:
  - profile          : author bio, location, social links
  - workbooks        : list of published workbooks with view/favourite counts
  - workbook_details : rich per-workbook metadata (dates, size, revision, luid)
  - workbook_views   : individual sheets/dashboards within each workbook
"""

import dlt
import requests

BASE_URL = "https://public.tableau.com"
_HEADERS = {"User-Agent": "dlthub-tableau-pipeline/1.0"}


@dlt.source(name="tableau_public")
def tableau_public_source(profile_name: str = "carole6045"):

    @dlt.resource(write_disposition="replace")
    def profile():
        r = requests.get(
            f"{BASE_URL}/profile/api/{profile_name}",
            headers=_HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        # drop embedded workbooks array – covered by the workbooks resource
        data.pop("workbooks", None)
        yield data

    @dlt.resource(write_disposition="replace", primary_key="workbook_repo_url")
    def workbooks():
        start = 0
        count = 50
        while True:
            r = requests.get(
                f"{BASE_URL}/public/apis/workbooks",
                params={
                    "profileName": profile_name,
                    "start": start,
                    "count": count,
                    "visibility": "NON_HIDDEN",
                },
                headers=_HEADERS,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            items = data.get("contents", [])
            if not items:
                break
            yield from items
            next_index = data.get("nextIndex", -1)
            if next_index == -1:
                break
            start = next_index

    @dlt.transformer(
        data_from=workbooks,
        write_disposition="replace",
        primary_key="workbook_repo_url",
    )
    def workbook_details(workbook):
        repo_url = workbook["workbookRepoUrl"]
        r = requests.get(
            f"{BASE_URL}/profile/api/single_workbook/{repo_url}",
            headers=_HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        yield r.json()

    @dlt.transformer(
        data_from=workbooks,
        write_disposition="replace",
        primary_key="sheet_repo_url",
    )
    def workbook_views(workbook):
        repo_url = workbook["workbookRepoUrl"]
        r = requests.get(
            f"{BASE_URL}/profile/api/workbook/{repo_url}",
            headers=_HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        for view in r.json().get("viewInfos", []):
            view["workbookRepoUrl"] = repo_url
            yield view

    return profile, workbooks, workbook_details, workbook_views


pipeline = dlt.pipeline(
    pipeline_name="tableau_public",
    destination="duckdb",
    dataset_name="tableau_public_data",
    progress="log",
)

if __name__ == "__main__":
    load_info = pipeline.run(tableau_public_source())
    print(load_info)
    print("\nTables loaded:")
    with pipeline.sql_client() as client:
        for row in client.execute_sql(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'tableau_public_data' ORDER BY table_name"
        ):
            print(" -", row[0])
