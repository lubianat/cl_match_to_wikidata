from multiprocessing.sharedctypes import Value
import pathlib
from re import S
from this import d
import pandas as pd
from pathlib import Path
from wdcuration import get_wikidata_items_for_id, lookup_id
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
        if row["name"] != row["name"]:  # Test nan
            continue
        current_id = str(row["id"]).strip()
        data_for_item = []

        if current_id not in existing_terms.keys():
            print(current_id)
            superclasses = []
            data_for_item = extract_anatomical_locations(
                uberon_to_wikidata_dict, references, row, data_for_item
            )
            data_for_item = extract_parent_classes(
                BASE_SUPERCLASS,
                existing_terms,
                row,
                superclasses,
                data_for_item,
                references,
            )
            database_id = row["id"]
            data_for_item.append(
                wdi_core.WDItemID(value=BASE_TYPE, prop_nr="P31", references=references)
            )
            data_for_item.append(
                wdi_core.WDExternalID(
                    value=str(database_id), prop_nr=SOURCE_DATABASE_PROPERTY
                )
            )
            data_for_item = extract_and_add_cross_references(
                row, data_for_item, references
            )
            label = row["name"]
            data_for_item, label = extract_found_in_taxon(
                references, data_for_item, label
            )
            item = wdi_core.WDItemEngine(data=data_for_item, new_item=True)

            if row["aliases"] == row["aliases"]:
                for alias in row["aliases"].split("|"):
                    item.set_aliases([alias], append=True)

            item.set_description(BASE_DESCRIPTION, lang="en")
            item.set_label(label=label, lang="en")
            try:
                item.write(
                    wdi_login_object,
                    bot_account=False,
                    edit_summary=EDIT_SUMMARY,
                )
                existing_terms[database_id] = item.wd_item_id
            except:
                pass
            print(f"Added {label} to Wikidata")

            time.sleep(0.1)


def extract_and_add_cross_references(row, data_for_item, references):
    property_value_pairs_for_ids = []
    if row["xrefs"] != row["xrefs"]:
        return data_for_item
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
            elif prefix == "PMID":
                publication = lookup_id(xref.strip().split(":")[1])
                data_for_item.append(
                    wdi_core.WDItemID(
                        value=publication,
                        prop_nr="P1343",
                        references=references,
                    )
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

    for property_value in property_value_pairs_for_ids:
        data_for_item.append(
            wdi_core.WDExternalID(value=property_value[1], prop_nr=property_value[0])
        )
    return data_for_item


def extract_found_in_taxon(references, data_for_item, label):
    if label != label:
        return data_for_item, label
    taxon_dict = {
        "mammalian": "Q7377",
        "Nematoda": "Q5185",
        "Protostomia": "Q5171",
        "Vertebrata": "Q25241",
        "Fungi": "Q764",
        "Endopterygota": "Q304358",
        "sensu Mus": "Q39275",
        "human": "Q15978631",
    }
    for taxon_name in taxon_dict.keys():
        if taxon_name in label:
            data_for_item.append(
                wdi_core.WDItemID(
                    value=taxon_dict[taxon_name],
                    prop_nr="P703",
                    references=references,
                )
            )
    if "," in label:

        taxon = label.split(",")[-1].strip()
        if taxon in taxon_dict:
            raw_label = label.split(",")
            raw_label = ",".join(raw_label[:-1]).strip()
            label = taxon + " " + raw_label

    return data_for_item, label


def extract_parent_classes(
    BASE_SUPERCLASS, existing_terms, row, superclasses, data_for_item, references
):
    if row["parents"] != row["parents"]:
        return data_for_item
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

    for superclass_qid in superclasses:
        data_for_item.append(
            wdi_core.WDItemID(
                value=superclass_qid, prop_nr="P279", references=references
            )
        )

    return data_for_item


def extract_anatomical_locations(
    uberon_to_wikidata_dict, references, row, data_for_item
):
    if row["parents"] != row["parents"]:
        return data_for_item
    for parent_id in row["parents"].split("|"):
        try:
            if "BFO:0000050 some UBERON" in parent_id:
                uberon_id = parent_id.replace("BFO:0000050 some UBERON:", "")
                uberon_id = uberon_id.replace("BFO:0000050 some UBERON_", "")
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
