from os import listdir
import os
from src.utils import Utils


class Entity:

    @staticmethod
    def get_section(section_root):
        validated_files = []
        header_dict = dict()

        for f in listdir(section_root):
            if f.endswith(".ann"):
                if f not in validated_files:
                    validated_files.append(f.replace(".ann", ""))
                else:
                    print("ERROR")
                counter = 1
                header_brat_file = os.path.join(section_root, f)
                ann_list = []
                with open(header_brat_file, "r", encoding="UTF-8") as header_file:
                    pre_header = ""
                    for l in header_file:
                        line = l.split("\t", 2)
                        header = line[1].split(" ", 2)
                        brat_dict = {}
                        if header[0] != pre_header:
                            brat_dict["T"] = "T" + str(counter)
                            brat_dict['label'] = header[0]
                            brat_dict['start'] = int(header[1])
                            brat_dict['end'] = int(header[2])
                            brat_dict['text'] = line[2].strip()
                            # brat_dict["T" + str(counter)] = line[1] + "\t" + line[2]
                            counter += 1
                        else:
                            continue
                        pre_header = header[0]
                        ann_list.append(brat_dict)
                    header_file.close()

                entities_ordered = sorted(ann_list, key=lambda entity: entity['start'])
                header_dict[f] = entities_ordered
        return header_dict, validated_files

    @staticmethod
    def get_variables(variable_root, validated_files):
        print(
            "List of removed variables that have been removed if the variable is duration/Tiempo (not min, hor) and if a longest variable is available for that begin span.")
        #
        #
        counter_removed = 0
        varibale_dict = dict()
        varibale_hash_dict = dict()
        for f in listdir(variable_root):
            if f.replace(".ann", "").replace(".txt.xmi", "") in validated_files:

                # if f.startswith("432062870"):
                #     print("Done")
                removed_list = []
                brat_dict = dict()
                final_brat_dict = dict()
                brat_hash_dict = dict()
                if f.endswith(".ann"):
                    counter = 1
                    variable_brat_file = os.path.join(variable_root, f)
                    ann_list = []
                    if f.startswith('sonespases_937961405'):
                        check = 0

                    with open(variable_brat_file, "r", encoding="UTF-8") as pipeline_file:
                        for l in pipeline_file:
                            line = l.split("\t", 2)

                            # if line[0].startswith("T37"):
                            #     print("Check")
                            if not l.startswith("#"):
                                label = line[1].split(" ", 2)
                                text, start_span, end_span = Utils.span_fixer(line[2][:-1], int(label[1]),
                                                                              int(label[2]), label[0])
                                temp = label[0] + " " + str(start_span) + " " + str(end_span)

                                l_3 = temp.split(" ", 2)
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
                                        # print(annotator, f, l.strip())
                                        counter_removed += 1
                                        temp = ""
                                        removed_list.append(line[0].replace("T", "#", 1))
                                else:
                                    temp = l_3[0] + " " + l_3[1] + " " + l_3[2]
                                if temp != "":
                                    brat_dict[line[0]] = temp + "\t" + text
                            else:
                                brat_hash_dict[line[0]] = line[1] + "\t" + line[2]

                        #             last_line = l
                        # if last_line.startswith("#"):
                        #     counter = int(last_line.split("\t")[0].split("#")[1]) + 1
                        # else:
                        #     try:
                        #         counter = int(last_line.split("\t")[0].split("T")[1]) + 1
                        #     except:
                        #         print(last_line)
                        pipeline_file.close()

                    for hash_var in removed_list:
                        del brat_hash_dict[hash_var]

                    for keys in brat_dict:

                        header_spans = brat_dict[keys].split("\t", 1)[0].split(" ", 2)

                        # if keys.startswith("T37"):
                        #     print("Check")

                        final_line = brat_dict[keys]
                        for keys_2 in brat_dict:
                            header_spans_2 = brat_dict[keys_2].split("\t", 1)[0].split(" ", 2)
                            if header_spans[0] == header_spans_2[0]:
                                if int(header_spans[1]) == int(header_spans_2[1]):
                                    try:
                                        if int(header_spans[2]) < int(header_spans_2[2]):
                                            final_line = ""
                                            break
                                    except:
                                        print("ERRPR", brat_dict[keys_2])
                                if int(header_spans[2]) == int(header_spans_2[2]):
                                    try:
                                        if int(header_spans[1]) > int(header_spans_2[1]):
                                            final_line = ""
                                            break
                                    except:
                                        print("ERRPR", brat_dict[keys_2])

                        if final_line != "":
                            temp = brat_dict[keys]
                            final_brat_dict = {}
                            final_brat_dict["T"] = keys
                            temp_core = temp.split("\t", 1)[0].split(" ")
                            final_brat_dict['label'] = temp_core[0]
                            final_brat_dict['start'] = int(temp_core[1])
                            final_brat_dict['end'] = int(temp_core[2])
                            final_brat_dict['text'] = temp.split("\t", 1)[1].strip()
                            ann_list.append(final_brat_dict)
                        else:
                            # print(annotator, f, brat_dict[keys].strip())
                            counter_removed += 1

                    entities_ordered = sorted(ann_list, key=lambda entity: entity['start'])

                    varibale_dict[f] = entities_ordered
                    varibale_hash_dict[f] = brat_hash_dict
            else:
                os.remove(os.path.join(variable_root, f))
                print("REMOVE:", os.path.join(variable_root, f))

        print(counter_removed, "Number of removed based on Duration, shortess length\n")
        return varibale_dict, varibale_hash_dict

