import base64
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AREA_SEAL_1,
    AREA_SEAL_2,
    AREA_SEAL_3,
    AREA_SEAL_4,
    AREA_SEAL_5,
    AREA_SEAL_6,
)


class Seal:
    def draw_seal(self, text):
        print(text)
        image = Image.new("RGBA", (1080, 1080), (200, 1, 1, 1))
        font = ImageFont.truetype(r"utilities/seal/YujiBoku-Regular.ttf", 100)
        draw = ImageDraw.Draw(image)

        if len(text) == 1:
            image = self.draw_seal_1([c for c in text], image, font, draw)
        if len(text) == 2:
            image = self.draw_seal_2([c for c in text], image, font, draw)
        if len(text) == 3:
            image = self.draw_seal_3([c for c in text], image, font, draw)
        if len(text) == 4:
            image = self.draw_seal_4([c for c in text], image, font, draw)
        if len(text) == 5:
            image = self.draw_seal_5([c for c in text], image, font, draw)
        if len(text) == 6:
            image = self.draw_seal_6([c for c in text], image, font, draw)

        image.show()
        image.save("output.png")

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        return img_str

    def draw_seal_1(self, text, image, font, draw):
        text = text[0]
        draw.text((500, 500), text, fill="red", font=font, align="left")

        draw.ellipse(AREA_SEAL_1, fill=None, outline="red", width=9)

        image = image.crop(AREA_SEAL_1)

        return image

    def draw_text_in_line(self, text, font, draw, y, x, gap):
        for c in text:
            draw.text((x, y), c, fill="red", font=font, align="left")
            y = y + gap

        return draw

    def draw_seal_2(self, text, image, font, draw):
        draw = self.draw_text_in_line(text, font, draw, 500, 500, 85)

        draw.ellipse(AREA_SEAL_2, fill=None, outline="red", width=9)

        image = image.crop(AREA_SEAL_2)

        return image

    def draw_seal_3(self, text, image, font, draw):
        draw = self.draw_text_in_line(text, font, draw, 500, 500, 85)

        draw.ellipse(AREA_SEAL_3, fill=None, outline="red", width=9)

        image = image.crop(AREA_SEAL_3)

        return image

    def draw_seal_4(self, text, image, font, draw):
        draw = self.draw_text_in_line(text[0:2], font, draw, 500, 500, 100)
        draw = self.draw_text_in_line(text[2:], font, draw, 500, 400, 100)

        draw.ellipse(AREA_SEAL_4, fill=None, outline="red", width=9)

        image = image.crop(AREA_SEAL_4)

        return image

    def draw_seal_5(self, text, image, font, draw):
        draw = self.draw_text_in_line(text[0:2], font, draw, 500, 500, 100)
        draw = self.draw_text_in_line(text[2:4], font, draw, 500, 400, 100)
        draw = self.draw_text_in_line(text[-1], font, draw, 700, 450, 100)

        draw.ellipse(AREA_SEAL_5, fill=None, outline="red", width=9)

        image = image.crop(AREA_SEAL_5)

        return image

    def draw_seal_6(self, text, image, font, draw):
        draw = self.draw_text_in_line(text[0:3], font, draw, 500, 500, 100)
        draw = self.draw_text_in_line(text[3:], font, draw, 500, 400, 100)

        draw.ellipse(AREA_SEAL_6, fill=None, outline="red", width=9)

        image = image.crop(AREA_SEAL_6)

        return image
