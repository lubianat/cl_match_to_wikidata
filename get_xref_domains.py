from itertools import chain

import pandas as pd
from black import main


def main():
    df = pd.read_csv("cl_clean.csv")
    xrefs = df["xrefs"].dropna()
    xrefs = list(chain.from_iterable([a.split("|") for a in xrefs]))
    xref_domains = list(set([xref.split(":")[0] for xref in xrefs]))
    print(xref_domains)


if __name__ == "__main__":
    main()
