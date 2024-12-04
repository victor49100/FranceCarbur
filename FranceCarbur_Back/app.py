from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import hashlib
import os
import requests
import folium
from folium.plugins import MarkerCluster
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


# Fonction pour télécharger et mettre en cache le fichier GeoJSON
def download_geojson():
    geojson_path = "static/data/geojson_cache.geojson"
    if not os.path.exists(geojson_path):
        response = requests.get(geojson_url)
        with open(geojson_path, 'wb') as f:
            f.write(response.content)
    return geojson_path


@app.route('/geojson-data', methods=['GET'])
def get_geojson_data():
    geojson_path = download_geojson()
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)



@app.route('/map', methods=['GET', 'POST'])
def show_map():
    geojson_path = download_geojson()
    map_path = "static/generated_map.html"

    # Liste des carburants disponibles
    all_fuels = ['SP95', 'SP98', 'Gazole', 'E10', 'GPL', 'E85']

    # Récupération des carburants sélectionnés
    selected_fuels = request.form.getlist('fuel_types') if request.method == 'POST' else all_fuels

    # Création de la carte
    france_map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(france_map)

    # Lecture des données GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Boucle sur les données pour ajouter les marqueurs
    for feature in data['features']:
        coords = feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]
        station_name = feature['properties'].get('nom', 'Station de carburant')

        prix_raw = feature['properties'].get('prix')
        if prix_raw:
            try:
                prix_list = json.loads(prix_raw)
            except json.JSONDecodeError:
                prix_list = []
        else:
            prix_list = []

        prix_info = '<ul style="list-style-type:none; padding: 0;">'
        display_station = False

        for prix in prix_list:
            if isinstance(prix, dict):
                nom_carburant = prix.get('@nom', 'Inconnu')
                valeur = prix.get('@valeur', None)

                # Affiche uniquement les carburants sélectionnés
                if nom_carburant in selected_fuels:
                    display_station = True
                    if valeur:
                        prix_info += f'<li style="padding: 5px; color: green; font-weight: bold;">{nom_carburant}: {valeur} €/L</li>'
                    else:
                        prix_info += f'<li style="padding: 5px; color: gray; text-decoration: line-through;">{nom_carburant}: Indisponible</li>'
        prix_info += '</ul>'

        if display_station:
            popup_content = f"""
                <div class="popup-content">
                    <b>{station_name}</b>
                    {prix_info}
                    <button class="btn btn-primary btn-sm mt-2" onclick="getDirections({coords[0]}, {coords[1]})">
                        Itinéraire
                    </button>
                </div>
            """
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_content, max_width=300, min_width=250)
            ).add_to(marker_cluster)

    # Sauvegarde de la carte
    france_map.save(map_path)

    return render_template('map.html', map_file=map_path, fuels=all_fuels, selected_fuels=selected_fuels)






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
