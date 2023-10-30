import io
from PIL import Image
import base64
from pix2tex.cli import LatexOCR

def get_eq_from_img(img_base64: str):
    img = base64.b64decode(img_base64)
    img = Image.open(io.BytesIO(img))
    model = LatexOCR()
    return model(img)
