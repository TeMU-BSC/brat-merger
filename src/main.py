import argparse
import os
from entities import Entity
from utils import Utils
from merge import Merger
from writer import Write


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="analysis")
    parser.add_argument('--data', help='Input of ANN directories (SECTION AND VARIABLES).')

    args = parser.parse_args()

    section_root = os.path.join(Utils.parentDir, "documents", "ANN_SECTION")

    if args.data is not None:
        section_root = args.data

    section, validated_files = Entity.get_section(section_root)

    variable_root = section_root.replace("ANN_SECTION", "ANN_VARIABLE")

    variables, variables_hash = Entity.get_variables(variable_root, validated_files)

    section_variable = Merger.merged_dic(section, variables)

    section_variable = Merger.diagnostic_filterring(section_variable)

    final_root = section_root.replace("ANN_SECTION", "ANN_FINAL")

    Write.save_accepted_variables(section_variable, variables_hash, final_root)
