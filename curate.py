import json
import random
from pathlib import Path

import pandas as pd
from black import main
from wdcuration.wdcuration import NewItemConfig, WikidataDictAndKey, render_qs_url


def main():
    HERE = Path(__file__).parent.resolve()
    df = pd.read_csv("cl_clean.csv")
    previous_cl_matches = json.loads(HERE.joinpath("cl_on_wikidata.json").read_text())
    ids_to_add = list(set(df["id"]) - set(previous_cl_matches))
    ids_to_add = sorted(ids_to_add)
    random.shuffle(ids_to_add)

    cell_dict = {
        "macrophage": "Q184204",
        "neuron": "Q43054",
        "endothelial cell": "Q11394395",
        "T cell": "Q193529",
    }

    to_create = ""
    try:
        for id_to_add in ids_to_add:

            row = df[df["id"] == id_to_add]
            master_dict = {"cl_on_wikidata": previous_cl_matches}
            id_property_value_pairs = {"P7963": [row["id"].item()]}
            item_property_value_pairs = {"P31": ["Q189118"]}
            if "human" in row["name"].item():
                item_property_value_pairs["P703"] = ["Q15978631"]
            for key, value in cell_dict.items():
                if key in row["name"].item():
                    item_property_value_pairs["P279"] = [value]

            if row["xrefs"].item() == row["xrefs"].item():  # Test nan
                print(row["xrefs"].item())
                for xref in row["xrefs"].item().split("|"):
                    try:
                        key_value_tuple = convert_id_to_wikidata(xref)
                        key = key_value_tuple[0]
                        value = key_value_tuple[1]
                        if key in id_property_value_pairs:
                            id_property_value_pairs[key].append(value)
                        else:
                            id_property_value_pairs[key] = [value]
                    except:
                        continue

            dict_and_key = WikidataDictAndKey(
                master_dict=master_dict,
                dict_name="cl_on_wikidata",
                path=HERE,
                dict_key=row["id"].item(),
                search_string=row["name"].item(),
                new_item_config=NewItemConfig(
                    labels={"en": row["name"].item()},
                    descriptions={"en": "cell type"},
                    id_property_value_pairs=id_property_value_pairs,
                    item_property_value_pairs=item_property_value_pairs,
                ),
                excluded_types=[
                    "Q13442814",
                    "Q2996394",
                    "Q112193867",
                    "Q187685",
                    "Q5058355",
                ],
            )

            to_create += dict_and_key.add_key(return_qs=True) + "\n"
    except KeyboardInterrupt as e:
        dict_and_key.save_dict()
        print(render_qs_url(to_create))
        return ""

    dict_and_key.save_dict()
    print(render_qs_url(to_create))
    return ""


def convert_id_to_wikidata(id_in_obo):

    domain = id_in_obo.split(":")[0]
    id_string = id_in_obo.split(":")[1]

    domain2statements = {
        "FMA": {"property": "P1402", "formatting_function": str},
        "BTO": {"property": "P5501", "formatting_function": lambda a: "BTO:" + a},
    }
    if domain in domain2statements:

        property_value_pair = (
            domain2statements[domain]["property"],
            domain2statements[domain]["formatting_function"](id_string),
        )
    else:
        property_value_pair = ()

    return property_value_pair


if __name__ == "__main__":
    main()
