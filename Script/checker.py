import argparse
from os import listdir
import os



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="analysis")
    parser.add_argument('--set', help='Which set is going to compare')

    args = parser.parse_args()


    dir1 = "/home/siabar/30yamak/git/BratMerger/documents/ANN_FINAL"
    dir2 = "/home/siabar/30yamak/git/BratMerger/documents/Wrong"

    annotators = ['isabel', 'eugenia', 'victoria', 'carmen']

    for ann in annotators:
        path_dir1 = os.path.join(dir1, ann, args.set)
        path_dir2 = os.path.join(dir2, ann, args.set)
        for f in os.listdir(path_dir1):
            dir1_l = []
            dir2_l = []

            if f.endswith(".ann"):
                counter1 = 0
                counter2 = 0
                final_brat_file = os.path.join(path_dir1, f)
                with open(final_brat_file, "r") as pipeline_file:
                    for line in pipeline_file:
                        temp = line.strip().split("\t")
                        if not temp[0].startswith("#"):
                            dir1_l.append("\t".join(temp[1:]))
                        counter1 += 1
                final_brat_file = os.path.join(path_dir2, f)
                with open(final_brat_file, "r") as pipeline_file:
                    for line in pipeline_file:
                        temp = line.strip().split("\t")
                        if not temp[0].startswith("#"):
                            dir2_l.append("\t".join(temp[1:]))
                        counter2 += 1
                if counter1 != counter2:
                    print(f, set(dir1_l)-set(dir2_l), set(dir2_l)-set(dir1_l))


    # HEADER_BRAT = os.path.join(main_root, text_files, Set)
    # PIPELINE_BRAT = HEADER_BRAT.replace("ANN_SECTION", "ANN_VARIABLE")
    # FINAL_BRAT = HEADER_BRAT.replace("ANN_SECTION", "ANN_FINAL")
    # os.makedirs(os.path.join(FINAL_BRAT), exist_ok=True)
    # merge(HEADER_BRAT, PIPELINE_BRAT, FINAL_BRAT)