from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import hashlib
import os
import requests
import folium
from folium.plugins import MarkerCluster  # Import du module pour le clustering
import json


# Chargement des variables d'environnement à partir du fichier .env
load_dotenv()

app = Flask(__name__)

# Configuration de la base de données via les variables d'environnement
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': os.getenv('DB_SSLMODE')
}

# Fonction pour télécharger et mettre en cache le fichier GeoJSON
geojson_url = "https://www.data.gouv.fr/fr/datasets/r/c465b7f9-f2d7-4e32-a575-d9d69494d112"


def download_geojson():
    geojson_path = "static/data/geojson_cache.geojson"
    if not os.path.exists(geojson_path):
        response = requests.get(geojson_url)
        with open(geojson_path, 'wb') as f:
            f.write(response.content)
    return geojson_path


# Fonction pour afficher la carte avec clustering des stations de carburant
@app.route('/map')
def show_map():
    geojson_path = download_geojson()

    # Création de la carte centrée sur la France
    france_map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Création du cluster
    marker_cluster = MarkerCluster().add_to(france_map)

    # Lecture du fichier GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Boucle sur chaque station pour ajouter les marqueurs et les popups avec les prix
    for feature in data['features']:
        # Récupération des coordonnées
        coords = feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]

        # Récupération des informations de la station
        station_name = feature['properties'].get('nom', 'Station de carburant')

        # Extraction et traitement des prix (conversion JSON)
        prix_raw = feature['properties'].get('prix')  # Récupérer la clé 'prix'
        if prix_raw:  # Vérifier si prix_raw n'est ni None ni vide
            try:
                prix_list = json.loads(prix_raw)  # Conversion de la chaîne JSON en liste de dictionnaires
            except json.JSONDecodeError:
                prix_list = []  # En cas d'erreur de conversion, définir une liste vide
        else:
            prix_list = []  # Si 'prix' est None ou absent, définir une liste vide

        # Construction du contenu du popup avec les prix
        prix_info = ""
        if prix_list:
            for prix in prix_list:
                # Vérifiez que chaque élément est un dictionnaire avant d'utiliser `.get()`
                if isinstance(prix, dict):
                    nom_carburant = prix.get('@nom', 'Inconnu')
                    valeur = prix.get('@valeur', 'N/A')
                    prix_info += f"{nom_carburant}: {valeur} €/L<br>"
                else:
                    prix_info += "Donnée de prix incorrecte<br>"
        else:
            prix_info = "Prix non disponible"

        # Création du popup
        popup_content = f"<b>{station_name}</b><br>{prix_info}"

        # Ajout du marqueur au cluster
        folium.Marker(
            location=coords,
            popup=popup_content
        ).add_to(marker_cluster)

    # Sauvegarde de la carte dans un fichier HTML
    map_path = "templates/map.html"
    france_map.save(map_path)

    # Rendre la carte
    return render_template("map.html")




# Fonctions pour la gestion de la base de données

def fetch_user_by_id(user_id):
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        cur.execute('SELECT * FROM public."user" WHERE id_user = %s;', (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except OperationalError as e:
        return {'error': f'Erreur de connexion : {e}'}
    except Exception as e:
        return {'error': f'Une erreur s\'est produite : {e}'}


def update_newPassword_by_id(id, newPassword):
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        cur.execute('UPDATE public."user" SET password = %s WHERE id_user = %s;', (newPassword, id))
        conn.commit()
        cur.close()
        conn.close()
        return 0
    except OperationalError as e:
        return {'error': f'Erreur de connexion : {e}'}
    except Exception as e:
        return {'error': f'Une erreur s\'est produite : {e}'}


# ROUTES

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')


@app.route('/api/user', methods=['GET'])
def get_user():
    args = request.args
    user_id = args.get('user_id')
    user = fetch_user_by_id(user_id)

    if user is None:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    user_data = {
        'id_user': user[0],
        'first_name': user[1],
        'last_name': user[2],
        'pseudo': user[3],
        'car_type': user[4],
        'conso': user[5],
        'car_name': user[6],
        'password': user[7],
    }

    return jsonify(user_data)


@app.route('/api/user/updateMDP', methods=['GET', 'PUT'])
def update_password():
    args = request.args
    user_id = args.get('user_id')

    new_password = args.get('new_password')
    salt = 'sel'
    dataBase_password = new_password + salt
    hashed = hashlib.sha256(dataBase_password.encode())

    if request.method == 'PUT':
        update = update_newPassword_by_id(user_id, hashed.hexdigest())
        if isinstance(update, dict) and 'error' in update:
            return jsonify(update), 404
        return jsonify({'OK': 'Changement réussi'})
    return jsonify({'error': 'Méthode non autorisée'}), 405


if __name__ == '__main__':
    app.run(debug=True)
