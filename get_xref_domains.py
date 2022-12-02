from black import main
import pandas as pd
import json
from wdcuration.wdcuration import check_and_save_dict, WikidataDictAndKey, NewItemConfig
from pathlib import Path
import random
from itertools import chain


def main():
    HERE = Path(__file__).parent.resolve()
    df = pd.read_csv("cl_clean.csv")

    xrefs = df["xrefs"].dropna()

    xrefs = list(chain.from_iterable([a.split("|") for a in xrefs]))

    xref_domains = list(set([xref.split(":")[0] for xref in xrefs]))
    print(xref_domains)


if __name__ == "__main__":
    main()
