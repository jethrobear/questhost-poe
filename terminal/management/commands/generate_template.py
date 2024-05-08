from pathlib import Path
import pickle
from tempfile import gettempdir
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
import qrcode
from terminal.models import *


class Command(BaseCommand):
    help = "Generate label image"

    def add_arguments(self, parser):
        parser.add_argument("print_id", type=int)
        parser.add_argument("max_width", type=int)

    def handle(self, *args, **options):
        # Get print job
        object = PrintJob.objects.get(pk=options["print_id"])
        filepath = object.image_path
        if not (filepath and Path(filepath).exists()):
            print_obj = pickle.loads(object.print_blob)
            print_id = getattr(print_obj, object.print_id)

            # Generate printable item
            qrimg: Image.Image = qrcode.make(print_id)
            qrimg = qrimg.resize((180, 180))
            baseimg = Image.new("1", (600, 180), 1)
            baseimg.paste(qrimg, (0, 0))

            draw = ImageDraw.ImageDraw(baseimg)
            ocrfontpath = Path(__file__).parent.joinpath("OCRA.otf")
            fnt = ImageFont.truetype(str(ocrfontpath), 38)
            draw.text((180, 0), print_id, font=fnt)
            draw.text((180, 90), print_obj.__class__.__name__, font=fnt)

            # Convert and save image to temp
            ratio = options["max_width"] / baseimg.size[1]
            new_size = (int(baseimg.size[0] * ratio), int(baseimg.size[1] * ratio))
            baseimg = baseimg.resize(new_size)
            filepath = Path(gettempdir()).joinpath(f"QH_PRINTSPOOL_{object.id}.png")
            baseimg.save(filepath, format="png")
            object.image_path = filepath
            object.save()
        return str(filepath)
