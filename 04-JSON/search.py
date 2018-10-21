import sqlite3
import sys
import json

conn = sqlite3.connect('scorelib.dat')
c = conn.cursor()

name = sys.argv[1]

results = c.execute("SELECT person.id, person.name, group_concat(score_author.score, ',') FROM \
            score_author JOIN person ON score_author.composer == person.id WHERE person.name LIKE ? GROUP BY person.id", ('%'+name+'%',)).fetchall()

out = {}

for c_id, c_name, score_ids in results:
    prints = []

    out[c_name] = prints

print(json.dumps(out, ensure_ascii=False, indent=4))
