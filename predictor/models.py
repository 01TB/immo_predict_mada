# predictor/models.py

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Town(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Town Name"))
    location = models.PointField(srid=4326, verbose_name=_("Location on Map"))

    def __str__(self): return self.name

    class Meta:
        verbose_name = _("Town")
        verbose_name_plural = _("Towns")


class Rental(models.Model):
    class AccessType(models.TextChoices):
        NO_ACCESS = 'sans_acces', _('Sans accès')
        MOTO = 'acces_moto', _('Accès moto')
        CAR = 'acces_voiture', _('Accès voiture')
        CAR_PARKING = 'acces_voiture_parking', _('Accès voiture + parking')

    class PropertyType(models.TextChoices):
        APARTMENT = 'APARTMENT', _('Apartment')
        HOUSE = 'HOUSE', _('House')

    # === [CORRECTION] REMOVED ALL SEMICOLONS ===
    class ApartmentSubtype(models.TextChoices):
        T1 = 'T1', 'T1'
        T2 = 'T2', 'T2'
        T3 = 'T3', 'T3'
        T4 = 'T4', 'T4'
        T5 = 'T5', 'T5'
        T6 = 'T6', 'T6'

    class HouseSubtype(models.TextChoices):
        F1 = 'F1', 'F1'
        F2 = 'F2', 'F2'
        F3 = 'F3', 'F3'
        F4 = 'F4', 'F4'
        F5 = 'F5', 'F5'
        F6 = 'F6', 'F6'

    # ============================================

    town = models.ForeignKey(Town, on_delete=models.CASCADE, verbose_name=_("Town"))
    access_type = models.CharField(max_length=30, choices=AccessType.choices, verbose_name=_("Access type"))
    property_type = models.CharField(max_length=10, choices=PropertyType.choices, verbose_name=_("Property type"))
    subtype = models.CharField(max_length=2, verbose_name=_("Subtype (T1/F1 etc.)"))
    num_rooms = models.PositiveIntegerField(default=1, verbose_name=_("Number of rooms"))

    exterior_showers_toilets = models.BooleanField(default=False, verbose_name=_("Exterior showers & toilets"))
    interior_showers_toilets = models.BooleanField(default=False, verbose_name=_("Interior showers & toilets"))
    garage = models.BooleanField(default=False, verbose_name=_("Garage"))
    garden = models.BooleanField(default=False, verbose_name=_("Garden"))

    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Rental Price"))

    def __str__(self):
        return f"{self.get_property_type_display()} {self.subtype} in {self.town.name}"

    class Meta:
        verbose_name = _("Rental Property")
        verbose_name_plural = _("Rental Properties")


class Land(models.Model):
    class PaperType(models.TextChoices):
        TITRE_FONCIER = 'titre_foncier', _('Titre foncier')
        ACTE_JURIDIQUE = 'acte_juridique', _('Acte juridique')
        PLAN_CADASTRE = 'plan_cadastre', _('Plan cadastré')

    class AccessType(models.TextChoices):
        NO_ACCESS = 'sans_acces', _('Sans accès')
        MOTO = 'acces_moto', _('Accès moto')
        CAR = 'acces_voiture', _('Accès voiture')
        CAR_PARKING = 'acces_voiture_parking', _('Accès voiture + parking')

    town = models.ForeignKey(Town, on_delete=models.CASCADE, verbose_name=_("Town"))
    paper_type = models.CharField(max_length=20, choices=PaperType.choices, verbose_name=_("Paper type"))
    access_type = models.CharField(max_length=30, choices=AccessType.choices, verbose_name=_("Access type"))
    is_fenced = models.BooleanField(default=False, verbose_name=_("Is fenced"))
    is_ready_to_build = models.BooleanField(default=False, verbose_name=_("Is ready to build"))

    # New fields as requested
    superficy = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Superficy (m²)"))
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Total Price"))

    def __str__(self):
        return f"Land in {self.town.name} ({self.superficy} m²)"

    class Meta:
        verbose_name = _("Land for Sale")
        verbose_name_plural = _("Lands for Sale")