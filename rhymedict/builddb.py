import buildraw

# try load the raw cmudict data
# on a failure to load, build it
def load_raw():
    try:
        with open(buildraw.cmudictraw_path, 'r') as file:
            return [line.strip('\n') for line in file.readlines()]
    except IOError:
        buildraw.buildraw()

        with open(buildraw.cmudictraw_path, 'r') as file:
            return [line.strip('\n') for line in file.readlines()]

cmudict_raw = load_raw()