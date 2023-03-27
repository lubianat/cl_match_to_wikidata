import random
from pathlib import Path
import datetime
import pandas as pd

from wdcuration import (
    query_wikidata,
    render_qs_url,
    NewItemConfig,
    WikidataDictAndKey,
    check_and_save_dict,
)


def get_reference2wikidata(REFERENCE_PID):
    query = f'SELECT DISTINCT ?reference_id (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{REFERENCE_PID} ?reference_id. }}'
    results = query_wikidata(query)
    return {a["reference_id"]: a["qid"] for a in results}


def get_new_pid2wikidata(NEW_PID):
    query = f'SELECT DISTINCT ?new_pid (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{NEW_PID} ?new_pid. }}'
    results = query_wikidata(query)
    return {a["new_pid"]: a["qid"] for a in results}


def get_reference2new_id_in_wikidata(REFERENCE_PID, NEW_PID):
    query = f'SELECT DISTINCT ?reference_id (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{REFERENCE_PID} ?reference_id. ?item wdt:{NEW_PID} ?new_id. }}'
    results = query_wikidata(query)
    return {a["reference_id"]: a["qid"] for a in results}


def get_matches_not_in_wikidata(reference2new_id, reference2new_id_in_wikidata):
    return set(reference2new_id) - set(reference2new_id_in_wikidata)


def get_reference2new_id(df, ids_to_add, reference_prefix="FMA"):
    reference2new_id = {}
    for id_to_add in ids_to_add:
        row = df[df["id"] == id_to_add]
        xrefs = row["xrefs"].item()
        if isinstance(xrefs, str) and reference_prefix in xrefs:
            for xref in xrefs.split("|"):
                if reference_prefix in xref:
                    reference2new_id[xref.split(":")[1]] = row["id"].item()
    return reference2new_id


def generate_qs_triple(qid, new_id, NEW_PID):
    return f'{qid}|{NEW_PID}|"{new_id}"\n'


def process_data(REFERENCE_PID, NEW_PID, DATA_DIR, reference_prefix):
    reference2wikidata = get_reference2wikidata(REFERENCE_PID)
    new_pid2wikidata = get_new_pid2wikidata(NEW_PID)
    reference2new_id_in_wikidata = get_reference2new_id_in_wikidata(
        REFERENCE_PID, NEW_PID, reference_prefix
    )

    df = pd.read_csv(
        DATA_DIR.joinpath("uberon_clean.csv"),
        dtype={"id": object},
        error_bad_lines=False,
    )
    current_wikidata_coverage = set(new_pid2wikidata.keys())
    ids_to_add = sorted(set(df["id"]) - current_wikidata_coverage)

    reference2new_id = get_reference2new_id(df, ids_to_add)

    matches_not_in_wikidata = get_matches_not_in_wikidata(
        reference2new_id, reference2new_id_in_wikidata
    )

    qs = ""
    for reference_term in matches_not_in_wikidata:
        try:
            qid = reference2wikidata[reference_term]
            new_id = reference2new_id[reference_term]

            qs += generate_qs_triple(qid, new_id, NEW_PID)
        except KeyError:
            pass
    return qs


def main():
    # Define constants
    HERE = Path(__file__).parent.resolve()
    DATA_DIR = HERE.parent.joinpath("data").resolve()
    RESULTS_DIR = HERE.parent.joinpath("results").resolve()
    REFERENCE_PID = "P1402"
    REFERENCE_PREFIX = "FMA"
    NEW_PID = "P1554"

    qs = process_data(
        REFERENCE_PID, NEW_PID, DATA_DIR, reference_prefix=REFERENCE_PREFIX
    )

    # Save QuickStatements to file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"quickstatements_{REFERENCE_PID}_{NEW_PID}_{timestamp}.txt"
    with open(RESULTS_DIR.joinpath(filename), "w") as f:
        f.write(qs)

    # Print URL for QuickStatements commands
    print(render_qs_url(qs))


if __name__ == "__main__":
    main()
