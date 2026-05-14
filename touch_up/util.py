from os.path import basename, splitext
from numpy import frombuffer, uint8

import numpy.typing as npt

def modify_path(path, s) -> str:
    file, ext = splitext(basename(path))
    return '{}{}{}'.format(file, s, ext)

def create_buffer_from_decoded(decoded) -> npt.NDArray:
    return frombuffer(decoded, uint8)