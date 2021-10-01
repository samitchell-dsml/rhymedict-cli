"""

--------------------------------------------------------
RHYMEDICT: command line tool for getting all the words 
which rhyme with a user entered word. User word and
given rhyming words are from the CMU Pronouncing
Dictionary.
--------------------------------------------------------

Usage: rhymedict <options> word

Options:
    -l --letter     Show all rhyming words starting with given letter
    --help          Show this message and exit.

"""

import click, sqlite3

def in_dict(cur, word):
    cur.execute('''
        SELECT
            word
        FROM
            words
        WHERE
            word = ?
    ''', (word,))

    return cur.fetchall()

def get_rhyme_sound(pronounciation):
    pronounciation = pronounciation.split(' ')

    rhyme_sound = 'No rhyme sound'
    
    for i in range(len(pronounciation) - 1, -1, -1):
        if pronounciation[i][-1] in ['1', '2']:
            rhyme_sound = ' '.join(pronounciation[i:])
            break
    
    return rhyme_sound

def get_pronounciations(cur, word):
    cur.execute('''
        SELECT
            word,
            pronounciation
        FROM
            pronounciations
        INNER JOIN words ON words.word_id = pronounciations.word_id
        WHERE
            word = ?
    ''', (word.upper(),))

    return set([t[1] for t in cur.fetchall()])

def get_rhyme_lists(cur, word):
    rhyme_lists = {}

    for pron in get_pronounciations(cur, word):
        cur.execute('''
            SELECT
                word
            FROM
                pronounciations
            INNER JOIN words ON words.word_id = pronounciations.word_id
            INNER JOIN rhyme_sounds ON rhyme_sounds.rhyme_sound_id = pronounciations.rhyme_sound_id
            WHERE
                rhyme_sound = ?
            AND
                word != ?
            AND
                rhyme_sound != ?
        ''', (get_rhyme_sound(pron),word,'No rhyme sound',))
        
        rhyme_lists[pron] = list(set([t[0] for t in cur.fetchall()]))
        rhyme_lists[pron].sort()

    return rhyme_lists

def print_rhymes(word, letter, rhyme_lists, in_dict):
    if in_dict:
        if letter:
            print('\n\t Words which rhyme with: {}, beginning with letter: {} \n'.format(word, letter))
        else:
            print('\n\t Words which rhyme with: {} \n'.format(word))
        
        for pron in sorted(rhyme_lists.keys()):
            rhyme_list = rhyme_lists[pron]

            if letter: 
                rhyme_list = [w for w in rhyme_list if w[0] == letter]

            print('\t\t Pronounciation: {}'.format(pron))
            print('\n\t\t\t', end='')

            if rhyme_list:
                print('\n\t\t\t'.join(['  '.join(rhyme_list[i:i+8]) for i in range(0, len(rhyme_list), 8)]) + '\n')
            else:
                print('No rhyme exists \n')
    else:
        print('\n\t The word {} is not in the CMU Pronouncing Dictionary \n'.format(word))

@click.command()
@click.argument('word')
@click.option('--letter', '-l', help='Show all rhyming words starting with given letter')
def main(word, letter):
    word = word.upper()
    
    if letter:
        letter = letter.upper()

    conn = sqlite3.connect('./cmudict.db')
    cur = conn.cursor()

    print_rhymes(word, letter, get_rhyme_lists(cur,word), in_dict(cur,word))

    conn.close()

if __name__ == '__main__':
    main()
