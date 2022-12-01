from wdcuration import query_wikidata
import json
from pathlib import Path
import pandas as pd
import json
from wdcuration.wdcuration import check_and_save_dict
from pathlib import Path


def main():
    HERE = Path(__file__).parent.resolve()

    all_cl_matches = json.loads(HERE.joinpath("cl_on_wikidata.json").read_text())

    existing_cl_matches = query_wikidata(
        '  SELECT DISTINCT ?id   (REPLACE(STR(?item), ".*Q", "Q") AS ?qid)  WHERE { ?item wdt:P7963 ?id . } '
    )

    existing_cl_matches_dict = {}
    for a in existing_cl_matches:
        existing_cl_matches_dict[a["id"]] = a["qid"]

    new_keys = all_cl_matches.keys() - existing_cl_matches_dict.keys()
    qs = ""
    for key in new_keys:
        qs += f'{all_cl_matches[key]}|P7963|"{key}"' + "\n"

    print(qs)


if __name__ == "__main__":
    main()
