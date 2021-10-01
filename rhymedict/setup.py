import sqlite3, os
from urllib.request import urlopen
from build.build_raw import load_raw

data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(data_path, 'cmudict.db')
repeat_suffixes = ['(1)', '(2)', '(3)']

def create_raw():
    cmudict_url = 'http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b'
    cmudict_read = [line for line in urlopen(cmudict_url).readlines()]

    # filter out unwanted words from the raw list and decode the latin-1 formatting
    acceptable_indices = [69] + list(range(71,76)) + [78, 79] + list(range(81, 84)) + [85, 86] + list(range(88, 91)) + list(range(126, 133905))
    cmudict_raw = [line.decode('latin-1') for line in cmudict_read if cmudict_read.index(line) in acceptable_indices ]
    
    with open(os.path.join(data_path, 'cmudict_raw.txt'), 'w') as file:
        for line in cmudict_raw:
            file.write(line)

def load_cmudict_tuples():
    try:
        with open(os.path.join(data_path, 'cmudict_raw.txt'), 'r') as file:
            cmudict_tuples = []

            for line in file.readlines():
                line = line.strip('\n').split('  ')
        
                word = line[0]
                pronounciation = line[1]

                cmudict_tuples.append((word, pronounciation))
            
            return cmudict_tuples
    except IOError:
        create_raw()
        load_cmudict_tuples()

def create_words_table(cmudict_tuples):
    words = []
    w_id = 0

    for w in [t[0] for t in cmudict_tuples]:
        if w[-3:] not in repeat_suffixes:
            words.append((w_id, w))
            w_id += 1

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS words (word_id int primary key, word text)')
    cur.executemany('INSERT INTO words VALUES (?,?)', words)

    conn.commit()
    conn.close()

def create_pronounciations_table(cmudict_tuples):
    pronounciations = []
    p_id = 0

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS pronounciations (pronounciation_id int primary key,
                                                    pronounciation text,
                                                    word_id int)
                                                    
    ''')

    for w,p in cmudict_tuples:
        if w[-3:] in repeat_suffixes:
            w = w[:-3]
        
        cur.execute('SELECT word_id FROM words WHERE word=?', (w,))
        w_id = cur.fetchone()[0]

        pronounciations.append((p_id, p, w_id))
        p_id += 1

    cur.executemany('INSERT INTO pronounciations VALUES (?,?,?)', pronounciations)

    conn.commit()
    conn.close()

cmudict_tuples = load_cmudict_tuples()
create_words_table(cmudict_tuples)
create_pronounciations_table(cmudict_tuples)