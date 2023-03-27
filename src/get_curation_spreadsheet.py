import pandas as pd
import json
from wdcuration import generate_curation_spreadsheet

from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()
RESULTS = HERE.parent.joinpath("results").resolve()


def main():
    generate_curation_spreadsheet(
        curation_table_path=DATA.joinpath("uberon_clean.csv"),
        identifiers_property="P1554",
        description_term_lookup="gallbladder",
        output_file_path="curation_sheet.csv",
    )


if __name__ == "__main__":
    main()
