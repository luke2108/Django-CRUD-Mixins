import io

from PIL import Image


def resize_image(data: io.BytesIO, max_width: int, max_height: int) -> bytes:
    img = Image.open(data)
    # リサイズ
    img.thumbnail(size=(max_width, max_height))
    # Exif取得
    exif_dict = img.info.get("exif", bytes())

    img_bytes = io.BytesIO()
    img.save(img_bytes, img.format, exif=exif_dict)
    return img_bytes.getvalue()
