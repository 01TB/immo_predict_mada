# immo_predict_mada

Application web Django qui **prédit le budget nécessaire pour louer une maison ou un appartement, ou acheter un terrain à Madagascar**, à partir de modèles de régression entraînés avec scikit-learn. L'interface est disponible en **français** et en **malgache**, et la ville se choisit directement sur une carte interactive.

> Projet académique réalisé en Licence 2 Informatique à l'IT University (Antananarivo), dans le cadre du cours d'Analyse de données.

---

## Fonctionnalités

- **Prédiction d'un loyer** (maison ou appartement) selon la ville, le type d'accès, le type de bien (T1 à T6 pour un appartement, F1 à F6 pour une maison), le nombre de pièces et les équipements (douches et toilettes intérieures ou extérieures, garage, jardin).
- **Prédiction du prix d'un terrain**, exprimé en ariary par m², selon la ville, le type de papier (titre foncier, acte juridique, plan cadastré), le type d'accès, la superficie, la clôture et la constructibilité.
- **Carte interactive** (Leaflet + OpenStreetMap) : les villes sont servies en GeoJSON depuis PostGIS, et un clic sur une ville la sélectionne dans le formulaire.
- **Interface bilingue français / malgache** grâce au système d'internationalisation de Django (`i18n_patterns`, fichiers `.po` / `.mo`).
- **Import de données CSV** (villes, locations, terrains) depuis une page dédiée.
- **Back-office** via l'administration Django.

## Démarche de machine learning

L'entraînement se fait dans le script [`train_models.py`](train_models.py), qui lit directement les données en base via l'ORM Django.

| | Modèle « location » | Modèle « terrain » |
|---|---|---|
| **Cible** | Prix du loyer (Ar) | Prix au m² (Ar/m²), calculé comme `price / superficy` |
| **Variables catégorielles** | ville, type d'accès, type de bien, sous-type | ville, type de papier, type d'accès |
| **Autres variables** | nombre de pièces, 4 équipements (booléens) | superficie, clôturé, prêt à bâtir |
| **Algorithme** | Régression linéaire (`LinearRegression`) | Régression linéaire (`LinearRegression`) |

Étapes :

1. **Extraction** des données depuis PostgreSQL dans un `DataFrame` pandas.
2. **Nettoyage** : conversion numérique, exclusion des terrains de superficie nulle.
3. **Encodage one-hot** des variables catégorielles (`pd.get_dummies`). La liste des colonnes obtenue est sauvegardée pour réaligner les saisies des utilisateurs sur le même format (`reindex`).
4. **Découpage** en données d'entraînement et de test (80 / 20, `random_state=42`).
5. **Entraînement** puis **évaluation** avec la RMSE (racine de l'erreur quadratique moyenne) sur le jeu de test.
6. **Sauvegarde** du modèle et des colonnes avec `joblib` dans `ml_models/`. Ces fichiers sont ensuite chargés par les vues Django pour faire les prédictions.

Un modèle n'est entraîné que si la base contient au moins 10 enregistrements.

## Stack technique

- **Back-end** : Python 3.13, Django 5.1, GeoDjango
- **Base de données** : PostgreSQL 17 + PostGIS 3.4
- **Data / ML** : pandas, NumPy, scikit-learn, joblib
- **Front-end** : templates Django, Bootstrap 5, Leaflet
- **Internationalisation** : Django i18n (français / malgache)

## Structure du projet

```
immo_predict_mada/
├── immo_predict_mada/     # Configuration Django (settings, urls)
├── predictor/             # Application principale : modèles, formulaires, vues
├── templates/             # Pages : accueil, prédiction location, prédiction terrain, import CSV
├── static/                # CSS et Leaflet
├── locale/                # Traductions (fr, mg)
├── data_berthin/          # Jeux de données CSV : villes, locations, terrains
├── ml_models/             # Modèles entraînés (.joblib)
├── train_models.py        # Script d'entraînement des modèles
└── manage.py
```

## Installation et lancement

### Prérequis

- Python 3.13
- PostgreSQL avec l'extension PostGIS
- GDAL (requis par GeoDjango)

### 1. Installer les dépendances

```bash
pip install django pandas numpy scikit-learn joblib psycopg2-binary gdal django-crispy-forms crispy-bootstrap5
```

### 2. Configurer la base de données

Créer une base `immo_predict_mada` avec l'extension PostGIS :

```sql
CREATE DATABASE immo_predict_mada;
\c immo_predict_mada
CREATE EXTENSION postgis;
```

Adapter ensuite dans `immo_predict_mada/settings.py` :
- les identifiants de connexion dans `DATABASES` ;
- le chemin `GDAL_LIBRARY_PATH` vers la bibliothèque GDAL de votre machine.

### 3. Créer les tables

```bash
python manage.py migrate
python manage.py createsuperuser   # optionnel, pour l'administration
```

### 4. Importer les données

Lancer le serveur, ouvrir la page `http://127.0.0.1:8000/fr/upload-csv/`, puis importer les fichiers de `data_berthin/` **dans cet ordre** (les locations et les terrains sont rattachés à une ville existante) :

1. **Villes** : `towns.csv`
2. **Locations** : `formatted_donnees_maisons.csv`
3. **Terrains** : `land_data.csv`

### 5. Entraîner les modèles

Depuis la racine du projet :

```bash
python train_models.py
```

Le script affiche la RMSE de chaque modèle et enregistre les fichiers dans `ml_models/`.

### 6. Lancer l'application

```bash
python manage.py runserver
```

Puis ouvrir `http://127.0.0.1:8000/fr/` (ou `/mg/` pour la version malgache).

## Limites et pistes d'amélioration

- **Jeu de données réduit** (environ 120 locations et 120 terrains) : les prédictions donnent un ordre de grandeur, pas une estimation fiable.
- **Modèle volontairement simple** : comparer la régression linéaire avec des modèles non linéaires (forêt aléatoire, gradient boosting) et utiliser la validation croisée.
- **Évaluation plus complète** : ajouter le R² et la MAE en plus de la RMSE.
- **Pipeline unique** : regrouper l'encodage et le modèle dans un `Pipeline` scikit-learn, pour éviter de dupliquer le prétraitement entre l'entraînement et les vues.
- **Configuration** : sortir les identifiants de base de données et la `SECRET_KEY` du code (variables d'environnement), et ajouter un `requirements.txt`.

## Auteur

**Tsitohaina Berthin RAMANANKIRAHINA**
[GitHub](https://github.com/01TB) · [LinkedIn](https://www.linkedin.com/in/tsitohaina-berthin-ramanankirahina-042aa4252) · [Portfolio](https://portfolio-tsitohaina-berthin-ramana.vercel.app)
