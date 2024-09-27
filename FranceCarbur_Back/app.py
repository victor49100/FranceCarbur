from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import OperationalError
from flask import Flask, render_template
from dotenv import load_dotenv
import os

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


# fonction bdd

def fetch_user_by_id(user_id):
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        # Requête SQL pour récupérer les données de la table "user" en fonction de l'ID
        cur.execute('SELECT * FROM public."user" WHERE id_user = %s;', (user_id,))
        # Récupération de la ligne
        user = cur.fetchone()
        # Fermeture du curseur et de la connexion
        cur.close()
        conn.close()

        return user

    except OperationalError as e:
        return {'error': f'Erreur de connexion : {e}'}
    except Exception as e:
        return {'error': f'Une erreur s\'est produite : {e}'}


def update_newPassword_by_id(id, newPassword):
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        # Exécution de la requête de mise à jour
        cur.execute('UPDATE public."user" SET password = %s WHERE id_user = %s;', (newPassword, id))
        
        # Commit des modifications
        conn.commit()
        # Fermeture des curseurs et connexion
        cur.close()
        conn.close()
        return 0
    except OperationalError as e:
        return {'error': f'Erreur de connexion : {e}'}
    except Exception as e:
        return {'error': f'Une erreur s\'est produite : {e}'}


# ROUTES

# GET

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

    # Convertir le tuple en un dictionnaire (si nécessaire)
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


# POST


# PUT
@app.route('/api/user/updateMDP', methods=['GET', 'PUT'])
def update_password():
    args = request.args
    user_id = args.get('user_id')
    new_password = args.get('new_password')
    if request.method == 'PUT':
        update = update_newPassword_by_id(user_id, new_password)
        if isinstance(update, dict) and 'error' in update:
            return jsonify(update), 404
        return jsonify({'OK': 'Changement réussi'})
    return jsonify({'error': 'Méthode non autorisée'}), 405



if __name__ == '__main__':
    app.run(debug=True)
