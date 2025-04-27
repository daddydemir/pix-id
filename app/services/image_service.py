from PIL import Image
from app.config.logging import setup_logger

logger = setup_logger(__name__)

def compress_jpeg(input_path, output_path, quality=85):
    img = Image.open(input_path)
    img.save(output_path, "JPEG", quality=quality)