from base64 import b64encode, b64decode
from mime_ext import get_extension
from cv2 import imread, imencode, imdecode, imwrite, cvtColor, threshold, equalizeHist, createCLAHE, Laplacian, CV_64F, IMREAD_COLOR, THRESH_BINARY, COLOR_BGR2GRAY, fastNlMeansDenoising, resize, INTER_AREA

from util import modify_path, create_buffer_from_decoded
from datauri import parse_datauri, create_datauri_from_bytes
from pii import redact_from_image

# grayscales image, enhances contrast for text, attempts to remove noise artifacts
def _enhance_image(img):
    grayscaled = cvtColor(img, COLOR_BGR2GRAY)
    clahe = createCLAHE(clipLimit=2.0, tileGridSize=(64, 64))
    clahe_image = clahe.apply(grayscaled)
    _, thresh = threshold(clahe_image, 100, 255, THRESH_BINARY)
    return fastNlMeansDenoising(thresh, None, 30, 7, 21)

# resizes image to downscale
def _resize_image(img, max_dim=2048):
    h, w = img.shape[:2]
    
    if max(h, w) <= max_dim:
        return img

    scale = max_dim / max(h, w)
    new_size = (int(w * scale), int(h * scale))
    return resize(img, new_size, interpolation=INTER_AREA)

def enhance_image_from_datauri(datauri):
    buf, parsed_mime = parse_datauri(datauri)
    mimetype, ext = parsed_mime
    img = imdecode(buf, IMREAD_COLOR)
    downscale = _resize_image(img)
    enhanced = _enhance_image(downscale) 
    _, encoded = imencode("{}".format(ext), enhanced)
    return create_datauri_from_bytes(encoded, mimetype)

def enhance_image_from_path(path, postprocess="_enhanced"):
    img = imread(path)
    enhanced = _enhance_image(img)
    imwrite(modify_path(path, postprocess), denoised)

def is_blurry(img, threshold=100): # < 100 is moderately blurry
    laplacian = Laplacian(img, CV_64F)
    variance = laplacian.var()
    return variance < threshold

def is_low_contrast(img, threshold=30): # < 30 is too low of contrast
    return img.std() < threshold

def has_noise(img, threshold=50): # Noise is adjustable, anything greater than 50 is acceptable
    return img.var() < threshold

# uses thresholds to determine if an image requires pre-processing
def should_preprocess_from_datauri(datauri):
    buf = create_buffer_from_decoded(b64decode(datauri.split(',')[1]))
    image = imdecode(buf, IMREAD_COLOR)
    grayscaled = cvtColor(image, COLOR_BGR2GRAY)
    return is_blurry(grayscaled) or is_low_contrast(grayscaled) or has_noise(grayscaled)

def should_preprocess_from_path(path):
    image = imread(path)
    grayscaled = cvtColor(image, COLOR_BGR2GRAY)
    return is_blurry(grayscaled) or is_low_contrast(grayscaled) or has_noise(grayscaled)