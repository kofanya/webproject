from flask import Flask, g 
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from datetime import timedelta
from models import db, TokenBlocklist, Ad, AdPhoto, User 

from auth import auth_bp
from ads import api_ads_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = 'my-secret-key-123456' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsweblab2.db'
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
        user_id = get_jwt_identity()
        if user_id:
            g.current_user_id = user_id
        else:
            g.current_user_id = None
    except Exception:
        g.current_user_id = None

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(api_ads_bp, url_prefix='/api') 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("База данных инициализирована.")
    app.run(debug=True)