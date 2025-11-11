from flask import Flask, request, jsonify
import os
import psycopg2 # Bibliothèque pour parler à PostgreSQL
import sys

app = Flask(__name__)

# Render injecte automatiquement l'URL de votre DB (celle que vous venez de copier)
# dans cette variable d'environnement. C'est magique.
DATABASE_URL = os.environ.get('DATABASE_URL')

def check_key_in_db(key_from_bot: str) -> bool:
    """Vérifie si la clé existe dans la base de données PostgreSQL."""
    
    if not DATABASE_URL:
        print("ERREUR FATALE: Variable d'environnement DATABASE_URL non trouvée.", file=sys.stderr)
        return False

    conn = None
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Exécute une requête SQL pour trouver la clé
        cursor.execute("SELECT 1 FROM licenses WHERE key = %s", (key_from_bot,))
        
        # fetchone() renvoie (1,) si la clé est trouvée, ou None
        result = cursor.fetchone()
        
        cursor.close()
        return result is not None # Renvoie True si la clé existe

    except Exception as e:
        print(f"Erreur de base de données: {e}", file=sys.stderr)
        return False
    finally:
        if conn:
            conn.close()

@app.route('/api/verify')
def verify_key_endpoint():
    """C'est l'URL publique que votre bot .exe va appeler."""
    
    key_from_bot = request.args.get('key')
    
    if not key_from_bot:
        return jsonify({"status": "error", "message": "Clé manquante"}), 400

    if check_key_in_db(key_from_bot):
        print(f"SUCCES: Clé {key_from_bot} validée.")
        return jsonify({"status": "valid"}), 200
    else:
        print(f"ECHEC: Clé {key_from_bot} refusée.")
        return jsonify({"status": "invalid", "message": "Clé inconnue ou expirée"}), 403

if __name__ == '__main__':
    # Cette partie est nécessaire pour que Gunicorn (serveur de Render) trouve l'application
    pass