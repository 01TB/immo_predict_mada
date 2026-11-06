# immo_predict_mada/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from predictor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')), # For language switching
]

# URLs that should be translated
urlpatterns += i18n_patterns(
    path('', views.HomePageView.as_view(), name='home'),
    path('predict-rental/', views.predict_rental_view, name='predict_rental'),
    path('predict-land/', views.predict_land_view, name='predict_land'),
    
    # API endpoint for the map
    path('api/towns/', views.towns_geojson, name='towns_geojson'),

    # Data management
    path('upload-csv/', views.upload_csv_view, name='upload_csv'),

    # Add other translated URLs here
    # prefix_default_language=False is useful to not have /fr/ in the default lang URL
)