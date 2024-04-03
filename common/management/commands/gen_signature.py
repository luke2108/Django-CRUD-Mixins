from io import BytesIO

import pdfkit
import PyPDF2

from django.conf import settings
from django.core.management.base import BaseCommand

from utilities.seal.seal import Seal

class Command(BaseCommand):
    def handle(self, *args, **options):
        seal = Seal()
        text = "KIET"
        seal.draw_seal(text)
        # pngImageB64String = "data:image/png;base64,"
        # image_base64 = pngImageB64String + image.decode("utf-8")
