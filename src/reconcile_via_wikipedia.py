import random
from pathlib import Path
import datetime
import pandas as pd
import requests
from wdcuration import (
    query_wikidata,
    render_qs_url,
    NewItemConfig,
    WikidataDictAndKey,
    check_and_save_dict,
)


def get_new_pid2wikidata(NEW_PID):
    query = f'SELECT DISTINCT ?new_pid (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{NEW_PID} ?new_pid. }}'
    results = query_wikidata(query)
    return {a["new_pid"]: a["qid"] for a in results}


def get_wikidata_ids_from_wikipedia_pages(pages):
    # Wikidata API endpoint
    endpoint = "https://www.wikidata.org/w/api.php"

    # Query parameters
    params = {
        "action": "wbgetentities",
        "sites": "enwiki",
        "titles": "|".join(pages),
        "props": "",
        "format": "json",
    }

    # Make the API request
    response = requests.get(endpoint, params=params).json()

    # Extract the Wikidata IDs from the response
    wikidata_ids = {}
    for page_id, page_data in response["entities"].items():
        if page_data.get("sitelinks"):
            wikipedia_title = page_data["sitelinks"]["enwiki"]["title"]
            wikidata_id = page_id
            wikidata_ids[wikipedia_title] = wikidata_id

    # Print the result
    return wikidata_ids


def process_data(NEW_PID, DATA_DIR, reference_prefix):
    new_pid2wikidata = get_new_pid2wikidata(NEW_PID)

    df = pd.read_csv(
        DATA_DIR.joinpath("uberon_clean.csv"),
        dtype={"id": object},
        error_bad_lines=False,
    )
    current_wikidata_coverage = set(new_pid2wikidata.keys())
    ids_to_add = sorted(set(df["id"]) - current_wikidata_coverage)
    df = df.dropna(subset=["xrefs"])
    reference2new_id = {}
    for i, row in df.iterrows():
        xrefs = row["xrefs"]
        if isinstance(xrefs, str) and reference_prefix in xrefs:
            for xref in xrefs.split("|"):
                if reference_prefix in xref:
                    reference2new_id[xref.split(":")[1]] = row["id"]

    wikipedia_pages = [a.replace("_", " ") for a in list(reference2new_id.keys())]
    qids = get_wikidata_ids_from_wikipedia_pages(wikipedia_pages[0:3])
    print(qids)


def main():
    # Define constants
    HERE = Path(__file__).parent.resolve()
    DATA_DIR = HERE.parent.joinpath("data").resolve()
    RESULTS_DIR = HERE.parent.joinpath("results").resolve()
    REFERENCE_PREFIX = "Wikipedia"
    NEW_PID = "P1554"

    qs = process_data(NEW_PID, DATA_DIR, reference_prefix=REFERENCE_PREFIX)

    # Save QuickStatements to file
    filename = f"quickstatements_from_wikipedia.txt"
    with open(RESULTS_DIR.joinpath(filename), "w") as f:
        f.write(qs)

    # Print URL for QuickStatements commands
    print(render_qs_url(qs))


if __name__ == "__main__":
    main()
