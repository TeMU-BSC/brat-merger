
REQUIRED_HEADERS = ["SECCION_DIAGNOSTICO_PRINCIPAL", "SECCION_DIAGNOSTICOS"]

REQUIRED_MAIN_VARIABLES = ["Ictus_isquemico", "Ataque_isquemico_transitorio", "Hemorragia_cerebral"]

REQUIRED_SECOND_VARIABLES = ["Arteria_afectada", "Localizacion", "Lateralizacion", "Etiologia"]

# Order is important
REQUIRED_SECOND_VARIABLES_FIRST = ["Lateralizacion", "Etiologia"]

HEMORRAGIA_EVIDENCE = ["aneurisma","angiopatia amiloide","cavernoma de circunvolucion","diseccio","hipertensiva","indeterminada","malformacion arteriovenosa","microangiopatica","secundaria a malformacion vascular","secundaria a tumor","hipertensivo"]
ISQUEMICO_EVIDENCE = ["a estudio","ateromatosis","aterosclerotico","aterotrombotico","cardioembolico","criptogenico","embolico","esus","indeterminado de causa doble","indeterminado por estudio incompleto","infrecuente","inhabitual","lacunar","mecanisme embolic","cardioemebolico","ce","etiologia pendent de filiacio","indeterminado (estudio incompleto)","insual","origen cardiaco"]
ETIOLOGIA_EVIDENCE = ["etiologia", "causa", "perfil", "de origen", "d'etiologia"]
