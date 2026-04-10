SORT_OPTIONS = {
    "students": {
        "options": ["Name", "Student ID", "Year Level", "Program", "College"],
        "columns": {
            "Name":       "Name",
            "Student ID": "ID",
            "Year Level": "Year Level",
            "Program":    "Program",
            "College":    "College"
        },
        "default": "Name"
    },
    "programs": {
        "options": ["Program Name", "Program ID", "College", "No. of Students"],
        "columns": {
            "Program Name":    "Program Name",
            "Program ID":      "Program ID",
            "College":         "College",
            "No. of Students": "No. of Students"
        },
        "default": "Program Name"
    },
    "colleges": {
        "options": ["College Name", "College ID", "No. of Programs", "No. of Students"],
        "columns": {
            "College Name":     "College Name",
            "College ID":       "College ID",
            "No. of Programs":  "No. of Programs",
            "No. of Students":  "No. of Students"
        },
        "default": "College Name"
    }
}


SEED_COLLEGES = [
    ("CCS",  "College of Computer Studies"),
    ("COE",  "College of Engineering"),
    ("CBA",  "College of Business Administration"),
    ("CED",  "College of Education"),
    ("CAS",  "College of Arts and Sciences"),
    ("CHK",  "College of Human Kinetics"),
    ("CNS",  "College of Nursing and Health Sciences"),
    ("CAF",  "College of Agriculture and Forestry"),
]

SEED_PROGRAMS = [
    ("BSCS",      "Bachelor of Science in Computer Science",        "CCS"),
    ("BSIT",      "Bachelor of Science in Information Technology",   "CCS"),
    ("BSISM",     "Bachelor of Science in Information Systems Mgmt", "CCS"),
    ("BSCE",      "Bachelor of Science in Civil Engineering",        "COE"),
    ("BSEE",      "Bachelor of Science in Electrical Engineering",   "COE"),
    ("BSME",      "Bachelor of Science in Mechanical Engineering",   "COE"),
    ("BSECE",     "Bachelor of Science in Electronics Engineering",  "COE"),
    ("BSIE",      "Bachelor of Science in Industrial Engineering",   "COE"),
    ("BSA",       "Bachelor of Science in Accountancy",             "CBA"),
    ("BSBA",      "Bachelor of Science in Business Administration",  "CBA"),
    ("BSEM",      "Bachelor of Science in Entrepreneurship",        "CBA"),
    ("BSFM",      "Bachelor of Science in Financial Management",    "CBA"),
    ("BEED",      "Bachelor of Elementary Education",               "CED"),
    ("BSED",      "Bachelor of Secondary Education",                "CED"),
    ("BSPSY",     "Bachelor of Science in Psychology",              "CAS"),
    ("BSSOC",     "Bachelor of Science in Sociology",               "CAS"),
    ("ABCOMM",    "Bachelor of Arts in Communication",              "CAS"),
    ("ABPOLSCI",  "Bachelor of Arts in Political Science",          "CAS"),
    ("BSMATH",    "Bachelor of Science in Mathematics",             "CAS"),
    ("BSBIO",     "Bachelor of Science in Biology",                 "CAS"),
    ("BSPE",      "Bachelor of Science in Physical Education",      "CHK"),
    ("BSRM",      "Bachelor of Science in Recreation Management",   "CHK"),
    ("BSN",       "Bachelor of Science in Nursing",                 "CNS"),
    ("BSPH",      "Bachelor of Science in Public Health",           "CNS"),
    ("BSND",      "Bachelor of Science in Nutrition and Dietetics", "CNS"),
    ("BSAGRI",    "Bachelor of Science in Agriculture",             "CAF"),
    ("BSFOREST",  "Bachelor of Science in Forestry",                "CAF"),
    ("BSAGRIBUS", "Bachelor of Science in Agribusiness",            "CAF"),
    ("BSANISCI",  "Bachelor of Science in Animal Science",          "CAF"),
    ("BSFISHE",   "Bachelor of Science in Fisheries",               "CAF"),
]

SEED_FIRSTNAMES = [
    "John","Mary","Jay","Aira","Mark","Jessa","Kevin","Angel","Paul","Kim",
    "Carlo","Joy","Ryan","Mae","Brian","Lyn","Chris","Anne","Jerome","Faith",
    "Ralph","Sheila","Noel","Grace","Ken","Hope","Joshua","Love","Patrick","Bless",
    "Allen","Princess","Alex","Andrea","Sean","Nicole","Jason","Karen","Richard","Donna",
    "Erwin","Cherry","Arvin","Camille","Leo","Vanessa","Bryan","Nica","Vince","Gab"
]

SEED_LASTNAMES = [
    "Santos", "Reyes", "Cruz", "Torres", "Garcia", "Flores", "Lopez", "Rivera", "Gonzalez", "Ramos",
    "Diaz", "Mendez", "Perez", "Ramirez", "Herrera", "Morales", "Gutierrez", "Ortiz", "Vargas", "Castro",
    "Jimenez", "Romero", "Moreno", "Munoz", "Alvarado", "Ruiz", "Medina", "Aguilar", "Vega", "Castillo",
    "Leon", "Delgado", "Rios", "Salazar", "Fuentes", "Campos", "Serrano", "Navarro", "Rojas", "Guerrero",
    "Soto", "Ponce", "Cabrera", "Ibarra", "Molina", "Sandoval", "Escobar", "Suarez", "Mejia", "Espinoza",
]