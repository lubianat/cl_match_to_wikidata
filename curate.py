from black import main
import pandas as pd
import json
from wdcuration.wdcuration import check_and_save_dict, WikidataDictAndKey, NewItemConfig
from pathlib import Path
import random








def convert_xref_to_wikidata(xref)
    "Converts an xref to a property value pair for Wikidata"

    if 



def main():
    HERE = Path(__file__).parent.resolve()
    df = pd.read_csv("cl_clean.csv")
    previous_cl_matches = json.loads(HERE.joinpath("cl_on_wikidata.json").read_text())

    ids_to_add = list(set(df["id"]) - set(previous_cl_matches))

    ids_to_add = sorted(ids_to_add)

    #random.shuffle(ids_to_add)

    try:
        for id_to_add in ids_to_add:

            row = df[df["id"] == id_to_add]
            master_dict = {"cl_on_wikidata": previous_cl_matches}

            id_property_value_pairs = {"P7963": [row["id"].item()]}

            for xref in row["xref"].split("|"):

              key, value = convert_xref_to_wikidata(xref)
              if key in id_property_value_pairs:
                id_property_value_pairs[key].append(value)
              else: 
                id_property_value_pairs[key] = value

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
                    item_property_value_pairs={"P31": ["Q189118"]},
                ),
                excluded_types=["Q13442814", "Q2996394", "Q112193867", "Q187685"],
            )

            dict_and_key.add_key()
    except KeyboardInterrupt as e:
        dict_and_key.save_dict()

    dict_and_key.save_dict()


if __name__ == "__main__":
    main()
