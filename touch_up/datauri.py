from base64 import b64encode, b64decode
from mime_ext import get_extension

from touch_up.util import create_buffer_from_decoded

def create_datauri_from_bytes(content, mime_type) -> str:
    return "data:{};base64,{}".format(mime_type, b64encode(content).decode('utf-8'))

def parse_datauri(datauri: str) -> tuple:
    header, data = datauri.split(',')
    _, mimetype = header.split(':')
    mimetype = mimetype.replace(';base64', '')
    ext = get_extension(mimetype)
    buf = create_buffer_from_decoded(b64decode(data))
    return (buf, (mimetype, ext))