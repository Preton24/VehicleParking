import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request
from models import db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' 

from models.user import User
from models.lot import ParkingLot
from models.slot import ParkingSlot
from models.reservation import Reservation

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Blueprints Registration ---
from controllers.auth_controller import auth_bp
from controllers.main_controller import main_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp, url_prefix='/')

@app.context_processor
def inject_globals():
    return dict(current_user=current_user, now=datetime.utcnow)

# --- Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Admin user
        if not User.query.filter_by(role='admin').first():
            admin_user = User(
                name='Admin',
                email='admin@example.com',
                password=generate_password_hash('adminpassword', method='pbkdf2:sha256'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin@example.com / adminpassword")

    app.run(debug=True)