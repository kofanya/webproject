from flask import Blueprint, jsonify, request, g, current_app
from models import Ad, AdPhoto, db, User 
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

api_ads_bp = Blueprint('api_ads', __name__)

def delete_file_from_disk(filename):
    if not filename: return
    try:
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Ошибка удаления: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def serialize_ad(ad, full=False, current_user=None):
    data = {
        'id': ad.id,
        'title': ad.title,
        'price': ad.price,
        'price_unit': ad.price_unit,
        'district': ad.district,
        'created_date': ad.created_date.isoformat() if ad.created_date else None,
        'main_photo': ad.photos[0].image_filename if ad.photos else None,
        'is_favorite': False
    }

    if current_user:
        data['is_favorite'] = current_user.has_liked(ad)

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
    ad_type = request.args.get('ad_type')
    category = request.args.get('category')
    district = request.args.get('district')
    current_user = None
    user_id = getattr(g, 'current_user_id', None)
    if user_id:
        current_user = User.query.get(int(user_id))

    query = Ad.query.filter_by(status='active')
    if ad_type:
        query = query.filter_by(ad_type=ad_type)
    if category and category != 'all':
        query = query.filter_by(category=category)
    if district and district != 'all':
        query = query.filter_by(district=district)
    
    ads = query.order_by(Ad.created_date.desc()).all()
    ads_list = [serialize_ad(ad, full=False, current_user=current_user) for ad in ads]
    return jsonify(ads_list)

@api_ads_bp.route('/ads/<int:id>', methods=['GET'])
def get_ad(id):
    current_user = None
    user_id = getattr(g, 'current_user_id', None)
    if user_id:
        current_user = User.query.get(int(user_id))

    ad = Ad.query.get(id)
    if ad is None:
        return jsonify({'error': 'Объявление не найдено'}), 404
    ad.views += 1
    db.session.commit()

    return jsonify(serialize_ad(ad, full=True, current_user=current_user))

@api_ads_bp.route('/ads', methods=['POST'])
def create_ad():
    if not request.is_json:
        return jsonify({'error': 'Content-Type должен быть application/json'}), 400

    data = request.get_json()
    
    required_fields = ['title', 'description', 'district']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно для заполнения'}), 400

    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
         return jsonify({'error': 'Необходима авторизация'}), 401
    
    price = data.get('price')
    if price is not None:
        try:
            if float(price) < 0:
                return jsonify({'error': 'Цена не может быть отрицательной'}), 400
        except ValueError:
            return jsonify({'error': 'Цена должна быть числом'}), 400
        
    try:
        new_ad = Ad(
            title=data['title'].strip(),
            description=data['description'].strip(), 
            price=price,
            price_unit=data.get('price_unit', 'rub'),
            ad_type=data.get('ad_type', 'item'),
            condition=data.get('condition'),
            district=data['district'].strip(),
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
    
    user_id = int(user_id) 
    ad = Ad.query.get(id)
    if not ad: return jsonify({'error': 'Объявление не найдено'}), 404

    if ad.user_id != user_id: return jsonify({'error': 'Нет прав на редактирование'}), 403

    if not request.is_json: return jsonify({'error': 'Content-Type должен быть application/json'}), 400

    data = request.get_json()

    try:
        if 'title' in data: ad.title = data['title'].strip()
        if 'description' in data: ad.description = data['description'].strip()
        if 'price' in data: 
            price = data['price']
            if price is not None:
                try:
                    if float(price) < 0:
                        return jsonify({'error': 'Цена не может быть отрицательной'}), 400
                except ValueError:
                    return jsonify({'error': 'Цена должна быть числом'}), 400
            ad.price = price
        if 'price_unit' in data: ad.price_unit = data['price_unit']
        if 'condition' in data: ad.condition = data['condition']
        if 'district' in data: ad.district = data['district']
        if 'address' in data: ad.address = data['address']
        if 'category' in data: ad.category = data['category']
        if 'status' in data: ad.status = data['status']

        if 'photos' in data and isinstance(data['photos'], list):
            old_photos = AdPhoto.query.filter_by(ad_id=ad.id).all()
            for photo in old_photos:
                delete_file_from_disk(photo.image_filename)
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
    
    user_id = int(user_id)
    ad = Ad.query.get(id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404

    if ad.user_id != user_id:
        return jsonify({'error': 'Нет прав на удаление'}), 403

    try:
        for photo in ad.photos:
            delete_file_from_disk(photo.image_filename)
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

@api_ads_bp.route('/ads/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
        return jsonify({'error': 'Нужна авторизация'}), 401

    user = User.query.get(int(user_id))
    ad = Ad.query.get(id)

    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404

    is_favorite = False
    
    if user.has_liked(ad):
        user.unlike(ad) 
        is_favorite = False
    else:
        user.like(ad)  
        is_favorite = True

    db.session.commit()
    return jsonify({'is_favorite': is_favorite})

@api_ads_bp.route('/favorites', methods=['GET'])
def get_favorites():
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
        return jsonify({'error': 'Нужна авторизация'}), 401

    user = User.query.get(int(user_id))
    favorite_ads = user.saved_ads.all()
 
    ads_list = [serialize_ad(ad, full=False, current_user=user) for ad in favorite_ads]
    return jsonify(ads_list)