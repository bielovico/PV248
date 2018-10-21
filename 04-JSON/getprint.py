import sqlite3
import sys
import json

print_id = sys.argv[1]

conn = sqlite3.connect('scorelib.dat')
c = conn.cursor()

c.execute("SELECT person.name, person.born, person.died FROM \
            ((print JOIN edition ON print.edition == edition.id) JOIN score_author ON score_author.score == edition.score) JOIN person ON person.id == score_author.composer \
            WHERE print.id == ?", (print_id,))

authors = []
for name, born, died in c:
    authors.append(dict(name=name, born=born, died=died))

print(json.dumps(authors, ensure_ascii=False, indent=4))


