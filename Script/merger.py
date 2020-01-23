import os
import string
from os import listdir
import argparse
import copy

from unidecode import unidecode


class merge():

    def __init__(self):
        self.fileDir = os.path.dirname(os.path.abspath(__file__))
        self.parentDir = os.path.dirname(self.fileDir)

        self.variable_names_dic = dict()
        self.section_name_dic = dict()

        self.section = dict()
        self.variables = dict()
        self.variables_hash = dict()

        self.set = None

        self.annotators = []
        self.section_variable = dict()

        self.validated_files = []

        self.required_headers = ["SECCION_DIAGNOSTICO_PRINCIPAL", "SECCION_DIAGNOSTICOS"]
        self.required_main_variables = ["Ictus_isquemico", "Ataque_isquemico_transitorio", "Hemorragia_cerebral"]
        self.required_second_variables = ["Arteria_afectada", "Localizacion", "Lateralizacion", "Etiologia"]


    def context_dic(self, path):
        with open(path, "r") as h:
            for line in h:
                line_unaccent = unidecode(line)
                row = line_unaccent.strip().split("\t")
                if len(row) == 3:
                    if not "_SUG_" + row[2] in self.variable_names_dic.keys():
                        self.variable_names_dic["_SUG_" + row[2]] = [row[0] + "|" + "_SUG_" + row[1]]
                    elif row[0] + "|" + "_SUG_" + row[1] not in self.variable_names_dic.get("_SUG_" + row[2]):
                        temp = self.variable_names_dic.get("_SUG_" + row[2])
                        temp.append(row[0] + "|" + "_SUG_" + row[1])
                        self.variable_names_dic.update({"_SUG_" + row[2]: temp})
                if not "_SUG_" + row[1] in self.section_name_dic.keys():
                    self.section_name_dic["_SUG_" + row[1]] = [row[0]]
                elif row[0] not in self.section_name_dic.get("_SUG_" + row[1]):
                    temp = self.section_name_dic.get("_SUG_" + row[1])
                    temp.append(row[0])
                    self.section_name_dic.update({"_SUG_" + row[1]: temp})

    def get_section(self, section_root):
        self.validated_files = []
        for annotator in self.annotators:
            header_brat = os.path.join(section_root, annotator, self.set)
            header_dict = dict()

            for f in listdir(header_brat):
                if f.endswith(".ann"):
                    if f not in self.validated_files:
                        self.validated_files.append(f.replace(".ann", ""))
                    else:
                        print("ERROR")
                    counter = 1
                    header_brat_file = os.path.join(header_brat, f)
                    ann_list = []
                    with open(header_brat_file, "r") as header_file:
                        pre_header = ""
                        for l in header_file:
                            line = l.split("\t", 2)
                            header = line[1].split(" ", 2)
                            if header[0] != pre_header:
                                brat_dict = {}
                                brat_dict["T"] = "T" + str(counter)
                                brat_dict['label'] = header[0]
                                brat_dict['start'] = int(header[1])
                                brat_dict['end'] = int(header[2])
                                brat_dict['text'] = line[2].strip()
                                # brat_dict["T" + str(counter)] = line[1] + "\t" + line[2]
                                counter += 1
                            pre_header = header[0]
                            ann_list.append(brat_dict)
                        header_file.close()

                    entities_ordered = sorted(ann_list, key=lambda entity: entity['start'])
                    header_dict[f] = entities_ordered
            self.section[annotator] = header_dict


    def span_fixer(self, text, start_span, end_span, label):
        punctuation = string.punctuation
        before_rstrip = len(text)
        text = text.rstrip()
        after_rstrip = len(text)
        end_span -= before_rstrip - after_rstrip
        while text[len(text) - 1] in punctuation:
            text = text[:-1]
            removed_space = len(text) - len(text.rstrip())
            text = text.rstrip()
            end_span -= 1 + removed_space
        before_lstrip = len(text)
        text = text.lstrip()
        after_lstrip = len(text)
        start_span += before_lstrip - after_lstrip
        while text[0] in string.punctuation:
            text = text[1:]
            removed_space = len(text) - len(text.lstrip())
            text = text.lstrip()
            start_span += 1 + removed_space

        return text, start_span, end_span

    def get_variables(self, variable_root):
        print(
            "List of removed variables that have been removed if the variable is duration (not min, hor) and we a longest variable is available for that begin span.")
        counter_removed = 0
        varibale = dict()
        varibale_hash = dict()

        for annotator in self.annotators:
            variable_brat = os.path.join(variable_root, annotator, self.set)
            varibale_dict = dict()
            varibale_hash_dict = dict()
            for f in listdir(variable_brat):
                if f.replace(".ann", "").replace(".txt.xmi","") in self.validated_files:

                    # if f.startswith("432062870"):
                    #     print("Done")
                    removed_list = []
                    brat_dict = dict()
                    final_brat_dict = dict()
                    brat_hash_dict = dict()
                    if f.endswith(".ann"):
                        counter = 1
                        variable_brat_file = os.path.join(variable_brat, f)
                        ann_list = []
                        if f.startswith('sonespases_937961405'):
                            check = 0

                        with open(variable_brat_file, "r") as pipeline_file:
                            for l in pipeline_file:
                                line = l.split("\t", 2)

                                # if line[0].startswith("T37"):
                                #     print("Check")
                                if not l.startswith("#"):
                                    label = line[1].split(" ", 2)
                                    text, start_span, end_span = self.span_fixer(line[2][:-1], int(label[1]), int(label[2]), label[0])
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
                    os.remove(os.path.join(variable_brat, f))
                    print("REMOVE:", os.path.join(variable_brat, f))

            varibale[annotator] = varibale_dict
            varibale_hash[annotator] = varibale_hash_dict

        self.variables = varibale
        self.variables_hash = varibale_hash
        print(counter_removed, "Number of removed based on Duration, shortess length\n")

    def merged_dic(self):
        print(
            "List of removed pre-annotated _SUG_Lateralizacion and _SUG_Etiologia happend in the middle of the SUG Seccion")
        removed_varibale = 0
        w_contaxt_awareness = open(
            os.path.join(merge_func.parentDir, "documents") + "/diff_link_contax_awareness_and_not", 'w')
        for annotator in self.annotators:
            file_section_variavle = {}
            for file, records in self.section.get(annotator).items():
                if file.startswith('375981881'):
                    check = 0
                section_dic = dict()

                section_ann = records

                variable_ann = self.variables.get(annotator).get(file)

                section_id = 0

                for variable_id, variable in enumerate(variable_ann):
                    current_section = section_ann[section_id]

                    # if current_section['label'] == 'SECCION_EVOLUCION':
                    #     print("D")
                    #
                    # if variable['start'] == 13210:
                    #     print("D")

                    if section_id == 0 and variable['start'] <= current_section['start']:
                        if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                            'label'] == "_SUG_Etiologia") and
                                variable['start'] >= current_section['start'] and variable['end'] <= current_section[
                                    'end']):
                            if "SECCION_DEFAULT" not in section_dic.keys():
                                section_dic['SECCION_DEFAULT'] = [variable]
                            else:
                                temp = section_dic['SECCION_DEFAULT']
                                temp.append(variable)
                                section_dic.update({'SECCION_DEFAULT': temp})
                        else:
                            # print(annotator, file, variable)
                            removed_varibale += 1
                    elif section_id == len(section_ann) - 1 and variable['start'] >= current_section['start']:
                        if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                            'label'] == "_SUG_Etiologia") and
                                variable['start'] >= current_section['start'] and variable['end'] <= current_section[
                                    'end']):
                            if current_section['label'] not in section_dic.keys():
                                section_dic[current_section['label']] = [
                                    {"T": "Details", "label": current_section['label'],
                                     "start": current_section['start'], "end": current_section['end'],
                                     "text": current_section['text']},
                                    variable]
                            else:
                                temp = section_dic.get(current_section['label'])
                                temp.append(variable)
                                section_dic.update({current_section['label']: temp})
                        else:
                            # print(annotator, file, variable)
                            removed_varibale += 1
                    elif current_section['start'] <= variable['start'] < section_ann[section_id + 1]['start']:
                        if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                            'label'] == "_SUG_Etiologia") and
                                variable['start'] >= current_section['start'] and variable['end'] <= current_section[
                                    'end']):
                            if current_section['label'] not in section_dic.keys():
                                section_dic[current_section['label']] = [
                                    {"T": "Details", "label": current_section['label'],
                                     "start": current_section['start'], "end": current_section['end'],
                                     "text": current_section['text']},
                                    variable]
                            else:
                                temp = section_dic[current_section['label']]
                                temp.append(variable)
                                section_dic.update({current_section['label']: temp})
                        else:
                            # print(annotator, file, variable)
                            removed_varibale += 1
                        if variable_id < (len(variable_ann) - 1):
                            if section_ann[section_id]['label'] not in section_dic.keys():
                                section_dic[section_ann[section_id]['label']] = [
                                    {"T": "Details", "start": section_ann[section_id]['start'],
                                     "end": section_ann[section_id]['end'], "label": section_ann[section_id]['label'],
                                     "text": section_ann[section_id]['text']}]
                            while section_id < (len(section_ann) - 1) and variable_ann[variable_id + 1]['start'] >= \
                                    section_ann[section_id + 1]['start']:
                                if section_ann[section_id + 1]['label'] not in section_dic.keys():
                                    section_dic[section_ann[section_id + 1]['label']] = [
                                        {"T": "Details", "start": section_ann[section_id + 1]['start'],
                                         "end": section_ann[section_id + 1]['end'],
                                         "label": section_ann[section_id + 1]['label'],
                                         "text": section_ann[section_id + 1]['text']}]
                                else:
                                    missed = True
                                    for sec_detail in section_dic.get(section_ann[section_id + 1]['label']):
                                        if sec_detail['T'].startswith("Details") and sec_detail['start'] == \
                                                section_ann[section_id + 1]['start']:
                                            missed = False
                                    if missed:
                                        temp = section_dic[section_ann[section_id + 1]['label']]
                                        temp.append({"T": "Details", "start": section_ann[section_id + 1]['start'],
                                                     "end": section_ann[section_id + 1]['end'],
                                                     "label": section_ann[section_id + 1]['label'],
                                                     "text": section_ann[section_id + 1]['text']})
                                        section_dic.update({section_ann[section_id + 1]['label']: temp})
                                section_id += 1
                        # else:
                        #     print("CHECK")
                    else:
                        if variable_id < (len(variable_ann) - 1):
                            while section_id < (len(section_ann) - 1) and variable_ann[variable_id]['start'] >= \
                                    section_ann[section_id + 1]['start']:
                                if section_ann[section_id]['label'] not in section_dic.keys():
                                    section_dic[section_ann[section_id]['label']] = [
                                        {"T": "Details", "start": section_ann[section_id]['start'],
                                         "end": section_ann[section_id]['end'],
                                         "label": section_ann[section_id]['label'],
                                         "text": section_ann[section_id]['text']}]
                                else:
                                    missed = True
                                    for sec_detail in section_dic.get(section_ann[section_id]['label']):
                                        if sec_detail['T'].startswith("Details") and sec_detail['start'] == \
                                                section_ann[section_id]['start']:
                                            missed = False
                                    if missed:
                                        temp = section_dic[section_ann[section_id]['label']]
                                        temp.append({"T": "Details", "start": section_ann[section_id]['start'],
                                                     "end": section_ann[section_id]['end'],
                                                     "label": section_ann[section_id]['label'],
                                                     "text": section_ann[section_id]['text']})
                                        section_dic.update({section_ann[section_id]['label']: temp})
                                section_id += 1
                            if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                                'label'] == "_SUG_Etiologia") and
                                    variable['start'] >= section_ann[section_id]['start'] and variable['end'] <=
                                    section_ann[section_id]['end']):
                                if section_ann[section_id]['label'] not in section_dic.keys():
                                    section_dic[section_ann[section_id]['label']] = [
                                        {"T": "Details", "start": section_ann[section_id]['start'],
                                         "end": section_ann[section_id]['end'],
                                         "label": section_ann[section_id]['label'],
                                         "text": section_ann[section_id]['text']}, variable]
                                else:
                                    temp = section_dic[section_ann[section_id]['label']]
                                    temp.append(variable)
                                    section_dic.update({section_ann[section_id]['label']: temp})
                        # else:
                        #     print("CHECK")

                for current_section in section_ann:
                    if current_section['label'] not in section_dic.keys():
                        section_dic[current_section['label']] = [
                            {"T": "Details", "start": current_section['start'], "end": current_section['end'],
                             "label": current_section['label'], "text": current_section['text']}]
                    else:
                        missed = True
                        for sec_detail in section_dic.get(current_section['label']):
                            if sec_detail['T'].startswith("Details") and sec_detail['start'] == current_section[
                                'start']:
                                missed = False
                        if missed:
                            temp = section_dic[current_section['label']]
                            temp.append({"T": "Details", "start": current_section['start'],
                                         "end": current_section['end'],
                                         "label": current_section['label'],
                                         "text": current_section['text']})
                            section_dic.update({current_section['label']: temp})

                file_section_variavle[file] = section_dic
                w_contaxt_awareness.write('http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/' + annotator + "/" +
                        self.set.split("+")[0] + '/#/' + annotator + "/." + self.set
                            + "/" + file.replace(".ann", "") + "\n")
            self.section_variable[annotator] = file_section_variavle

        print(removed_varibale,
              "Number of variables that have been removed for _SUG_Lateralizacion and _SUG_Etiologia\n")

    def diagnostic_filterring(self):
        print("Remove Diagnostic variables that are not in Diagnostic seccion ")
        counter =  0
        all =  0
        section_variable_original = copy.deepcopy(self.section_variable)
        for annotator, files in self.section_variable.items():
            for file, sections in files.items():
                for section, records in sections.items():
                    new_record = records[:]
                    for record in new_record:
                        all += 1
                        if record["T"] != "Details" and \
                                section not in self.required_headers and \
                                (record["label"].split("_SUG_")[-1] in self.required_main_variables or
                                record["label"].split("_SUG_")[-1] in self.required_second_variables):
                            self.section_variable[annotator][file][section].remove(record)
                            counter+=1

        print("Number of removed variabes:", counter, "out of", all)
    def context_awareness(self):

        # For first time, Contect_awareness would be apply just for 8 new duplicated files on Bunch 5.
        print("List of removed variables based on the contect awareness:")
        counter_removed = 0
        counter_all = 0
        for annotator, files in self.section_variable.items():
            for file, section_variable in files.items():
                if file.startswith('453865409.utf8'):
                    check = 5
                for section, vars in section_variable.items():
                    if section == 'SECCION_ANTECEDENTES_PATOLOGICOS':
                        check = 5
                    details_section = None
                    variables = vars.copy()
                    for var in variables:
                        if var['label'] == 'TAC_craneal':
                            check = 7
                        counter_all += 1
                        warning1 = False
                        warning2 = True
                        if var['T'].startswith("T"):
                            if (var['label'] in self.section_name_dic.keys() and
                                    not section in self.section_name_dic[var['label']]):
                                warning1 = True
                            if warning1 and var['label'] in self.variable_names_dic.keys():
                                sec_var_list = self.variable_names_dic.get(var['label'])
                                for sec_var_current in sec_var_list:
                                    sec_var = sec_var_current.split("|")
                                    if warning2 == False:
                                        continue
                                    if sec_var[0] == section:
                                        for var_2 in vars:
                                            if var_2['T'].startswith("T"):
                                                if var_2['label'] == sec_var[1]:
                                                    warning2 = False
                                                    continue
                            if section != "SECCION_DEFAULT" and warning1 and warning2:
                                self.section_variable[annotator][file][section].remove(var)
                                # if var['T'].replace("T", "#") in self.variables_hash[annotator][file].keys():
                                #     del self.variables_hash[annotator][file][var['T'].replace("T", "#")]
                                counter_removed += 1

                                print("Annotator:", annotator, ", File: ", file,
                                      ", Section (", details_section['start'], ",", details_section['end'], "): ",
                                      section, ", Variable: ", var)
                        else:
                            details_section = var
        print(counter_removed, "out of", counter_all, "variables are removed based on the context awareness algorithm.")

    def save_accepted_varibales(self, ann_final):

        print("Saving accepted varibales and section in the final ann.")

        for dir, files in self.section_variable.items():
            for file, section_varibale in files.items():
                T = 0
                final_brat_file = os.path.join(ann_final, dir, self.set)
                os.makedirs(os.path.join(final_brat_file), exist_ok=True)
                final_brat_f = open(os.path.join(final_brat_file, file), "w")
                for section, variables in section_varibale.items():
                    for var in variables:
                        if var["T"].startswith("T"):
                            final_brat_f.write('T' + str(T) +
                                               "\t" + var['label'] + " " + str(var['start']) + " " + str(var['end']) +
                                               "\t" + var['text'] + "\n")
                            if var['T'].replace("T", "#") in self.variables_hash[dir][file].keys():
                                final_brat_f.write('#' + str(T) + "\t" + self.variables_hash[dir][file][var['T']
                                                   .replace("T", "#")].replace(var['T'], 'T' + str(T)))
                        else:
                            final_brat_f.write('T' + str(T) +
                                               "\t" + var['label'] + " " + str(var['start']) + " " + str(var['end']) +
                                               "\t" + var['text'] + "\n")
                        T += 1
        print("Done")

    # def merge(ann_section, ann_variable, ann_final):
    #     header_brat = ann_section
    #     pipeline_brat = ann_variable
    #     final_brat = ann_final
    #
    #     for f in listdir(pipeline_brat):
    #         removed_list = []
    #         final_dict = dict()
    #         brat_dict = dict()
    #         if f.endswith(".ann"):
    #             counter = 1
    #             final_brat_file = os.path.join(final_brat, f)
    #             with open(final_brat_file, "w") as final_brat_f:
    #                 with open(os.path.join(pipeline_brat, f), "r") as pipeline_file:
    #                     last_line = ""
    #                     for l in pipeline_file:
    #                         line = l.split("\t", 2)
    #                         temp = line[1]
    #                         if not l.startswith("#"):
    #                             l_3 = line[1].split(" ", 2)
    #                             if l_3[0].startswith("DATE"):
    #                                 l_3[0] = "FECHA"
    #                             elif l_3[0].startswith("TIME"):
    #                                 l_3[0] = "HORA"
    #                             elif l_3[0].startswith("DURATION"):
    #                                 l_3[0] = "TIEMPO"
    #
    #                             if l_3[0] == "TIEMPO":
    #                                 if "min" in l_3[1].lower() or "hor" in l_3[1].lower():
    #                                     temp = l_3[0] + " " + l_3[1] + " " + l_3[2]
    #                                 else:
    #                                     temp = ""
    #                                     removed_list.append(line[0].replace("T", "#", 1))
    #                             else:
    #                                 temp = l_3[0] + " " + l_3[1] + " " + l_3[2]
    #                         if temp != "":
    #                             brat_dict[line[0]] = line[0] + "\t" + temp + "\t" + line[2]
    #                             last_line = l
    #                 if last_line.startswith("#"):
    #                     counter = int(last_line.split("\t")[0].split("#")[1]) + 1
    #                 else:
    #                     try:
    #                         counter = int(last_line.split("\t")[0].split("T")[1]) + 1
    #                     except:
    #                         print(last_line)
    #                 pipeline_file.close()
    #
    #                 header_brat_file = os.path.join(header_brat, f)
    #
    #                 with open(header_brat_file, "r") as header_file:
    #                     pre_header = ""
    #                     for l in header_file:
    #                         line = l.split("\t", 2)
    #                         header = line[1].split(" ", 2)
    #                         if header[0] != pre_header:
    #                             # temp_accented_string = line[1].split(" ")
    #                             # length_temp = len(temp_accented_string)
    #                             # accented_string = "_".join(temp_accented_string[0:length_temp - 2])
    #                             #
    #                             # unaccented_string = "SECTION_" + unidecode.unidecode(accented_string)
    #                             # header_dic.add(unaccented_string)
    #                             # final_brat_f.write("T" + str(counter) + "\t" + line[1])
    #                             temp_list = []
    #                             for keys in brat_dict:
    #                                 if brat_dict[keys].startswith("T"):
    #                                     header_spans = brat_dict[keys].split("\t", 2)[1].split(" ", 2)
    #                                     if header_spans[0] == "_SUG_Lateralizacion" or header_spans[
    #                                         0] == "_SUG_Etiologia":
    #                                         if int(header_spans[1]) >= int(line[1].split(" ")[1]) and \
    #                                                 int(header_spans[2]) <= int(line[1].split(" ")[2]):
    #                                             temp_list.append(keys)
    #                             for key in temp_list:
    #                                 del brat_dict[key]
    #
    #                             brat_dict["T" + str(counter)] = "T" + str(counter) + "\t" + line[1] + "\t" + line[2]
    #                             counter += 1
    #                         pre_header = header[0]
    #                 header_file.close()
    #                 # -------------------
    #                 for keys in brat_dict:
    #                     if brat_dict[keys].startswith("T"):
    #                         header_spans = brat_dict[keys].split("\t", 2)[1].split(" ", 2)
    #                         final_line = brat_dict[keys]
    #                         for keys_2 in brat_dict:
    #                             if brat_dict[keys_2].startswith("T"):
    #                                 header_spans_2 = brat_dict[keys_2].split("\t", 2)[1].split(" ", 2)
    #                                 if header_spans[0] == header_spans_2[0]:
    #                                     if int(header_spans[1]) == int(header_spans_2[1]):
    #                                         try:
    #                                             if int(header_spans[2]) < int(header_spans_2[2]):
    #                                                 final_line = ""
    #                                                 break
    #                                         except:
    #                                             print(brat_dict[keys_2])
    #                         if final_line != "":
    #                             final_dict[keys] = brat_dict[keys]
    #                     elif keys not in removed_list:
    #                         final_dict[keys] = brat_dict[keys]
    #
    #                 for keys, values in final_dict.items():
    #                     val = values.replace("&apos;", "'")
    #                     final_brat_f.write(val)
    #
    #             final_brat_f.close()
    #     # for term in header_dic:
    #     #     print(term)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="analysis")
    parser.add_argument('--set', help='Which set is going to compare')

    args = parser.parse_args()

    merge_func = merge()

    merge_func.set = args.set

    section_root = os.path.join(merge_func.parentDir, "documents", "ANN_SECTION")

    context_file = os.path.join(merge_func.parentDir, "data/contexts.csv")

    merge_func.context_dic(context_file)

    annotators_list = []

    for text_files in os.listdir(section_root):
        if not text_files.startswith("."):
            annotators_list.append(text_files)

    merge_func.annotators = annotators_list

    merge_func.get_section(section_root)

    variable_root = section_root.replace("ANN_SECTION", "ANN_VARIABLE")
    merge_func.get_variables(variable_root)

    merge_func.merged_dic()

    merge_func.diagnostic_filterring()

    merge_func.context_awareness()

    final_root = section_root.replace("ANN_SECTION", "ANN_FINAL")
    merge_func.save_accepted_varibales(final_root)

    # HEADER_BRAT = os.path.join(main_root, text_files, Set)
    # PIPELINE_BRAT = HEADER_BRAT.replace("ANN_SECTION", "ANN_VARIABLE")
    # FINAL_BRAT = HEADER_BRAT.replace("ANN_SECTION", "ANN_FINAL")
    # os.makedirs(os.path.join(FINAL_BRAT), exist_ok=True)
    # merge(HEADER_BRAT, PIPELINE_BRAT, FINAL_BRAT)
