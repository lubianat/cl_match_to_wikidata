import pandas as pd
import json
from pathlib import Path
from wdcuration import search_wikidata, get_wikidata_items_for_id
import time
from tqdm import tqdm


def main():
    generate_curation_spreadsheet()


def generate_curation_spreadsheet(
    identifiers_property="P7963",
    curation_table="cl_clean.csv",
    output_file="curation_sheet.csv",
): 
    cl_on_wikidata = get_wikidata_items_for_id(identifiers_property)

    full_df = pd.read_csv(curation_table)

    not_on_wikidata = full_df[~full_df["id"].isin(cl_on_wikidata.keys())]
    excluded_types = {
        "Q13442814": "",
        "Q2996394": "",
        "Q112193867": "",
        "Q187685": "",
        "Q59582589": "",
        "Q21014462": "",
        "Q5058355": "cell component",
        "Q14860489": "molecular function",
        "Q30612": "clinical trial",
        "Q16521": "species",
        "Q8054": "protein",
        "Q7187": "gene",
    }.keys()

    wikidata_ids = []
    wikidata_labels = []
    wikidata_descriptions = []

    try:
        for i, row in tqdm(not_on_wikidata.iterrows(), total=len(not_on_wikidata)):
            guess_now = search_wikidata(
                search_term=row["name"], excluded_types=excluded_types
            )
            wikidata_ids.append(guess_now["id"])
            wikidata_labels.append(guess_now["label"])
            wikidata_descriptions.append(guess_now["description"])
            time.sleep(0.1)

    except KeyboardInterrupt as e:
        for j, row in tqdm(not_on_wikidata.iterrows(), total=len(not_on_wikidata)):
            if j >= i:
                wikidata_ids.append("NONE")
                wikidata_labels.append("NONE")
                wikidata_descriptions.append("NONE")
        print(e)

    not_on_wikidata["wikidata_id"] = wikidata_ids
    not_on_wikidata["wikidata_label"] = wikidata_labels
    not_on_wikidata["wikidata_description"] = wikidata_descriptions
    not_on_wikidata.to_csv(output_file)


if __name__ == "__main__":
    main()
