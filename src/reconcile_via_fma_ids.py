import json
import random
from pathlib import Path

import pandas as pd
from black import main
from wdcuration import query_wikidata, render_qs_url
from wdcuration.wdcuration import (NewItemConfig, WikidataDictAndKey,
                                   check_and_save_dict)

HERE = Path(__file__).parent.resolve()

fma2wikidata_result = query_wikidata(
    '  SELECT DISTINCT ?fma_id   (REPLACE(STR(?item), ".*Q", "Q") AS ?qid)  WHERE { ?item wdt:P1402 ?fma_id .      } '
)

fma2wikidata = {}
for a in fma2wikidata_result:
    fma2wikidata[a["fma_id"]] = a["qid"]


fma2cl_in_wikidata_result = query_wikidata(
    '  SELECT DISTINCT ?fma_id   (REPLACE(STR(?item), ".*Q", "Q") AS ?qid)  WHERE { ?item wdt:P1402 ?fma_id .  ?item wdt:P7963 ?id .    } '
)

fma2cl_in_wikidata = {}
for a in fma2cl_in_wikidata_result:
    fma2cl_in_wikidata[a["fma_id"]] = a["qid"]


HERE = Path(__file__).parent.resolve()
df = pd.read_csv("cl_clean.csv")
previous_cl_matches = json.loads(HERE.joinpath("cl_on_wikidata.json").read_text())
ids_to_add = list(set(df["id"]) - set(previous_cl_matches))
ids_to_add = sorted(ids_to_add)


fma2cl = {}
for id_to_add in ids_to_add:

    row = df[df["id"] == id_to_add]
    master_dict = {"cl_on_wikidata": previous_cl_matches}

    id_property_value_pairs = {"P7963": [row["id"].item()]}

    if row["xrefs"].item() == row["xrefs"].item():  # Test nan
        for xref in row["xrefs"].item().split("|"):
            if "FMA" in xref:
                fma2cl[xref.split(":")[1]] = row["id"].item()


matches_not_in_wikidata = list(set(fma2cl) - set(fma2cl_in_wikidata))

qs = ""

for fma_term in matches_not_in_wikidata:

    try:
        qid = fma2wikidata[fma_term]
        cl_id = fma2cl[fma_term]

        qs += f'{qid}|P7963|"{cl_id}"\n'
    except:
        continue

print(render_qs_url(qs))
