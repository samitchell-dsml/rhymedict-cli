import sqlite3, os
from urllib.request import urlopen

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

def load_cmudict_raw():
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

def get_rhyme_sound(pronounciation):
    pronounciation = pronounciation.split(' ')

    rhyme_sound = 'No rhyme sound'
    
    for i in range(len(pronounciation) - 1, -1, -1):
        if pronounciation[i][-1] in ['1', '2']:
            rhyme_sound = ' '.join(pronounciation[i:])
            break
    
    return rhyme_sound

def create_words_table(cursor, words):
    word_id_tuples = []
    word_id = 0

    for word in words:
        if word[-3:] not in repeat_suffixes:
            word_id_tuples.append((word_id, word))
            word_id += 1

    cursor.execute('CREATE TABLE IF NOT EXISTS words (word_id int primary key, word text)')
    cursor.executemany('INSERT INTO words VALUES (?,?)', word_id_tuples)

def create_pronounciations_table(cursor, cmudict_tuples):
    prounounciation_id_tuples = []
    pronounciation_id = 0

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pronounciations (pronounciation_id int primary key,
                                                    pronounciation text,
                                                    word_id int)
                                                    
    ''')

    for word,pronounciation in cmudict_tuples:
        if word[-3:] in repeat_suffixes:
            word = word[:-3]
        
        cursor.execute('SELECT word_id FROM words WHERE word=?', (word,))
        word_id = cursor.fetchone()[0]

        prounounciation_id_tuples.append((pronounciation_id, pronounciation, word_id))
        pronounciation_id += 1

    cursor.executemany('INSERT INTO pronounciations VALUES (?,?,?)', prounounciation_id_tuples)

def create_rhyme_sounds_table(cursor, pronounciations):
    rhyme_sounds = []
    rhyme_sound_id = 0

    for pronounciation in pronounciations:
        rhyme_sound_id_tuple = (rhyme_sound_id, get_rhyme_sound(pronounciation))

        if rhyme_sound_id_tuple not in rhyme_sounds:
            rhyme_sounds.append(rhyme_sound_id_tuple)
            rhyme_sound_id += 1
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS rhyme_sounds (rhyme_sound_id int primary key,
                                                                rhyme_sound text)
    ''')
    cursor.executemany('INSERT INTO rhyme_sounds VALUES (?,?)', rhyme_sounds)

def create_cmudict(cmudict_raw):

    return 0

def create_db(cmudict):

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS words (word_id int primary key, word text)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rhyme_sounds (rhyme_sound_id int primary key,
                                                                rhyme_sound text)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pronounciations (pronounciation_id int primary key,
                                                    pronounciation text,
                                                    word_id int)
                                                    
    ''')

    connection.commit()
    connection.close()

    return 0


if __name__ == '__main__':
    cmudict_raw = load_cmudict_raw()[:100]
    create_db(cmudict_raw)