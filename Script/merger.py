import os
from os import listdir
import argparse

fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)


def merge(ann_section, ann_variable, ann_final):
    header_brat = ann_section
    pipeline_brat = ann_variable
    final_brat = ann_final

    for f in listdir(pipeline_brat):
        removed_list = []
        final_dict = dict()
        brat_dict = dict()
        if f.endswith(".ann"):
            counter = 1
            final_brat_file = os.path.join(final_brat, f)
            with open(final_brat_file, "w") as final_brat_f:
                with open(os.path.join(pipeline_brat, f), "r") as pipeline_file:
                    last_line = ""
                    for l in pipeline_file:
                        line = l.split("\t", 2)
                        temp = line[1]
                        if not l.startswith("#"):
                            l_3 = line[1].split(" ", 2)
                            if l_3[0].startswith("DATE"):
                                l_3[0] = "FECHA"
                            elif l_3[0].startswith("TIME"):
                                l_3[0] = "HORA"
                            elif l_3[0].startswith("DURATION"):
                                l_3[0] = "TIEMPO"

                            if l_3[0] == "TIEMPO":
                                if "min" in l_3[1].lower() or "hor" in l_3[1].lower():
                                    temp = l_3[0] + " " + l_3[1] + " " + l_3[2]
                                else:
                                    temp = ""
                                    removed_list.append(line[0].replace("T", "#", 1))
                            else:
                                temp = l_3[0] + " " + l_3[1] + " " + l_3[2]
                        if temp != "":
                            brat_dict[line[0]] = line[0] + "\t" + temp + "\t" + line[2]
                            last_line = l
                if last_line.startswith("#"):
                    counter = int(last_line.split("\t")[0].split("#")[1]) + 1
                else:
                    try:
                        counter = int(last_line.split("\t")[0].split("T")[1]) + 1
                    except:
                        print(last_line)
                pipeline_file.close()

                header_brat_file = os.path.join(header_brat, f)

                with open(header_brat_file, "r") as header_file:
                    pre_header = ""
                    for l in header_file:
                        line = l.split("\t", 2)
                        header = line[1].split(" ", 2)
                        if header[0] != pre_header:
                            # temp_accented_string = line[1].split(" ")
                            # length_temp = len(temp_accented_string)
                            # accented_string = "_".join(temp_accented_string[0:length_temp - 2])
                            #
                            # unaccented_string = "SECTION_" + unidecode.unidecode(accented_string)
                            # header_dic.add(unaccented_string)
                            # final_brat_f.write("T" + str(counter) + "\t" + line[1])
                            temp_list = []
                            for keys in brat_dict:
                                if brat_dict[keys].startswith("T"):
                                    header_spans = brat_dict[keys].split("\t", 2)[1].split(" ", 2)
                                    if header_spans[0] == "_SUG_Lateralizacion" or header_spans[0] == "_SUG_Etiologia":
                                        if int(header_spans[1]) >= int(line[1].split(" ")[1]) and \
                                                int(header_spans[2]) <= int(line[1].split(" ")[2]):
                                            temp_list.append(keys)
                            for key in temp_list:
                                del brat_dict[key]

                            brat_dict["T" + str(counter)] = "T" + str(counter) + "\t" + line[1] + "\t" + line[2]
                            counter += 1
                        pre_header = header[0]
                header_file.close()
                # -------------------
                for keys in brat_dict:
                    if brat_dict[keys].startswith("T"):
                        header_spans = brat_dict[keys].split("\t", 2)[1].split(" ", 2)
                        final_line = brat_dict[keys]
                        for keys_2 in brat_dict:
                            if brat_dict[keys_2].startswith("T"):
                                header_spans_2 = brat_dict[keys_2].split("\t", 2)[1].split(" ", 2)
                                if header_spans[0] == header_spans_2[0]:
                                    if int(header_spans[1]) == int(header_spans_2[1]):
                                        try:
                                            if int(header_spans[2]) < int(header_spans_2[2]):
                                                final_line = ""
                                                break
                                        except:
                                            print(brat_dict[keys_2])
                        if final_line != "":
                            final_dict[keys] = brat_dict[keys]
                    elif keys not in removed_list:
                        final_dict[keys] = brat_dict[keys]

                for keys, values in final_dict.items():
                    val = values.replace("&apos;", "'")
                    final_brat_f.write(val)

            final_brat_f.close()
    # for term in header_dic:
    #     print(term)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="analysis")
    parser.add_argument('--set', help='Which set is going to compare')

    args = parser.parse_args()
    Set = args.set

    main_root = os.path.join(parentDir, "documents", "ANN_SECTION")

    for text_files in os.listdir(main_root):
        if not text_files.startswith("."):
            HEADER_BRAT = os.path.join(main_root, text_files, Set)
            PIPELINE_BRAT = HEADER_BRAT.replace("ANN_SECTION", "ANN_VARIABLE")
            FINAL_BRAT = HEADER_BRAT.replace("ANN_SECTION", "ANN_FINAL")
            os.makedirs(os.path.join(FINAL_BRAT), exist_ok=True)

            merge(HEADER_BRAT, PIPELINE_BRAT, FINAL_BRAT)
