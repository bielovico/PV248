import sqlite3
import scorelib
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]
schema_file = './scorelib.sql'

prints = scorelib.load(input_file)

conn = sqlite3.connect(output_file)
c = conn.cursor()

with open(schema_file, 'r') as f:
    c.executescript(f.read())
conn.commit()

c.execute('CREATE TABLE person_temp (born integer, died integer, name varchar not null)')
c.execute('CREATE TABLE score_temp (name varchar, genre varchar, key varchar, incipit varchar, year integer)')

for p in prints:
    for a in p.composition().authors:
        c.execute('INSERT INTO person_temp VALUES (?, ?, ?)', (a.born, a.died, a.name))
    for e in p.edition.authors:
        c.execute('INSERT INTO person_temp VALUES (?, ?, ?)', (a.born, a.died, a.name))
    c.execute('INSERT INTO score_temp VALUES (?, ?, ?, ?, ?)', (p.composition().name, p.composition().genre, p.composition().key, p.composition().year))

c.execute("INSERT INTO person(born, died, name) SELECT MIN(born), MAX(died), name FROM person_temp WHERE name != '' GROUP BY name")
c.execute('DROP TABLE person_temp')

# dist_names = sorted(c.execute('SELECT DISTINCT name FROM person_temp').fetchall(), key = lambda a: a[0])

# for name in dist_names:
#     print(c.execute('SELECT name, MIN(born), MAX(died) FROM person_temp GROUP BY ?', name).fetchone())




conn.commit()
conn.close()

