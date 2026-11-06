# predictor/views.py

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.serializers import serialize
from django.contrib import messages
from django.utils.translation import gettext as _
import joblib
import pandas as pd
import io

from .models import Town, Rental, Land
from .forms import RentalPredictionForm, LandPredictionForm, CSVUploadForm


class HomePageView(TemplateView):
    template_name = "home.html"


def predict_rental_view(request):
    prediction = None
    form = RentalPredictionForm(request.POST or None)

    if request.method == 'POST':  # Check for POST first
        if form.is_valid():  # Then check for validity
            try:
                # ... your existing prediction logic ...
                # Load the trained model and the list of columns
                model = joblib.load('ml_models/rental_model.joblib')
                model_columns = joblib.load('ml_models/rental_encoder.joblib')

                data = form.cleaned_data
                town_obj = Town.objects.get(pk=data['town'])

                input_df = pd.DataFrame([{
                    'town': town_obj.id,
                    'access_type': data['access_type'],
                    'property_type': data['property_type'],
                    'subtype': data['subtype'],
                    'num_rooms': data['num_rooms'],
                    'exterior_showers_toilets': data['exterior_showers_toilets'],
                    'interior_showers_toilets': data['interior_showers_toilets'],
                    'garage': data['garage'],
                    'garden': data['garden'],
                }])

                # One-hot encode the user's input
                categorical_cols = ['town', 'access_type', 'property_type', 'subtype']
                query = pd.get_dummies(input_df, columns=categorical_cols)

                # Align columns
                query = query.reindex(columns=model_columns, fill_value=0)

                # Make prediction
                predicted_price = model.predict(query)
                prediction = round(predicted_price[0], 2)

            except FileNotFoundError:
                messages.error(request, _("Prediction model not found. Please train the model first."))
            except Exception as e:
                messages.error(request, _("An error occurred during prediction: ") + str(e))

        else:
            # === [DEBUGGING STEP] PRINT THE ERRORS ===
            print("Form is NOT valid. Errors:")
            print(form.errors)
            # ========================================

    context = {
        'form': form,
        'prediction': prediction,
        'apartment_subtypes': Rental.ApartmentSubtype.choices,
        'house_subtypes': Rental.HouseSubtype.choices
    }
    return render(request, 'predict_rental.html', context)


def predict_land_view(request):
    prediction = None
    form = LandPredictionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            # Load the trained model and the list of columns
            model = joblib.load('ml_models/land_model.joblib')
            model_columns = joblib.load('ml_models/land_encoder.joblib')  # This now loads a list

            data = form.cleaned_data
            town_obj = Town.objects.get(pk=data['town'])

            input_df = pd.DataFrame([{
                'town': town_obj.id,
                'paper_type': data['paper_type'],
                'access_type': data['access_type'],
                'is_fenced': data['is_fenced'],
                'is_ready_to_build': data['is_ready_to_build'],
                'superficy': data['superficy'],
            }])

            categorical_cols = ['town', 'paper_type', 'access_type']
            input_encoded = pd.get_dummies(input_df, columns=categorical_cols)

            # === [CORRECTION] USE THE LOADED LIST TO REINDEX ===
            input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

            predicted_price = model.predict(input_encoded)
            prediction = round(predicted_price[0], 2)

        except FileNotFoundError:
            messages.error(request, _("Prediction model not found. Please train the model first."))
        except Exception as e:
            messages.error(request, _("An error occurred during prediction: ") + str(e))

    context = {
        'form': form,
        'prediction': prediction
    }
    return render(request, 'predict_land.html', context)


# --- Other views (unchanged) ---

def towns_geojson(request):
    towns = Town.objects.all()
    geojson = serialize('geojson', towns, geometry_field='location', fields=('pk', 'name'))
    return HttpResponse(geojson, content_type='application/json')


def upload_csv_view(request):
    if request.method == 'POST':
        model_type = request.POST.get('model_type')
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, _("This is not a CSV file."))
                return redirect('upload_csv')

            try:
                df = pd.read_csv(io.TextIOWrapper(csv_file.file, encoding='utf-8'))
                if model_type == 'towns':
                    import_towns(df)
                    messages.success(request, _("Towns imported successfully!"))
                elif model_type == 'rentals':
                    import_rentals(df)
                    messages.success(request, _("Rental data imported successfully!"))
                elif model_type == 'land':
                    import_land(df)
                    messages.success(request, _("Land data imported successfully!"))
                else:
                    messages.error(request, _("Invalid model type selected."))
            except Exception as e:
                messages.error(request, _("Error processing file: ") + str(e))

            return redirect('upload_csv')
    else:
        form = CSVUploadForm()
    return render(request, 'upload_csv.html', {'form': form})


def import_towns(df):
    from django.contrib.gis.geos import Point
    for index, row in df.iterrows():
        Town.objects.update_or_create(
            name=row['name'],
            defaults={'location': Point(float(row['longitude']), float(row['latitude']))}
        )


def import_rentals(df):
    for index, row in df.iterrows():
        town = Town.objects.get(name=row['town_name'])
        Rental.objects.create(
            town=town, access_type=row['access_type'], property_type=row['property_type'],
            subtype=row['subtype'], num_rooms=row['num_rooms'],
            exterior_showers_toilets=row['exterior_showers_toilets'],
            interior_showers_toilets=row['interior_showers_toilets'], garage=row['garage'],
            garden=row['garden'], price=row['price']
        )


def import_land(df):
    for index, row in df.iterrows():
        town = Town.objects.get(name=row['town_name'])
        Land.objects.create(
            town=town,
            paper_type=row['paper_type'],
            access_type=row['access_type'],
            is_fenced=row['is_fenced'],
            is_ready_to_build=row['is_ready_to_build'],
            # Use the new columns from the CSV
            superficy=row['superficy'],
            price=row['price']
        )