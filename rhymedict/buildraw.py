from urllib.request import urlopen
from os import path

cmudict_url = 'http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b'
cmudictraw_path = path.join(path.dirname(__file__), 'data/cmudictraw.txt')

def buildraw():
    cmudict_raw = [line for line in urlopen(cmudict_url).readlines()]

    
    # filter out unwanted words from the raw list and decode the latin-1 formatting
    acceptable_indices = [69] + list(range(71,76)) + [78, 79] + list(range(81, 84)) + [85, 86] + list(range(88, 91)) + list(range(126, 133905))
    cmudict = [line.decode('latin-1') for line in cmudict_raw if cmudict_raw.index(line) in acceptable_indices ]

    with open(cmudictraw_path, 'w') as file:
        for line in cmudict:
            file.write(line)