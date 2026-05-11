from os.path import basename, splitext
from numpy import frombuffer, uint8

def modify_path(path, s):
    file, ext = splitext(basename(path))
    return '{}{}{}'.format(file, s, ext)

def create_buffer_from_decoded(decoded):
    return frombuffer(decoded, uint8)