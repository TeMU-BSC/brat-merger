import os


class Write:

    @staticmethod
    def save_accepted_variables(section_variable, variables_hash, ann_final):

        print("Saving accepted variables and section in the final ann.")

        for file, section_variable in section_variable.items():
            T = 0
            final_brat_file = ann_final
            os.makedirs(os.path.join(final_brat_file), exist_ok=True)
            final_brat_f = open(os.path.join(final_brat_file, file), "w", encoding="UTF-8")
            for section, variables in section_variable.items():
                for var in variables:
                    if var["T"].startswith("T"):
                        tuple = ()

                        final_brat_f.write('T' + str(T) +
                                           "\t" + var['label'] + " " + str(var['start']) + " " + str(var['end']) +
                                           "\t" + var['text'] + "\n")
                        if var['T'].replace("T", "#") in variables_hash[file].keys():
                            final_brat_f.write('#' + str(T) + "\t" + variables_hash[file][var['T']
                                               .replace("T", "#")].replace(var['T'], 'T' + str(T)))
                    else:
                        final_brat_f.write('T' + str(T) +
                                           "\t" + var['label'] + " " + str(var['start']) + " " + str(var['end']) +
                                           "\t" + var['text'] + "\n")
                    T += 1
        print("Done")
