from flask import Blueprint, jsonify, request, g
from models import Review, Ad, User, db
from sqlalchemy import and_

api_reviews_bp = Blueprint('api_reviews', __name__)

@api_reviews_bp.route('/reviews', methods=['POST'])
def create_review():
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
        return jsonify({'error': 'Нужна авторизация'}), 401

    data = request.get_json()
    ad_id = data.get('ad_id')
    rating = data.get('rating')
    text = data.get('text', '')

    if not ad_id or not rating:
        return jsonify({'error': 'Укажите объявление и оценку'}), 400

    ad = Ad.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404

    if ad.user_id == user_id:
        return jsonify({'error': 'Нельзя писать отзыв самому себе'}), 400

    existing_review = Review.query.filter_by(author_id=user_id, ad_id=ad_id).first()
    if existing_review:
        return jsonify({'error': 'Вы уже оставили отзыв по этому объявлению'}), 400

    try:
        new_review = Review(
            rating=int(rating),
            text=text,
            author_id=user_id,
            target_user_id=ad.user_id,
            ad_id=ad.id
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({'message': 'Отзыв опубликован'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_reviews_bp.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    reviews = Review.query.filter_by(target_user_id=user_id).order_by(Review.created_date.desc()).all()
    
    result = []
    for r in reviews:
        result.append({
            'id': r.id,
            'rating': r.rating,
            'text': r.text,
            'date': r.created_date.isoformat(),
            'author_name': r.author.name,
            'ad_title': r.ad_id
        })

    return jsonify({
        'user_name': target_user.name,
        'average_rating': target_user.average_rating,
        'reviews': result
    })