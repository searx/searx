
from os.path import realpath, dirname, splitext, join
from os import listdir
from imp import load_source

engine_dir = dirname(realpath(__file__))

engines = []

for filename in listdir(engine_dir):
    modname = splitext(filename)[0]
    if filename.startswith('_') or not filename.endswith('.py'):
        continue
    filepath = join(engine_dir, filename)
    engines.append(load_source(modname, filepath))
