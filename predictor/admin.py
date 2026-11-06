# predictor/admin.py

from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from .models import Town, Rental, Land


# Use ModelAdmin for Town as Leaflet is not strictly necessary here
# and can add dependencies. If you have Leaflet properly configured,
# you can switch back to admin.LeafletGeoAdmin.
@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('property_type', 'subtype', 'town', 'num_rooms', 'price')
    list_filter = ('property_type', 'town', 'access_type')
    search_fields = ('town__name',)
    fieldsets = (
        (None, {'fields': ('town', 'property_type', 'subtype', 'num_rooms', 'price')}),
        (_('Access'), {'fields': ('access_type',)}),
        (_('Conveniences'), {'fields': ('exterior_showers_toilets', 'interior_showers_toilets', 'garage', 'garden')}),
    )


# === [CORRECTION] UPDATING THE LAND ADMIN CLASS ===
@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    # Display the new fields and the calculated price per sqm
    list_display = ('town', 'superficy', 'price', 'get_price_per_sqm', 'paper_type')
    list_filter = ('town', 'paper_type', 'is_fenced')
    search_fields = ('town__name',)

    # Organize the fields for better editing in the admin detail view
    fieldsets = (
        (None, {'fields': ('town', 'paper_type', 'access_type')}),
        (_('Characteristics'), {'fields': ('is_fenced', 'is_ready_to_build')}),
        (_('Pricing and Area'), {'fields': ('superficy', 'price')}),
    )

    @admin.display(description=_('Price per m² (Ar)'))
    def get_price_per_sqm(self, obj):
        """
        Calculates the price per square meter on the fly for display.
        """
        if obj.superficy and obj.superficy > 0:
            return round(obj.price / obj.superficy, 2)
        return 0