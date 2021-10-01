import sqlite3, os
from urllib.request import urlopen

data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(data_path, 'cmudict.db')

def create_cmudict_tuples():
    cmudict_url = 'http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b'
    cmudict_read = [line for line in urlopen(cmudict_url).readlines()]

    # filter out unwanted words from the raw list and decode the latin-1 formatting
    acceptable_indices = [69] + list(range(71,76)) + [78, 79] + list(range(81, 84)) + [85, 86] + list(range(88, 91)) + list(range(126, 133905))
    cmudict_raw = [line.decode('latin-1') for line in cmudict_read if cmudict_read.index(line) in acceptable_indices]

    cmudict_tuples = []

    for line in cmudict_raw:
        line = line.strip('\n').split('  ')
        
        word = line[0]
        pronounciation = line[1]

        cmudict_tuples.append((word, pronounciation))
      
    return cmudict_tuples

def get_rhyme_sound(pronounciation):
    pronounciation = pronounciation.split(' ')

    rhyme_sound = 'No rhyme sound'
    
    for i in range(len(pronounciation) - 1, -1, -1):
        if pronounciation[i][-1] in ['1', '2']:
            rhyme_sound = ' '.join(pronounciation[i:])
            break
    
    return rhyme_sound

def repeated_word(word):
    return word[-3:] in ['(1)', '(2)', '(3)'] 

def create_db(cmudict_raw):
    word_list = [t[0] for t in cmudict_raw]
    pronounciation_list = [t[1] for t in cmudict_raw]
    rhyme_sound_list = [get_rhyme_sound(p) for p in pronounciation_list]

    word_dict = {}
    word_id = 0

    for word in word_list:
        if not repeated_word(word):
            word_dict[word] = word_id
            word_id += 1

    words = [(item[1], item[0]) for item in word_dict.items()]

    rhyme_sound_dict = {}
    rhyme_sound_id = 0

    for rhyme_sound in rhyme_sound_list:
        if rhyme_sound not in rhyme_sound_dict.keys():
            rhyme_sound_dict[rhyme_sound] = rhyme_sound_id
            rhyme_sound_id += 1

    rhyme_sounds = [(item[1], item[0]) for item in rhyme_sound_dict.items()]

    pronounciations = []
    pron_id = 0

    for word, pron in cmudict_raw:
        if repeated_word(word):
            word_id = word_dict[word[:-3]]
        else:
            word_id = word_dict[word]

        rhyme_sound_id = rhyme_sound_dict[get_rhyme_sound(pron)]

        pronounciations.append((pron_id, pron, word_id, rhyme_sound_id))
        pron_id += 1
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS words (word_id int primary key, word text)')
    cursor.executemany('INSERT INTO words VALUES (?,?)', words)
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS rhyme_sounds (rhyme_sound_id int primary key,
                                                                rhyme_sound text)
    ''')
    cursor.executemany('INSERT INTO rhyme_sounds VALUES (?,?)', rhyme_sounds)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pronounciations (pronounciation_id int primary key,
                                                    pronounciation text,
                                                    word_id int,
                                                    rhyme_sound_id int)
                                                    
    ''')
    cursor.executemany('INSERT INTO pronounciations VALUES (?,?,?,?)', pronounciations)

    connection.commit()
    connection.close()

if __name__ == '__main__':
    cmudict_tuples = create_cmudict_tuples()
    create_db(cmudict_tuples)