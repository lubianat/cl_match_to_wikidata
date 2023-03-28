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
import time
from tqdm import tqdm


def get_new_pid2wikidata(NEW_PID):
    query = f'SELECT DISTINCT ?new_pid (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{NEW_PID} ?new_pid. }}'
    results = query_wikidata(query)
    return {a["new_pid"]: a["qid"] for a in results}


def get_ids_from_pages(pages):
    """
    Returns a dictionary with page titles as keys and Wikidata QIDs as values
    """
    url = "https://en.wikipedia.org/w/api.php?action=query"
    params = {
        "format": "json",
        "prop": "pageprops",
        "ppprop": "wikibase_item",
        "redirects": "1",
        "titles": "|".join(pages),
    }
    r = requests.get(url, params)
    data = r.json()
    id_dict = {}
    for key, values in data["query"]["pages"].items():
        title = values["title"]
        if "pageprops" in values:
            qid = values["pageprops"]["wikibase_item"]
            id_dict[title] = qid

    return id_dict


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def process_data(NEW_PID, DATA_DIR, reference_prefix):
    new_pid2wikidata = get_new_pid2wikidata(NEW_PID)

    df = pd.read_csv(
        DATA_DIR.joinpath("uberon_clean.csv"),
        dtype={"id": object},
        error_bad_lines=False,
    )
    current_wikidata_coverage = set(new_pid2wikidata.keys())
    df = df.dropna(subset=["xrefs"])
    reference2new_id = {}
    for i, row in df.iterrows():
        xrefs = row["xrefs"]
        if isinstance(xrefs, str) and reference_prefix in xrefs:
            for xref in xrefs.split("|"):
                if reference_prefix in xref:
                    reference2new_id[xref.split(":")[1]] = row["id"]

    wikipedia_pages = [a.replace("_", " ") for a in list(reference2new_id.keys())]
    pages_with_wikidata_ids = {}

    size = int(len(wikipedia_pages) / 50)
    for pages in tqdm(chunks(wikipedia_pages, 50), total=size):
        pages_with_wikidata_ids.update(get_ids_from_pages(pages))
        time.sleep(0.2)

    print(pages_with_wikidata_ids)

    qs = ""
    for reference_id, new_id in reference2new_id.items():
        if new_id not in new_pid2wikidata.keys():
            if reference_id.replace("_", " ") in pages_with_wikidata_ids.keys():
                qid = pages_with_wikidata_ids[reference_id.replace("_", " ")]
                qs += f'{qid}|{NEW_PID}|"{new_id}"|S887|Q117319166|S248|Q7876491\n'

    return qs


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
