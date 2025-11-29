from PIL import Image

def compress_image(path, max_side: int = 1024, quality: int = 85):
    img = Image.open(path)
    img.thumbnail((max_side, max_side))
    img = img.convert("RGB")  # на всякий случай для JPEG
    img.save(path, format="JPEG", quality=quality, optimize=True)
