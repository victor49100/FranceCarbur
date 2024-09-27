from flask import Flask, jsonify
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
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

@app.route('/app/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = fetch_user_by_id(user_id)
    
    if user is None:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Convertir le tuple en un dictionnaire (si nécessaire)
    user_data = {
        'id_user': user[0],
        'username': user[1],
        'email': user[2]
    }
    
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True)
