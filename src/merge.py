from collections import OrderedDict
import copy
import const as const
from utils import Utils


class Merger:

    @staticmethod
    def merged_dic(section, variables):
        print(
            "Removing _SUG_Lateralizacion and _SUG_Etiologia if they are in the middle of the Section")
        #
        removed_varibale = 0
        file_section_variavle = {}
        for file, records in section.items():
            if file.startswith('375981881'):
                check = 0

            #  final_brat_f = open(os.path.join("/ICTUSnet/data/ANN_FINAL", file), "w", encoding="UTF-8")
            section_dic = OrderedDict()

            section_ann = records

            variable_ann = variables.get(file)

            section_id = 0
            if len(section_ann) is not 0:
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
                            if sec_detail['T'].startswith("Details") and sec_detail['start'] \
                                    == current_section['start']:
                                missed = False
                        if missed:
                            temp = section_dic[current_section['label']]
                            temp.append({"T": "Details", "start": current_section['start'],
                                         "end": current_section['end'],
                                         "label": current_section['label'],
                                         "text": current_section['text']})
                            section_dic.update({current_section['label']: temp})
            else:
                for variable_id, variable in enumerate(variable_ann):
                    if "SECCION_DEFAULT" not in section_dic.keys():
                        section_dic['SECCION_DEFAULT'] = [variable]
                    else:
                        temp = section_dic['SECCION_DEFAULT']
                        temp.append(variable)
                        section_dic.update({'SECCION_DEFAULT': temp})

            file_section_variavle[file] = section_dic

        print(removed_varibale,
              "Number of variables that have been removed for _SUG_Lateralizacion and _SUG_Etiologia\n")

        return file_section_variavle


    @staticmethod
    def diagnostic_filterring(section_variable):
        print("Removing Diagnostic variables that are not in Diagnostic seccion and ")
        print("Removing Etiologia variables that are coming with their related Diagnostic and")
        print("Removing Arteria_afectada variables that are coming with Hemorragia Diagnostic")
        counter_diag = 0
        counter_etiologia = 0
        counter_arteria_afectada = 0
        all = 0
        section_variable_original = copy.deepcopy(section_variable)
        for file, sections in section_variable.items():
            for section, records in sections.items():
                first_main_variables = []
                new_record = records[:]
                Hemorragia_enable = False
                for record in new_record:
                    all += 1
                    if record["T"] != "Details":
                        if section not in const.REQUIRED_HEADERS:
                            if (record["label"].split("_SUG_")[-1] in const.REQUIRED_MAIN_VARIABLES or
                                    record["label"].split("_SUG_")[-1] in const.REQUIRED_SECOND_VARIABLES):
                                section_variable[file][section].remove(record)
                                counter_diag += 1
                        elif (record["label"].split("_SUG_")[-1] in const.REQUIRED_MAIN_VARIABLES or
                              record["label"].split("_SUG_")[-1] in const.REQUIRED_SECOND_VARIABLES_FIRST):
                            if record["label"].split("_SUG_")[-1] in first_main_variables:
                                section_variable[file][section].remove(record)
                                counter_diag += 1
                                # first_main_variables.append(record["label"].split("_SUG_")[-1])
                            else:
                                first_main_variables.append(record["label"].split("_SUG_")[-1])
                                if record["label"].split("_SUG_")[-1] == 'Hemorragia_cerebral':
                                    Hemorragia_enable = True
                # For filtering Etiologia
                if section in const.REQUIRED_HEADERS:
                    new_record = sections[section][:]
                    for record in new_record:
                        all += 1
                        if record["T"] != "Details":
                            if record["label"].split("_SUG_")[-1] == "Etiologia":
                                if (Hemorragia_enable and
                                        not Utils.similarity_hemorragia_evidence(record["text"].split("_SUG_")[-1]) and
                                        Utils.similarity_isquemico_evidence(record["text"].split("_SUG_")[-1])):
                                    section_variable[file][section].remove(record)
                                    counter_etiologia += 1
                                elif (not Hemorragia_enable and
                                      Utils.similarity_hemorragia_evidence(record["text"].split("_SUG_")[-1]) and
                                      not Utils.similarity_isquemico_evidence(record["text"].split("_SUG_")[-1])):
                                    section_variable[file][section].remove(record)
                                    counter_etiologia += 1
                            if record["label"].split("_SUG_")[-1] == "Arteria_afectada" and Hemorragia_enable:
                                section_variable[file][section].remove(record)
                                counter_arteria_afectada += 1


        print("\nNumber of removed diagnostic variabes are not in Diagnostic Section: {}, "
              "\nNumber of removed Etiologia variables that are coming with their related Diagnostic: {},"
              "\nNumber of removed Arteria_afectada variables that are coming with Hemorragia Diagnostic: {},"
              "\n out of {}\n".format(counter_diag, counter_etiologia, counter_arteria_afectada, all))

        return section_variable


