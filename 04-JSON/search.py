import sqlite3
import sys
import json

conn = sqlite3.connect('scorelib.dat')
c = conn.cursor()

name = sys.argv[1]

def get_print(print_id):
    print_dict = {}
    print_info = c.execute("SELECT print.partiture, edition.name, edition.year, score.name, score.year, score.genre, score.incipit, score.key, edition.id, score.id \
                FROM (print JOIN edition ON print.edition == edition.id) JOIN score ON edition.score == score.id \
                WHERE print.id == ?", (print_id,)).fetchone()
    print_dict['Print Number'] = print_id
    if print_info[0] == "Y":
        print_dict['Partiture'] = True
    else:
        print_dict['Partiture'] = False
    print_dict['Edition'] = print_info[1]
    print_dict['Publication Year'] = print_info[2]
    print_dict['Title'] = print_info[3]
    print_dict['Compostition Year'] = print_info[4]
    print_dict['Genre'] = print_info[5]
    print_dict['Incipit'] = print_info[6]
    print_dict['Key'] = print_info[7]

    editors = []
    c.execute("SELECT person.name, person.born, person.died FROM edition_author JOIN person ON edition_author.editor == person.id \
            WHERE edition_author.edition == ?", (print_info[8],))
    for name, born, died in c:
        editors.append(dict(name=name, born=born, died=died))
    print_dict['Editor'] = editors    

    composers = []
    c.execute("SELECT person.name, person.born, person.died FROM score_author JOIN person ON score_author.composer == person.id \
                WHERE score_author.score == ?", (print_info[9],))
    for name, born, died in c:
        composers.append(dict(name=name, born=born, died=died))
    print_dict['Composer'] = composers

    voices=[]
    c.execute("SELECT name, range FROM voice WHERE score == ? ORDER BY number ASC", (print_info[9],))
    for name, range in c:
        voices.append(dict(name=name, range=range))
    print_dict['Voices'] = voices

    return print_dict

results = c.execute("SELECT person.id, person.name FROM \
            score_author JOIN person ON score_author.composer == person.id WHERE person.name LIKE ? GROUP BY person.id", ('%'+name+'%',)).fetchall()

out = {}

for c_id, c_name in results:
    prints = []
    print_ids = c.execute("SELECT id FROM print WHERE edition IN (SELECT id FROM edition WHERE score IN (SELECT score FROM score_author WHERE composer == ?))", \
                            (c_id,)).fetchall()
    for p in print_ids:
        prints.append(get_print(p[0]))

    out[c_name] = prints

print(json.dumps(out, ensure_ascii=False, indent=4))
