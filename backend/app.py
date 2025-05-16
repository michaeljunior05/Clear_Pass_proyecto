# test
# backend/app.py
from flask import Flask, render_template, url_for, session, redirect
import os
from .routes.auth_routes import auth_bp
from flask_session import Session

app = Flask(__name__, static_folder=os.path.join('..', 'frontend', 'static'), template_folder=os.path.join('..', 'frontend', 'templates'))
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET']) #se agrego esto
def show_register_form():
    return render_template('register.html')


@app.route('/productos')
def productos():
    return render_template('productos.html')
if __name__ == '__main__':
    app.run(debug=True)

