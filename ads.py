from flask import Blueprint, jsonify, request, g, current_app
from models import Ad, AdPhoto, db
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

api_ads_bp = Blueprint('api_ads', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def serialize_ad(ad, full=False):
    data = {
        'id': ad.id,
        'title': ad.title,
        'price': ad.price,
        'price_unit': ad.price_unit,
        'city': ad.city,
        'created_date': ad.created_date.isoformat() if ad.created_date else None,
        'main_photo': ad.photos[0].image_filename if ad.photos else None
    }

    if full:
        data.update({
            'description': ad.description,
            'ad_type': ad.ad_type,
            'condition': ad.condition,
            'address': ad.address,
            'views': ad.views,
            'status': ad.status,
            'category': ad.category,
            'user_id': ad.user_id,
            'photos': [p.image_filename for p in ad.photos] 
        })
    
    return data

@api_ads_bp.route('/ads', methods=['GET'])
def get_ads():
    ads = Ad.query.filter_by(status='active').order_by(Ad.created_date.desc()).all()
    
    ads_list = [serialize_ad(ad, full=False) for ad in ads]
    return jsonify(ads_list)

@api_ads_bp.route('/ads/<int:id>', methods=['GET'])
def get_ad(id):
    ad = Ad.query.get(id)
    if ad is None:
        return jsonify({'error': 'Объявление не найдено'}), 404
    ad.views += 1
    db.session.commit()

    return jsonify(serialize_ad(ad, full=True))

@api_ads_bp.route('/ads', methods=['POST'])
def create_ad():
    if not request.is_json:
        return jsonify({'error': 'Content-Type должен быть application/json'}), 400

    data = request.get_json()
    
    required_fields = ['title', 'description', 'city']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно для заполнения'}), 400

    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
         return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        new_ad = Ad(
            title=data['title'].strip(),
            description=data['description'].strip(), 
            price=data.get('price'),
            price_unit=data.get('price_unit', 'rub'),
            ad_type=data.get('ad_type', 'item'),
            condition=data.get('condition'),
            city=data['city'].strip(),
            address=data.get('address'),
            category=data.get('category'),
            user_id=user_id,
            status='active'
        )
        
        db.session.add(new_ad)
        db.session.flush() 

        photos_data = data.get('photos', [])
        if isinstance(photos_data, list):
            for filename in photos_data:
                photo = AdPhoto(image_filename=filename, ad_id=new_ad.id)
                db.session.add(photo)

        db.session.commit()
        return jsonify({'id': new_ad.id, 'message': 'Объявление создано'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при сохранении', 'details': str(e)}), 500

@api_ads_bp.route('/ads/<int:id>', methods=['PUT'])
def edit_ad(id):
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
         return jsonify({'error': 'Необходима авторизация'}), 401

    ad = Ad.query.get(id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404

    if ad.user_id != user_id:
        return jsonify({'error': 'Нет прав на редактирование'}), 403

    if not request.is_json:
        return jsonify({'error': 'Content-Type должен быть application/json'}), 400

    data = request.get_json()

    try:
        if 'title' in data: ad.title = data['title'].strip()
        if 'description' in data: ad.description = data['description'].strip()
        if 'price' in data: ad.price = data['price']
        if 'price_unit' in data: ad.price_unit = data['price_unit']
        if 'condition' in data: ad.condition = data['condition']
        if 'city' in data: ad.city = data['city']
        if 'address' in data: ad.address = data['address']
        if 'category' in data: ad.category = data['category']
        if 'status' in data: ad.status = data['status']

        if 'photos' in data and isinstance(data['photos'], list):
            AdPhoto.query.filter_by(ad_id=ad.id).delete()
            for filename in data['photos']:
                photo = AdPhoto(image_filename=filename, ad_id=ad.id)
                db.session.add(photo)

        db.session.commit()
        return jsonify({'message': 'Объявление обновлено', 'id': ad.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении', 'details': str(e)}), 500

@api_ads_bp.route('/ads/<int:id>', methods=['DELETE'])
def delete_ad(id):
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
         return jsonify({'error': 'Необходима авторизация'}), 401

    ad = Ad.query.get(id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404

    if ad.user_id != user_id:
        return jsonify({'error': 'Нет прав на удаление'}), 403

    try:
        db.session.delete(ad)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при удалении', 'details': str(e)}), 500
    
@api_ads_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Нет файла'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        
        file.save(os.path.join(upload_path, unique_filename))
        
        return jsonify({'filename': unique_filename}), 201
    
    return jsonify({'error': 'Недопустимый формат файла'}), 400

