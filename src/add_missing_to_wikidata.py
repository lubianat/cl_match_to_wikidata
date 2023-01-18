from multiprocessing.sharedctypes import Value
import pathlib
from re import S
from this import d
import pandas as pd
from pathlib import Path
from wdcuration import get_wikidata_items_for_id
from wikidataintegrator import wdi_core, wdi_login
from login import *
import time


def main():
    HERE = Path(__file__).parent.resolve()
    DATA = HERE.parent.joinpath("data").resolve()

    BASE_SUPERCLASS = "Q7868"  # Cell
    SOURCE_DATABASE = "Q55118285"  # Cell Ontology
    SOURCE_DATABASE_PROPERTY = "P7963"
    BASE_DESCRIPTION = "cell type"
    BASE_TYPE = "Q189118"
    EDIT_SUMMARY = "Create item based on the Cell Ontology"

    df = pd.read_csv(f"{DATA}/cl_clean.csv", on_bad_lines="skip", dtype={"id": object})

    existing_terms = get_wikidata_items_for_id("P7963")
    uberon_to_wikidata_dict = get_wikidata_items_for_id("P1554")

    stated_in_source_statement = wdi_core.WDItemID(
        value=SOURCE_DATABASE, prop_nr="P248", is_reference=True
    )
    references = [[stated_in_source_statement]]
    wdi_login_object = wdi_login.WDLogin(WDUSER, WDPASS)

    for i, row in df.iterrows():
        current_id = str(row["id"]).strip()
        data_for_item = []

        if current_id not in existing_terms.keys():
            print(current_id)
            superclasses = []
            data_for_item = extract_anatomical_locations(
                uberon_to_wikidata_dict, references, row, data_for_item
            )

            superclasses = extract_parent_classes(
                BASE_SUPERCLASS, existing_terms, row, superclasses
            )

            database_id = row["id"]

            label = row["name"]

            data_for_item = extract_found_in_taxon(references, data_for_item, label)

            data_for_item.append(
                wdi_core.WDItemID(value=BASE_TYPE, prop_nr="P31", references=references)
            )
            for superclass_qid in superclasses:
                data_for_item.append(
                    wdi_core.WDItemID(
                        value=superclass_qid, prop_nr="P279", references=references
                    )
                )

            data_for_item.append(
                wdi_core.WDExternalID(
                    value=str(database_id), prop_nr=SOURCE_DATABASE_PROPERTY
                )
            )

            property_value_pairs_for_ids = []
            property_value_pairs_for_ids = extract_cross_references(
                row, property_value_pairs_for_ids
            )

            for property_value in property_value_pairs_for_ids:
                data_for_item.append(
                    wdi_core.WDExternalID(
                        value=property_value[1], prop_nr=property_value[0]
                    )
                )

            item = wdi_core.WDItemEngine(data=data_for_item, new_item=True)

            item.set_description(BASE_DESCRIPTION, lang="en")
            item.set_label(label=label, lang="en")
            try:
                print(item.wd_item_id)
                item.write(
                    wdi_login_object,
                    bot_account=False,
                    edit_summary=EDIT_SUMMARY,
                )

                existing_terms[database_id] = item.wd_item_id

            except:
                print(f"{label} already in Wikidata")
                continue
            print(f"Added {label} to Wikidata")

            time.sleep(0.1)


def extract_found_in_taxon(references, data_for_item, label):
    if "," in label:
        taxon_dict = {"mammalian": "Q7377"}

        taxon = label.split(",")[1].strip()
        if taxon in taxon_dict:
            raw_label = label.split(",")[0].strip()
            label = taxon + " " + raw_label
            taxon_dict = {"mammalian": "Q7377"}

            data_for_item.append(
                wdi_core.WDItemID(
                    value=taxon_dict[taxon],
                    prop_nr="P703",
                    references=references,
                )
            )

    return data_for_item


def extract_cross_references(row, property_value_pairs_for_ids):
    for xref in row["xrefs"].split("|"):
        try:
            prefix = xref.strip().split(":")[0]
            print(prefix)
            if prefix == "BTO":
                property_value_pairs_for_ids.append(("P5501", xref.strip()))
            elif prefix == "FMA":
                property_value_pairs_for_ids.append(
                    ("P1402", xref.strip().split(":")[1])
                )
            elif prefix in [
                "FAO",
                "CALOHA",
                "FBbt",
                "GO",
                "EMAPA",
                "MP",
                "https",
                "EFO",
                "ILX",
                "PMID",
            ]:
                pass
            else:
                pass
        except:
            pass
    return property_value_pairs_for_ids


def extract_parent_classes(BASE_SUPERCLASS, existing_terms, row, superclasses):
    for parent_id in row["parents"].split("|"):
        try:
            parent_id = parent_id.strip().replace(":", "_")
            superclass_qid = existing_terms[str(parent_id)]
        except:
            print(parent_id)
            print("No superclass found")
            superclass_qid = BASE_SUPERCLASS
        superclasses.append(superclass_qid)
    superclasses = list(set(superclasses))
    if len(superclasses) > 1:
        try:
            superclasses.remove("Q7868")
        except ValueError:
            pass
    return superclasses


def extract_anatomical_locations(
    uberon_to_wikidata_dict, references, row, data_for_item
):
    for parent_id in row["parents"].split("|"):
        try:
            if "BFO:0000050 some UBERON" in parent_id:
                uberon_id = parent_id.replace("BFO:0000050 some UBERON:", "")
                anatomical_location_qid = uberon_to_wikidata_dict[uberon_id]
                data_for_item.append(
                    wdi_core.WDItemID(
                        value=anatomical_location_qid,
                        prop_nr="P927",
                        references=references,
                    )
                )
        except:
            pass
    return data_for_item


if __name__ == "__main__":
    main()
