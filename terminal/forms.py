import re
from django import forms

TICKET_REGEX = r"(?P<TID>[A-Za-z0-9]{3,4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{5})"


class BarcodeSearchForm(forms.Form):
    barcode = forms.CharField(
        widget=forms.TextInput(
            attrs={"autofocus": True},
        )
    )

    def clean_barcode(self):
        result = re.search(TICKET_REGEX, self.cleaned_data["barcode"])
        if not result:
            self.add_error(
                "barcode",
                "Barcode content didn't match expected regex pattern",
            )
        else:
            return result.group("TID").upper()
