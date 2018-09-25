import re
import sys

re_composer = re.compile('Composer: (.*)')
re_century = re.compile('Composition Year: ([0-9 .]*)(.* century)?')
re_key = re.compile('Key: (.*)')
pattern_date = r' \([0-9/+-]*\)'

def parse_composer(line):
    composers = re_composer.match(line)
    if composers is not None:
        composers = composers.group(1)
        composers = composers.split(';')
        for composer in composers:
            composer = re.sub(pattern_date, '', composer)
            composer = composer.strip()
            if composer != '':
                c = pieces_by_composer.get(composer)
                if c is None:
                    pieces_by_composer[composer] = 1
                else:
                    pieces_by_composer[composer] += 1
    return

def print_composers():
    for composer, pieces in pieces_by_composer.items():
        print('%s: %d' % (composer, pieces)) 
    return

def parse_century(line):
    year = re_century.match(line)
    if year is not None:
        year = year.group(1)
        y = year.split('.')
        if len(y) > 1:
            year = y[-1]
        year = year.strip()
        if year != '':
            if len(year) == 2:
                c = pieces_by_century.get(year)
                if c is None:
                    pieces_by_century[year] = 1
                else:
                    pieces_by_century[year] += 1
            else:
                pass
            print(year)
    return

def print_centuries():
    for century, pieces in pieces_by_century.items():
        print('%s: %d' % (century, pieces))
    return

def parse_key(line):
    keys = re_key.match(line)
    if keys is not None:
        print(keys.group(1))
    return

def print_keys():
    for key, pieces in pieces_by_key.items():
        print('%s: %d' % (key, pieces)) 
    return

parsers = {'composer':parse_composer, 'century':parse_century, 'key':parse_key}
printers = {'composer':print_composers, 'century':print_centuries, 'key':print_keys}
pieces_by_composer = {}
pieces_by_century = {}
pieces_by_key = {}

file_path = sys.argv[1]
mode = sys.argv[2]

def main():
    if mode not in parsers:
        print('Invalid mode!')
        return
    parser = parsers[mode]
    printer = printers[mode]
    for line in open(file_path, mode='rt', encoding='utf-8'):
        parser(line)
    printer()

if __name__ == '__main__':
    main()