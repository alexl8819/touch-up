from base64 import b64decode
from cv2 import imread, imencode, imdecode, imwrite, rectangle, IMREAD_COLOR
from pytesseract import image_to_data, Output
from presidio_analyzer import AnalyzerEngine, PatternRecognizer

from util import modify_path, create_buffer_from_decoded
from datauri import parse_datauri, create_datauri_from_bytes

def _word_overlaps_entity(word, entity):
    return not (word["end"] <= entity.start or word["start"] >= entity.end)

# Removes pii entities from an image by extracting text via ocr (tesseract) 
# then applies a black rectangular overlay where its positioned
# TODO: custom entities need to be passed through for better accuracy via deny-lists
def _redact_entities(img, fields):
    ocr = image_to_data(img, output_type=Output.DICT)
    words = []
    full_text_parts = []
    cursor = 0

    for i in range(len(ocr["text"])):
        text = ocr["text"][i].strip()
        if not text:
            continue

        start = cursor
        end = start + len(text)
        words.append({
            "text": text,
            "start": start,
            "end": end,
            "left": ocr["left"][i],
            "top": ocr["top"][i],
            "width": ocr["width"][i],
            "height": ocr["height"][i],
        })

        full_text_parts.append(text)
        cursor = end + 1

    full_text = " ".join(full_text_parts)
    analyzer = AnalyzerEngine()
    results = analyzer.analyze(
        text=full_text,
        language="en",
        entities=fields
    )
    boxes_to_redact = []

    for entity in results:
        for word in words:
            if _word_overlaps_entity(word, entity):
                boxes_to_redact.append(word)
    
    for word in boxes_to_redact:
        x, y, w_box, h_box = word["left"], word["top"], word["width"], word["height"]
        rectangle(img, (x, y), (x + w_box, y + h_box), (0, 0, 0), -1)
    
    return img

def redact_from_datauri(datauri, fields=["PERSON", "ADDRESS", "LOCATION", "PHONE_NUMBER", "EMAIL_ADDRESS"]):
    buf, parsed_mime = parse_datauri(datauri)
    mimetype, ext = parsed_mime
    img = imdecode(buf, IMREAD_COLOR)
    redacted = _redact_entities(img, fields)
    _, encoded = imencode("{}".format(ext), redacted)
    return create_datauri_from_bytes(encoded, mimetype)

def redact_from_image(path, fields=["PERSON", "ADDRESS", "LOCATION", "PHONE_NUMBER", "EMAIL_ADDRESS"], postprocess="_redacted"):
    img = imread(path)
    redacted = _redact_entities(img, fields)
    imwrite(modify_path(path, postprocess), img)