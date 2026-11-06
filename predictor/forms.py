# predictor/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Rental, Land


class RentalPredictionForm(forms.Form):
    town = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    access_type = forms.ChoiceField(choices=Rental.AccessType.choices, label=_("Access type"),
                                    widget=forms.Select(attrs={'class': 'form-select'}))
    property_type = forms.ChoiceField(choices=Rental.PropertyType.choices, label=_("Property type"),
                                      widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    num_rooms = forms.IntegerField(label=_("Num rooms"), min_value=1, initial=1,
                                   widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # === [THE FOOLPROOF FIX] ===
    # Directly define the field with ALL possible choices from the start.
    # This ensures that any submitted value ('T1', 'F1', etc.) will be valid.
    # The JavaScript on the front-end will still manage what the user sees.
    subtype = forms.ChoiceField(
        choices=Rental.ApartmentSubtype.choices + Rental.HouseSubtype.choices,
        label=_("Apartment type"),  # JS will change this label
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # ============================

    exterior_showers_toilets = forms.BooleanField(required=False, label=_("Exterior showers & toilets"),
                                                  widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    interior_showers_toilets = forms.BooleanField(required=False, label=_("Interior showers & toilets"),
                                                  widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    garage = forms.BooleanField(required=False, label=_("Garage"),
                                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    garden = forms.BooleanField(required=False, label=_("Garden"),
                                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # We no longer need the __init__ method for this fix.
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     all_subtypes = list(Rental.ApartmentSubtype.choices) + list(Rental.HouseSubtype.choices)
    #     self.fields['subtype'].choices = all_subtypes


# LandPredictionForm and CSVUploadForm remain the same
class LandPredictionForm(forms.Form):
    town = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    paper_type = forms.ChoiceField(
        label=_("Paper type"),
        choices=Land.PaperType.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    access_type = forms.ChoiceField(
        label=_("Access type"),
        choices=Land.AccessType.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # New field for the user to input
    superficy = forms.DecimalField(
        label=_("Superficy (in m²)"),
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500'})
    )
    is_fenced = forms.BooleanField(
        required=False,
        label=_("Is fenced"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_ready_to_build = forms.BooleanField(
        required=False,
        label=_("Is ready to build"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label=_("Select a CSV file"))