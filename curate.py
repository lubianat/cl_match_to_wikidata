from black import main
import pandas as pd
import json
from wdcuration.wdcuration import check_and_save_dict
from pathlib import Path


def main():
    HERE = Path(__file__).parent.resolve()
    df = pd.read_csv("cl_clean.csv")
    previous_cl_matches = json.loads(HERE.joinpath("cl_on_wikidata.json").read_text())

    for i, row in df.iterrows():
        if row["id"] in previous_cl_matches:
            continue
        else:
            master_dict = {"cl_on_wikidata": previous_cl_matches}

            previous_cl_matches = check_and_save_dict(
                master_dict,
                "cl_on_wikidata",
                path=HERE,
                string=row["name"],
                dict_key=row["id"],
                excluded_types=["Q13442814", "Q2996394"],
            )


if __name__ == "__main__":
    main()
