from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe


class HTML5QRTextInput(TextInput):
    def __init__(self, *args, **kwargs):
        kwargs["attrs"]["data-reader-input"] = 1
        super().__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        result = super().render(*args, **kwargs)
        return mark_safe(
            f"""<div
        id='{kwargs['attrs']['id']}_qr_reader'
        data-reader-scanner="1">
        </div>
        {result}"""
        )

    class Media:
        js = ["html5-qrcode.min.js", "django_barcode.js"]
