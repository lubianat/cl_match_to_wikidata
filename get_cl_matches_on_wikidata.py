import json
from pathlib import Path

from wdcuration import query_wikidata
from wdcuration import get_wikidata_items_for_id

HERE = Path(__file__).parent.resolve()


def get_cl_matches_on_wikidata():

    existing_cl_terms = get_wikidata_items_for_id("P11302")
    HERE.joinpath("cl_on_wikidata.json").write_text(
        json.dumps(existing_cl_terms, indent=4, sort_keys=True)
    )


if __name__ == "__main__":
    get_cl_matches_on_wikidata()
