import sqlite3
import scorelib
import sys
import json

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
c.execute('CREATE TABLE score_temp (fid integer, name varchar, genre varchar, key varchar, incipit varchar, year integer, composers varchar, voices varchar)')
c.execute('CREATE TABLE score_full (id integer primary key not null, name varchar, genre varchar, key varchar, incipit varchar, year integer, composers varchar, voices varchar)')
c.execute('CREATE TABLE edition_temp (score integer, name varchar, year integer, editors varchar)')
c.execute('CREATE TABLE edition_full (id integer primary key not null, score integer, name varchar, year integer, editors varchar)')
c.execute('CREATE TABLE print_temp (id integer, partiture char(1), edition integer, temp_id integer)')



for i,p in enumerate(prints):
    for a in p.composition().authors:
        c.execute('INSERT INTO person_temp VALUES (?, ?, ?)', (a.born, a.died, a.name))
    for a in p.edition.authors:
        c.execute('INSERT INTO person_temp VALUES (?, ?, ?)', (a.born, a.died, a.name))
    c.execute('INSERT INTO score_temp VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (i, p.composition().name, p.composition().genre, p.composition().key, p.composition().incipit, p.composition().year, json.dumps([a.name for a in p.composition().authors], ensure_ascii=False), json.dumps([(v.date_range,v.name) for v in p.composition().voices], ensure_ascii=False)))
    # for i, v in enumerate(p.composition().voices):
    #     c.execute('INSERT INTO voice_temp VALUES (?, ?, ?, ?)', (i, c.lastrowid, v.date_range, v.name))
    c.execute('INSERT INTO edition_temp VALUES (?, ?, ?, ?)', (i, p.edition.name, None, json.dumps([a.name for a in p.edition.authors], ensure_ascii=False)))
    c.execute('INSERT INTO print_temp VALUES (?, ?, ?, ?)', (p.print_id, '{}'.format('Y' if p.partiture else 'N'), None, i))    

c.execute("INSERT INTO person(born, died, name) SELECT MIN(born), MAX(died), name FROM person_temp WHERE name != '' GROUP BY name")
c.execute('DROP TABLE person_temp')
c.execute('INSERT INTO score_full(name, genre, incipit, key, year, composers, voices) SELECT name, genre, incipit, key, year, composers, voices FROM score_temp GROUP BY name, genre, incipit, key, year, composers, voices')
editions = c.execute("SELECT * FROM edition_temp WHERE not(name isnull and year isnull and editors=='[]')").fetchall()
for edition in editions:
    score = c.execute("SELECT name, genre, incipit, key, year, composers, voices FROM score_temp WHERE fid = ?", (edition[0],)).fetchone()
    score_id = c.execute("SELECT id FROM score_full WHERE name = ? and genre = ? and incipit = ? and key=? and year=? and composers=? and voices=?", (score[0], score[1], score[2], score[3], score[4], score[5], score[6])).fetchone()[0]
    c.execute("INSERT INTO edition_full(score, name, year, editors) VALUES (?, ?, ?, ?)", (score_id, edition[1], edition[2], edition[3]))

editions = c.execute("SELECT score FROM edition_temp WHERE not(name isnull and year isnull and editors=='[]')").fetchall()
for i,e in enumerate(editions):
    e_id = i
    p_id = e[0]
    c.execute("UPDATE print_temp SET edition = ? WHERE temp_id = ?", (e_id, p_id))
c.execute("INSERT INTO print SELECT id, partiture, edition FROM print_temp")

voice_list = c.execute('SELECT id, voices FROM score_full').fetchall()
for row in voice_list:
    voices = json.loads(row[1])
    for i, v in enumerate(voices):
        c.execute('INSERT INTO voice(number, score, range, name) VALUES (?, ?, ?, ?)', (i+1, row[0], v[0], v[1]))

composers_list = c.execute('SELECT id, composers FROM score_full').fetchall()
persons_list = c.execute('SELECT name, id FROM person').fetchall()
persons_dict = dict(persons_list)
for row in composers_list:
    composers = json.loads(row[1])
    for a in composers:
        c.execute('INSERT INTO score_author(score, composer) VALUES (?, ?)', (row[0], persons_dict[a]))
editors_list = c.execute('SELECT id, editors FROM edition_full').fetchall()
for row in editors_list:
    editors = json.loads(row[1])
    for a in editors:
        c.execute('INSERT INTO edition_author(edition, editor) VALUES (?, ?)', (row[0], persons_dict[a]))

c.execute('INSERT INTO score(name, genre, incipit, key, year) SELECT name, genre, incipit, key, year FROM score_full')
c.execute("INSERT INTO edition(score, name, year) SELECT score, name, year FROM edition_full")

c.execute('DROP TABLE score_temp')
c.execute('DROP TABLE score_full')
c.execute('DROP TABLE edition_temp')
c.execute('DROP TABLE edition_full')
c.execute('DROP TABLE print_temp')

conn.commit()
conn.close()

