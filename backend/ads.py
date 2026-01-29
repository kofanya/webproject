from flask import Blueprint, jsonify, request, g, current_app
from models import Ad, AdPhoto, db, User
from datetime import datetime
import os
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

api_ads_bp = Blueprint('api_ads', __name__)


def delete_file_from_disk(filename):
    if not filename: return
    try:
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Ошибка удаления файла: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_ads_bp.route('/ads', methods=['GET'])
def get_ads():
    ad_type = request.args.get('ad_type')
    category = request.args.get('category')
    district = request.args.get('district')
    
    current_user = None
    user_id = g.current_user_id
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
    response_list = []
    
    for ad in ads:
        main_photo = ad.photos[0].image_filename if ad.photos else None
        
        is_favorite = False
        if current_user:
            is_favorite = current_user.has_liked(ad)

        ad_data = {
            'id': ad.id,
            'title': ad.title,
            'price': ad.price,
            'price_unit': ad.price_unit,
            'district': ad.district,
            'created_date': ad.created_date.isoformat() if ad.created_date else None,
            'main_photo': main_photo,
            'is_favorite': is_favorite,
        }
        response_list.append(ad_data)

    return jsonify(response_list)

@api_ads_bp.route('/ads/<int:id>', methods=['GET'])
def get_ad(id):
    current_user = None
    user_id = g.current_user_id
    if user_id:
        current_user = User.query.get(int(user_id))

    ad = Ad.query.get(id)
    if ad is None:
        return jsonify({'error': 'Объявление не найдено'}), 404
    ad.views += 1
    db.session.commit()

    is_favorite = False
    if current_user:
        is_favorite = current_user.has_liked(ad)

    all_photos = [p.image_filename for p in ad.photos]
    main_photo = all_photos[0] if all_photos else None

    ad_data = {
        'id': ad.id,
        'title': ad.title,
        'price': ad.price,
        'price_unit': ad.price_unit,
        'district': ad.district,
        'created_date': ad.created_date.isoformat() if ad.created_date else None,
        'main_photo': main_photo,
        'is_favorite': is_favorite,
        'description': ad.description,
        'ad_type': ad.ad_type,
        'condition': ad.condition,
        'address': ad.address,
        'views': ad.views,
        'status': ad.status,
        'category': ad.category,
        'user_id': ad.user_id,
        'photos': all_photos
    }

    return jsonify(ad_data)

@api_ads_bp.route('/ads', methods=['POST'])
def create_ad():
    if not request.is_json:
        return jsonify({'error': 'Нужен JSON'}), 400

    data = request.get_json()

    if not data.get('title') or not data.get('description') or not data.get('district'):
        return jsonify({'error': 'Заполните обязательные поля'}), 400

    user_id = g.current_user_id
    if not user_id:
         return jsonify({'error': 'Нужна авторизация'}), 401

    price = data.get('price')
    try:
        if price is not None and float(price) < 0:
            return jsonify({'error': 'Цена не может быть меньше 0'}), 400
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
        return jsonify({'id': new_ad.id, 'message': 'Создано'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_ads_bp.route('/ads/<int:id>', methods=['PUT'])
def edit_ad(id):
    user_id = g.current_user_id
    if not user_id:
         return jsonify({'error': 'Нужна авторизация'}), 401
    
    ad = Ad.query.get(id)
    if not ad: return jsonify({'error': 'Не найдено'}), 404

    if ad.user_id != int(user_id): return jsonify({'error': 'Нет прав'}), 403

    data = request.get_json()

    try:
        if 'title' in data: ad.title = data['title']
        if 'description' in data: ad.description = data['description']
        if 'price' in data: ad.price = data['price']
        if 'price_unit' in data: ad.price_unit = data['price_unit']
        if 'condition' in data: ad.condition = data['condition']
        if 'district' in data: ad.district = data['district']
        if 'address' in data: ad.address = data['address']
        if 'category' in data: ad.category = data['category']
        if 'status' in data: ad.status = data['status']
        if 'photos' in data and isinstance(data['photos'], list):
            new_filenames = set(data['photos'])
            current_photos = AdPhoto.query.filter_by(ad_id=ad.id).all()

            for photo in current_photos:
                if photo.image_filename not in new_filenames:
                    delete_file_from_disk(photo.image_filename)
                    db.session.delete(photo)

            existing_filenames = {p.image_filename for p in current_photos}
            for filename in new_filenames:
                if filename not in existing_filenames:
                    db.session.add(AdPhoto(image_filename=filename, ad_id=ad.id))

        db.session.commit()
        return jsonify({'message': 'Обновлено', 'id': ad.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_ads_bp.route('/ads/<int:id>', methods=['DELETE'])
def delete_ad(id):
    user_id = g.current_user_id
    if not user_id:
         return jsonify({'error': 'Нужна авторизация'}), 401
    
    ad = Ad.query.get(id)
    if not ad: return jsonify({'error': 'Не найдено'}), 404

    if ad.user_id != int(user_id): return jsonify({'error': 'Нет прав'}), 403

    try:
        for photo in ad.photos:
            delete_file_from_disk(photo.image_filename)
        
        db.session.delete(ad)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@api_ads_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files: return jsonify({'error': 'Нет файла'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'Файл не выбран'}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        path = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(path, exist_ok=True)
        file.save(os.path.join(path, unique_filename))
        
        return jsonify({'filename': unique_filename}), 201
    
    return jsonify({'error': 'Неверный формат'}), 400

@api_ads_bp.route('/ads/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    user_id = g.current_user_id
    if not user_id: return jsonify({'error': 'Нужна авторизация'}), 401

    user = User.query.get(int(user_id))
    ad = Ad.query.get(id)

    if not ad: return jsonify({'error': 'Не найдено'}), 404

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
    user_id = g.current_user_id
    if not user_id: return jsonify({'error': 'Нужна авторизация'}), 401

    user = User.query.get(int(user_id))
    favorite_ads = user.saved_ads.all()
    response_list = []
    for ad in favorite_ads:
        main_photo = ad.photos[0].image_filename if ad.photos else None
        is_favorite = True 

        ad_data = {
            'id': ad.id,
            'title': ad.title,
            'price': ad.price,
            'price_unit': ad.price_unit,
            'district': ad.district,
            'created_date': ad.created_date.isoformat() if ad.created_date else None,
            'main_photo': main_photo,
            'is_favorite': is_favorite
        }
        response_list.append(ad_data)

    return jsonify(response_list)