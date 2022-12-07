import json
from pathlib import Path

from wdcuration import query_wikidata

HERE = Path(__file__).parent.resolve()

existing_cl_terms = query_wikidata(
    '  SELECT DISTINCT ?id   (REPLACE(STR(?item), ".*Q", "Q") AS ?qid)  WHERE { ?item wdt:P7963 ?id . } '
)

existing_cl_terms_dict = {}
for a in existing_cl_terms:
    existing_cl_terms_dict[a["id"]] = a["qid"]

HERE.joinpath("cl_on_wikidata.json").write_text(
    json.dumps(existing_cl_terms_dict, indent=4, sort_keys=True)
)
