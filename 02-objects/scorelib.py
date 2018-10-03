import re

re_composer = re.compile('Composer: (.*)')
re_print_id = re.compile('Print Number: ([0-9]*)')
re_edition = re.compile('Edition: (.*)')
re_editor = re.compile('Editor: (.*)')
re_partiture = re.compile('Partiture: (.*)')
re_range = re.compile('.*?([a-zA-Z0-9]*-{1,2}[a-zA-Z0-9]*).*')
re_dates = re.compile(r'.*?(\(\*?([0-9]{4})?-{0,2}\+?([0-9]{4})?\)).*')


class Print:
    def __init__(self, print_id, edition = None, partiture = None):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture
    def format(self):
        print('Print Number:', self.print_id)
        print('Composer:', '; '.join([str(p) for p in self.composition().authors]))
        print('Title:', self.composition().name)
        print('Genre:', self.composition().genre)
        print('Key:', self.composition().key)
        print('Composition Year:', self.composition().year)
        print('Publication Year: ')
        print('Edition:', self.edition.name)
        print('Editor:', ''.join([str(p) for p in self.edition.authors]))
        for i,voice in enumerate(self.composition().voices):
            print('Voice ', str(i+1), ': ', str(voice), sep='')
        print('Partiture:', 'yes' if self.partiture else 'no')
        print('Incipit:', self.composition().incipit)
    def composition(self):
        return self.edition.composition

class Edition:
    composition = None
    authors = []
    name = None
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name


class Composition:
    name = None
    incipit = None
    key = None
    genre = None
    year = None
    voices = []
    authors = []
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors
    

class Voice:
    def __init__(self, name, range = None):
        self.name = name
        self.range = range
    def __str__(self):
        out = ''
        if self.range is not None:
            out += self.range + ', '
        out += self.name
        return out

class Person:
    def __init__(self, name="", born=None, died=None):
        self.name = name
        self.born = born
        self.died = died
        self.dates_known = born is not None or died is not None
    def __str__(self):
        out = self.name
        if self.dates_known:
            out += ' ('
            if self.born is not None:
                out += self.born
            out += '--'
            if self.died is not None:
                out += self.died
            out += ')'
        return out

def parse_print(p):
    p = p.strip()
    ps = p.split('\n')
    
    print_id = int(ps[0].split(':')[1])
    
    composers = ps[1].split(':')[1]
    composers = composers.split(';')
    authors = []
    for composer in composers:
        dates = re_dates.match(composer)
        if dates is not None:
            born = dates.group(2)
            died = dates.group(3)
            name = composer[:dates.start(1)] + composer[dates.end(1):]
            name = name.strip()
            person = Person(name, born, died)
            authors.append(person)
        else:
            authors.append(Person(composer.strip()))

    title = ps[2].split(':')[1]

    genres = ps[3].split(':')[1]
    # genres = genres.split(',')
    
    key = ps[4].split(':')[1]
    
    c_year = ps[5].split(':')[1]
    c_year = c_year.strip()
    if re.match('^[0-9]{4}$', c_year) is not None:
        c_year = int(c_year)
    
    # p_year = ps[6].split(':')[1]
    
    edition_name = ps[7].split(':')[1]
    
    editors = ps[8].split(':')[1]
    edit_authors = []
    dates = re_dates.match(editors)
    if dates is not None:
        born = dates.group(2)
        died = dates.group(3)
        name = editors[:dates.start(1)] + editors[dates.end(1):]
        name = name.strip()
        person = Person(name, born, died)
        edit_authors.append(person)
    else:
        edit_authors.append(Person(editors))

    voices = []
    current_line = 9
    for line in ps[9:-1]:
        if line[0] == 'V':
            v = line.split(':')[1]
            range = re_range.match(v)
            if range is not None:
                range = range.group(1)
                v = re.sub(range + ',? ?', '', v)
                voice = Voice(v, range)
                voices.append(voice)
            else:
                voices.append(Voice(v))
            current_line += 1
        else:
            break

    partiture_line = current_line
    partiture = ps[partiture_line].split(':')[1]
    partiture = partiture.strip()
    if len(partiture) >= 3 and partiture[:3] == 'yes':
        partiture = True
    else:
        partiture = False

    incipit = ps[partiture_line+1].split(':')[1]

    composition = Composition(title, incipit, key, genres, c_year, voices, authors)
    edition = Edition(composition, edit_authors, edition_name)
    pr = Print(print_id, edition, partiture)
    return pr

    


    

def load(filename):
    f = open(filename, mode='rt', encoding='utf-8')
    data = f.read()
    f.close()
    prints = data.split('\n\n')
    pps = []
    for p in prints:
        pp = parse_print(p)
        pps.append(pp)
    return sorted(pps, key=lambda p: p.print_id)
