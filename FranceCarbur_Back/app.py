from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import hashlib
import os
import requests
import folium
from folium.plugins import MarkerCluster  # Import du module pour le clustering

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

    # Ajout des stations de carburant à partir du fichier GeoJSON
    folium.GeoJson(
        geojson_path,
        name="Stations",
        popup=lambda feature: feature['properties'].get('nom', 'Station de carburant')  # Ajouter des popups si besoin
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
