# backend/controllers/auth_controller.py
import json
import os
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests
import google_auth_oauthlib.flow
from flask import session



#cambio.
DATABASE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'database', 'data.json')
GOOGLE_CLIENT_ID = '222270840199-pcntooj9dsvmsn79j11glth1fueaurij.apps.googleusercontent.com' # Asegúrate de que sea el mismo en frontend y backend # Asegúrate de que sea el mismo en frontend y backend

def get_users():
    try:
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('users', [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_user(user_data):
    users = get_users()
    users.append(user_data)
    try:
        with open(DATABASE_FILE, 'w') as f:
            json.dump({'users': users}, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False

def login_user(email, password):
    users = get_users()
    for user in users:
        if user.get('email') == email and user.get('password'):
            if bcrypt.checkpw(password.encode('utf-8'), user.get('password').encode('utf-8')):
                return user
    return None
def handle_google_callback(code):
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'path/to/your/client_secret.json', # ¡Reemplaza con la ruta correcta!
            scopes=['openid', 'email', 'profile']
        )
        flow.redirect_uri = 'http://127.0.0.1:5000/auth/google/callback'
        authorization_response = f'http://127.0.0.1:5000/auth/google/callback?code={code}'
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        request = requests.Request()
        id_info = id_token.verify_oauth2_token(credentials.id_token, request, GOOGLE_CLIENT_ID)

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        google_id = id_info['sub']
        email = id_info['email']
        name = id_info['name']

        users = get_users()
        user_exists = False
        for user in users:
            if user.get('google_id') == google_id:
                user_exists = True
                return {'id': user.get('id'), 'email': user.get('email'), 'name': user.get('name')}

        if not user_exists:
            new_user = {'id': len(users) + 1, 'google_id': google_id, 'email': email, 'name': name}
            if save_user(new_user):
                return {'id': new_user['id'], 'email': new_user['email'], 'name': new_user['name']}
            else:
                return None

        return None

    except Exception as e:
        print(f"Error handling Google callback: {e}")
        return None
    
def register_user(email, password):
    print("Función register_user llamada con email:", email, "y password:", password)
    users = get_users()
    print(f"Valor de 'users' después de get_users(): {users}")
    for user in users:
        print(f"Iterando sobre usuario: {user.get('email') if user else None}")
        if user and user.get('email') == email:
            print(f"Email '{email}' ya existe en la base de datos.")
            return None # El email ya está en uso

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = {'id': len(users) + 1, 'email': email, 'password': hashed_password}
    print(f"Usuario a guardar: {new_user}")
    if save_user(new_user):
        print("Usuario guardado exitosamente.")
        return new_user
    else:
        print("Error al guardar el usuario.")
        return None