from flask import Flask, g, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from datetime import timedelta
from models import db, TokenBlocklist, Ad, AdPhoto, User 
import os

from auth import auth_bp
from ads import api_ads_bp
from messages import api_messages_bp
from reviews import api_reviews_bp
from admin import admin_bp

app = Flask(__name__, static_folder='static_dist', static_url_path='/')
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'webproject.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SECRET_KEY'] = 'my-secret-key-123456' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = "secret-jwt-key-1234"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

app.config["JWT_TOKEN_LOCATION"] = ["cookies"] 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db.init_app(app)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_token(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

@app.before_request
def load_user_from_jwt():
    try:
        verify_jwt_in_request(optional=True)
        user_id = int(get_jwt_identity())
        if user_id:
            g.current_user_id = user_id
        else:
            g.current_user_id = None
    except Exception:
        g.current_user_id = None

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.get(int(identity))
    if user and user.is_admin:
        return {'is_administrator': True}
    return {'is_administrator': False}

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    uploads_folder = os.path.join(app.root_path, 'static', 'uploads')
    return send_from_directory(uploads_folder, filename)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(api_ads_bp, url_prefix='/api')
app.register_blueprint(api_messages_bp, url_prefix='/api') 
app.register_blueprint(api_reviews_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')