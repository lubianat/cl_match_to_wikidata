import pandas as pd
import json
from pathlib import Path
from wdcuration import generate_curation_spreadsheet


def main():
    generate_curation_spreadsheet(
        curation_table_path="cl_clean.csv",
        identifiers_property="P7963",
        output_file_path="curation_sheet.csv",
        fixed_type="Q189118",
    )


if __name__ == "__main__":
    main()
