from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    get_jwt_identity, get_jwt, jwt_required, decode_token
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, TokenBlocklist, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
 
    name = data.get('name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({"success": False, "error": "Имя, email и пароль обязательны"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "Пользователь с таким email уже существует"}), 409
    hashed = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(
        name=name, 
        last_name=last_name,
        email=email, 
        hashed_password=hashed,
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "Регистрация успешна"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Ошибка базы данных: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Нет данных'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.hashed_password, password):
        return jsonify({'success': False, 'error': 'Неверный email или пароль'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'last_name': user.last_name,
            'email': user.email,
        }
    })

    response.set_cookie('access_token_cookie', value=access_token, httponly=True)
    response.set_cookie('refresh_token_cookie', value=refresh_token, httponly=True, path='/api/auth/refresh') 

    return response, 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    response = jsonify({"success": True})
    response.set_cookie('access_token_cookie', value=new_access_token, httponly=True)
    return response, 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))

    refresh_cookie = request.cookies.get('refresh_token_cookie')
    if refresh_cookie:
        try:
            decoded = decode_token(refresh_cookie)
            db.session.add(TokenBlocklist(jti=decoded['jti']))
        except Exception:
            pass

    db.session.commit()

    response = jsonify({"success": True, "message": "Выход выполнен"})
    response.set_cookie('access_token_cookie', '', expires=0, httponly=True)
    response.set_cookie('refresh_token_cookie', '', expires=0, httponly=True)
    return response, 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    }), 200
